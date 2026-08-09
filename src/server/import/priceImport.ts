import JSZip from "jszip";
import { XMLParser } from "fast-xml-parser";
import type { Part } from "@/src/data/catalog";
import type { PriceImportRow } from "@/src/server/db/catalog";

type RawTable = string[][];

const parser = new XMLParser({
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
  textNodeName: "#text"
});

const columnAliases: Record<string, keyof PriceImportRow> = {
  "название": "name",
  "наименование": "name",
  "товар": "name",
  "name": "name",
  "артикул": "article",
  "article": "article",
  "sku": "article",
  "oem": "oem",
  "номер": "oem",
  "номер детали": "oem",
  "марка": "brand",
  "brand": "brand",
  "модель": "model",
  "model": "model",
  "категория": "category",
  "category": "category",
  "производитель": "manufacturer",
  "manufacturer": "manufacturer",
  "бренд детали": "manufacturer",
  "цена": "price",
  "price": "price",
  "стоимость": "price",
  "наличие": "availability",
  "availability": "availability",
  "склад": "stock",
  "stock": "stock",
  "срок": "delivery",
  "delivery": "delivery",
  "срок поставки": "delivery"
};

const availabilityValues: Part["availability"][] = ["в наличии", "1-3 дня", "под заказ", "уточнить"];

const normalizeHeader = (value: string) => value.trim().toLocaleLowerCase("ru-RU").replace(/\s+/g, " ");

const parsePrice = (value: string) => {
  const normalized = value.replace(/[^\d,.]/g, "").replace(",", ".");
  const price = Number(normalized);

  return Number.isFinite(price) ? Math.round(price) : undefined;
};

const parseCsvLine = (line: string) => {
  const cells: string[] = [];
  let current = "";
  let insideQuotes = false;

  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    const next = line[index + 1];

    if (char === '"' && next === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      insideQuotes = !insideQuotes;
    } else if ((char === "," || char === ";") && !insideQuotes) {
      cells.push(current.trim());
      current = "";
    } else {
      current += char;
    }
  }

  cells.push(current.trim());
  return cells;
};

const parseCsv = (content: string): RawTable =>
  content
    .replace(/^\uFEFF/, "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map(parseCsvLine);

const decodeCsvContent = (buffer: ArrayBuffer) => {
  const bytes = new Uint8Array(buffer);

  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    return new TextDecoder("windows-1251", { fatal: true }).decode(bytes);
  }
};

const asArray = <T>(value: T | T[] | undefined): T[] => {
  if (!value) {
    return [];
  }

  return Array.isArray(value) ? value : [value];
};

const readSharedStrings = async (zip: JSZip) => {
  const sharedStringsFile = zip.file("xl/sharedStrings.xml");

  if (!sharedStringsFile) {
    return [];
  }

  const xml = parser.parse(await sharedStringsFile.async("text")) as {
    sst?: {
      si?: Array<{ t?: string | { "#text"?: string }; r?: Array<{ t?: string | { "#text"?: string } }> }>;
    };
  };

  return asArray(xml.sst?.si).map((item) => {
    if (typeof item.t === "string") {
      return item.t;
    }

    if (item.t && typeof item.t === "object") {
      return item.t["#text"] ?? "";
    }

    return asArray(item.r)
      .map((run) => (typeof run.t === "string" ? run.t : run.t?.["#text"] ?? ""))
      .join("");
  });
};

const columnIndexFromRef = (ref: string) => {
  const letters = ref.replace(/\d+/g, "");
  let index = 0;

  for (const letter of letters) {
    index = index * 26 + letter.toUpperCase().charCodeAt(0) - 64;
  }

  return Math.max(index - 1, 0);
};

const readCellValue = (cell: Record<string, unknown>, sharedStrings: string[]) => {
  const type = String(cell["@_t"] ?? "");
  const rawValue = cell.v;

  if (type === "s") {
    return sharedStrings[Number(rawValue)] ?? "";
  }

  if (type === "inlineStr") {
    const inline = cell.is as { t?: string | { "#text"?: string } } | undefined;
    return typeof inline?.t === "string" ? inline.t : inline?.t?.["#text"] ?? "";
  }

  return rawValue === undefined || rawValue === null ? "" : String(rawValue);
};

const parseXlsx = async (buffer: ArrayBuffer): Promise<RawTable> => {
  const zip = await JSZip.loadAsync(buffer);
  const sharedStrings = await readSharedStrings(zip);
  const sheetFile = zip.file("xl/worksheets/sheet1.xml");

  if (!sheetFile) {
    return [];
  }

  const xml = parser.parse(await sheetFile.async("text")) as {
    worksheet?: {
      sheetData?: {
        row?: Array<{ c?: Array<Record<string, unknown>> | Record<string, unknown> }>;
      };
    };
  };

  return asArray(xml.worksheet?.sheetData?.row).map((row) => {
    const cells = asArray(row.c);
    const values: string[] = [];

    cells.forEach((cell) => {
      const ref = String(cell["@_r"] ?? "");
      values[columnIndexFromRef(ref)] = readCellValue(cell, sharedStrings);
    });

    return values.map((value) => value ?? "");
  });
};

const mapRawTable = (table: RawTable): PriceImportRow[] => {
  const [headers = [], ...rows] = table;
  const mappedHeaders = headers.map((header) => columnAliases[normalizeHeader(header)]);

  return rows
    .map((row) => {
      const item: Partial<PriceImportRow> = {};

      row.forEach((value, index) => {
        const key = mappedHeaders[index];

        if (!key || !value.trim()) {
          return;
        }

        if (key === "price") {
          item.price = parsePrice(value);
        } else if (key === "availability") {
          const availability = value.trim().toLocaleLowerCase("ru-RU") as Part["availability"];
          item.availability = availabilityValues.includes(availability) ? availability : "уточнить";
        } else {
          item[key] = value.trim() as never;
        }
      });

      return item;
    })
    .filter((row): row is PriceImportRow => Boolean(row.name?.trim() && row.article?.trim()));
};

export const parsePriceImportFile = async (file: File) => {
  const filename = file.name;
  const extension = filename.split(".").pop()?.toLowerCase() ?? "";
  const buffer = await file.arrayBuffer();
  const table =
    extension === "xlsx"
      ? await parseXlsx(buffer)
      : parseCsv(decodeCsvContent(buffer));

  return {
    filename,
    fileKind: extension || "csv",
    rows: mapRawTable(table)
  };
};
