export type CarModel = {
  name: string;
  years: string;
  generations: string[];
};

export type Brand = {
  name: string;
  models: CarModel[];
};

export type Category = {
  name: string;
  description: string;
};

export type Part = {
  id: string;
  name: string;
  oem: string;
  article: string;
  manufacturer: string;
  category: string;
  compatibility: string[];
  price: number;
  availability: "в наличии" | "1-3 дня" | "под заказ" | "уточнить";
  delivery: string;
  analogs: string[];
  quality: "оригинал" | "заводской аналог";
};

export const brands: Brand[] = [
  {
    name: "Audi",
    models: [
      { name: "A4", years: "2015-2024", generations: ["B9", "B9 рестайлинг"] },
      { name: "Q5", years: "2017-2025", generations: ["FY", "FY рестайлинг"] }
    ]
  },
  {
    name: "BMW",
    models: [
      { name: "3 Series", years: "2018-2026", generations: ["G20", "G21"] },
      { name: "X5", years: "2018-2026", generations: ["G05"] }
    ]
  },
  {
    name: "Toyota",
    models: [
      { name: "Camry", years: "2017-2025", generations: ["XV70"] },
      { name: "RAV4", years: "2018-2025", generations: ["XA50"] }
    ]
  },
  {
    name: "Volkswagen",
    models: [
      { name: "Tiguan", years: "2016-2024", generations: ["AD/BW"] },
      { name: "Passat", years: "2014-2024", generations: ["B8"] }
    ]
  }
];

export const categories: Category[] = [
  { name: "Тормозная система", description: "Диски, колодки, датчики износа и крепеж." },
  { name: "Фильтры и сервис", description: "Масляные, воздушные, салонные и топливные фильтры." },
  { name: "Подвеска", description: "Рычаги, сайлентблоки, ступицы и амортизаторы." },
  { name: "Электрика", description: "Датчики, модули, свечи и элементы управления." },
  { name: "Двигатель", description: "Ремни, ролики, прокладки и навесное оборудование." }
];

export const parts: Part[] = [
  {
    id: "brake-disc-audi-b9",
    name: "Тормозной диск передний",
    oem: "8W0615301T",
    article: "BD-8301T",
    manufacturer: "ATE",
    category: "Тормозная система",
    compatibility: ["Audi A4 B9", "Audi A5 F5"],
    price: 9840,
    availability: "1-3 дня",
    delivery: "Склад поставщика, проверка применимости менеджером",
    analogs: ["8W0615301AA", "BD-8301X"],
    quality: "заводской аналог"
  },
  {
    id: "oil-filter-bmw-g20",
    name: "Фильтр масляный",
    oem: "11428583898",
    article: "OF-583898",
    manufacturer: "Mann",
    category: "Фильтры и сервис",
    compatibility: ["BMW 3 Series G20", "BMW X3 G01"],
    price: 1820,
    availability: "в наличии",
    delivery: "Можно зарезервировать сегодня",
    analogs: ["HU 6014 z", "11428575211"],
    quality: "заводской аналог"
  },
  {
    id: "sensor-toyota-xv70",
    name: "Датчик кислорода",
    oem: "8946733050",
    article: "OS-33050",
    manufacturer: "Denso",
    category: "Электрика",
    compatibility: ["Toyota Camry XV70", "Toyota RAV4 XA50"],
    price: 12600,
    availability: "под заказ",
    delivery: "Ориентир 5-10 дней после подтверждения",
    analogs: ["89467-33050", "DOX-0279"],
    quality: "оригинал"
  },
  {
    id: "belt-vw-b8",
    name: "Комплект ремня ГРМ",
    oem: "04L198119E",
    article: "TBK-98119E",
    manufacturer: "Continental",
    category: "Двигатель",
    compatibility: ["Volkswagen Passat B8", "Volkswagen Tiguan AD"],
    price: 21800,
    availability: "уточнить",
    delivery: "Цена и срок зависят от поставщика",
    analogs: ["CT1168K1", "04L198119A"],
    quality: "заводской аналог"
  }
];

export const formatPrice = (value: number) =>
  new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0
  }).format(value);
