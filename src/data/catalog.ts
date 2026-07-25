export type CarModel = {
  name: string;
  slug: string;
  years: string;
  generations: string[];
};

export type Brand = {
  name: string;
  slug: string;
  country: string;
  models: CarModel[];
};

export type Category = {
  name: string;
  slug: string;
  description: string;
};

export type PartCondition = "новая" | "контрактная" | "восстановленная";

export type Part = {
  id: string;
  slug: string;
  name: string;
  oem: string;
  article: string;
  manufacturer: string;
  category: string;
  categorySlug: string;
  brand: string;
  brandSlug: string;
  model: string;
  compatibility: string[];
  price: number;
  availability: "в наличии" | "1-3 дня" | "под заказ" | "уточнить";
  delivery: string;
  analogs: string[];
  condition: PartCondition;
  quality: "оригинал" | "заводской аналог" | "проверенная контрактная";
  stock: string;
  description: string;
  specs: Record<string, string>;
};

export const brands: Brand[] = [
  {
    name: "Skoda",
    slug: "skoda",
    country: "Чехия",
    models: [
      { name: "Octavia", slug: "octavia", years: "2004-2026", generations: ["A5", "A7", "A8"] },
      { name: "Kodiaq", slug: "kodiaq", years: "2016-2026", generations: ["NS", "PS"] },
      { name: "Rapid", slug: "rapid", years: "2013-2024", generations: ["NH", "рестайлинг"] }
    ]
  },
  {
    name: "Volkswagen",
    slug: "volkswagen",
    country: "Германия",
    models: [
      { name: "Tiguan", slug: "tiguan", years: "2016-2026", generations: ["AD", "BW"] },
      { name: "Polo", slug: "polo", years: "2011-2026", generations: ["Sedan", "Liftback"] },
      { name: "Passat", slug: "passat", years: "2014-2024", generations: ["B8"] }
    ]
  },
  {
    name: "Audi",
    slug: "audi",
    country: "Германия",
    models: [
      { name: "A4", slug: "a4", years: "2015-2025", generations: ["B9", "B9 рестайлинг"] },
      { name: "Q5", slug: "q5", years: "2017-2026", generations: ["FY"] }
    ]
  },
  {
    name: "Toyota",
    slug: "toyota",
    country: "Япония",
    models: [
      { name: "Camry", slug: "camry", years: "2017-2026", generations: ["XV70", "XV80"] },
      { name: "RAV4", slug: "rav4", years: "2018-2026", generations: ["XA50"] }
    ]
  },
  {
    name: "Hyundai",
    slug: "hyundai",
    country: "Корея",
    models: [
      { name: "Solaris", slug: "solaris", years: "2017-2026", generations: ["HC", "рестайлинг"] },
      { name: "Creta", slug: "creta", years: "2016-2026", generations: ["GS", "SU2"] }
    ]
  },
  {
    name: "Kia",
    slug: "kia",
    country: "Корея",
    models: [
      { name: "Rio", slug: "rio", years: "2017-2026", generations: ["FB", "рестайлинг"] },
      { name: "Sportage", slug: "sportage", years: "2016-2026", generations: ["QL", "NQ5"] }
    ]
  },
  {
    name: "BMW",
    slug: "bmw",
    country: "Германия",
    models: [
      { name: "3 Series", slug: "3-series", years: "2018-2026", generations: ["G20", "G21"] },
      { name: "X5", slug: "x5", years: "2018-2026", generations: ["G05"] }
    ]
  },
  {
    name: "Mercedes-Benz",
    slug: "mercedes-benz",
    country: "Германия",
    models: [
      { name: "E-Class", slug: "e-class", years: "2016-2026", generations: ["W213", "W214"] },
      { name: "GLC", slug: "glc", years: "2015-2026", generations: ["X253", "X254"] }
    ]
  },
  {
    name: "Renault",
    slug: "renault",
    country: "Франция",
    models: [
      { name: "Logan", slug: "logan", years: "2014-2026", generations: ["L52", "L52 рестайлинг"] },
      { name: "Duster", slug: "duster", years: "2015-2026", generations: ["HS", "HM"] }
    ]
  },
  {
    name: "Lada",
    slug: "lada",
    country: "Россия",
    models: [
      { name: "Vesta", slug: "vesta", years: "2015-2026", generations: ["2180", "NG"] },
      { name: "Granta", slug: "granta", years: "2011-2026", generations: ["2190", "FL"] }
    ]
  }
];

export const categories: Category[] = [
  { name: "Кузов и оптика", slug: "body-lighting", description: "Фары, фонари, зеркала, решетки, бамперы и наружные элементы." },
  { name: "Двигатель", slug: "engine", description: "Навесное оборудование, датчики, насосы, прокладки и узлы двигателя." },
  { name: "Трансмиссия", slug: "transmission", description: "КПП, приводы, ШРУСы, сцепление и связанные узлы." },
  { name: "Подвеска и рулевое", slug: "suspension-steering", description: "Рычаги, амортизаторы, ступицы, рейки и наконечники." },
  { name: "Тормозная система", slug: "brakes", description: "Диски, колодки, суппорты, датчики износа и крепеж." },
  { name: "Фильтры и ТО", slug: "service", description: "Расходники для регулярного обслуживания и подготовки к сезону." },
  { name: "Электрика", slug: "electric", description: "Блоки управления, проводка, генераторы, стартеры и датчики." },
  { name: "Салон и безопасность", slug: "interior-safety", description: "Рули, подушки, панели, ремни, крепеж и элементы салона." }
];

export const parts: Part[] = [
  {
    id: "octavia-led-headlamp-left",
    slug: "octavia-led-headlamp-left",
    name: "Фара светодиодная левая",
    oem: "5E1 941 015 ZM",
    article: "ZP-LGT-5015L",
    manufacturer: "Zemazap Select",
    category: "Кузов и оптика",
    categorySlug: "body-lighting",
    brand: "Skoda",
    brandSlug: "skoda",
    model: "Octavia",
    compatibility: ["Skoda Octavia A7", "Skoda Octavia A7 рестайлинг"],
    price: 34700,
    availability: "уточнить",
    delivery: "Подтверждение склада и состояния перед резервом",
    analogs: ["5E1941017", "ZP-LGT-5017"],
    condition: "контрактная",
    quality: "проверенная контрактная",
    stock: "1 шт. на проверке",
    description: "Рабочая позиция для витрины: оптика проходит внешний осмотр, проверку креплений и маркировки.",
    specs: {
      Сторона: "левая",
      Тип: "LED",
      Состояние: "контрактная, без скрытых крепежных дефектов в карточке MVP",
      Проверка: "маркировка, корпус, разъемы"
    }
  },
  {
    id: "tiguan-steering-rack",
    slug: "tiguan-steering-rack",
    name: "Рулевая рейка электрическая",
    oem: "5Q1 423 055 ZM",
    article: "ZP-STR-3055",
    manufacturer: "Zemazap Select",
    category: "Подвеска и рулевое",
    categorySlug: "suspension-steering",
    brand: "Volkswagen",
    brandSlug: "volkswagen",
    model: "Tiguan",
    compatibility: ["Volkswagen Tiguan AD", "Volkswagen Tiguan BW"],
    price: 58800,
    availability: "под заказ",
    delivery: "Ориентир 3-7 дней после подтверждения поставщика",
    analogs: ["5Q1423051", "ZP-STR-3051"],
    condition: "восстановленная",
    quality: "проверенная контрактная",
    stock: "поставщик",
    description: "Узел для сценария заказа с обязательным подтверждением по модели, году и типу усилителя.",
    specs: {
      Усилитель: "электрический",
      Комплектность: "рейка без тяг",
      Проверка: "люфт, корпус, разъем",
      Гарантия: "после согласования поставщика"
    }
  },
  {
    id: "camry-front-brake-kit",
    slug: "camry-front-brake-kit",
    name: "Комплект передних тормозных дисков",
    oem: "43512-33ZP0",
    article: "ZP-BRK-33P0",
    manufacturer: "Nisshinbo",
    category: "Тормозная система",
    categorySlug: "brakes",
    brand: "Toyota",
    brandSlug: "toyota",
    model: "Camry",
    compatibility: ["Toyota Camry XV70", "Toyota Camry XV80"],
    price: 16400,
    availability: "1-3 дня",
    delivery: "Склад поставщика, резерв после звонка менеджера",
    analogs: ["43512-33140", "ZP-BRK-3140"],
    condition: "новая",
    quality: "заводской аналог",
    stock: "2 комплекта",
    description: "Новая расходная позиция для быстрого заказа по артикулу или модели автомобиля.",
    specs: {
      Ось: "передняя",
      Количество: "2 диска",
      Тип: "вентилируемый",
      Упаковка: "парная"
    }
  },
  {
    id: "kia-sportage-timing-kit",
    slug: "kia-sportage-timing-kit",
    name: "Комплект цепи ГРМ",
    oem: "24321-2GZP0",
    article: "ZP-ENG-2GZP",
    manufacturer: "INA",
    category: "Двигатель",
    categorySlug: "engine",
    brand: "Kia",
    brandSlug: "kia",
    model: "Sportage",
    compatibility: ["Kia Sportage QL", "Kia Sportage NQ5", "Hyundai Tucson NX4"],
    price: 28600,
    availability: "уточнить",
    delivery: "Цена зависит от комплектации набора",
    analogs: ["24321-2G500", "ZP-ENG-2G50"],
    condition: "новая",
    quality: "заводской аналог",
    stock: "подбор поставщика",
    description: "Пример товара, где менеджер уточняет двигатель и состав комплекта перед продажей.",
    specs: {
      Узел: "ГРМ",
      Двигатель: "2.0/2.4 бензин, уточнить",
      Комплект: "цепь, башмаки, натяжитель",
      Проверка: "по артикулу и мотору"
    }
  },
  {
    id: "solaris-oil-filter",
    slug: "solaris-oil-filter",
    name: "Фильтр масляный",
    oem: "26300-35ZP0",
    article: "ZP-SRV-3500",
    manufacturer: "Mann",
    category: "Фильтры и ТО",
    categorySlug: "service",
    brand: "Hyundai",
    brandSlug: "hyundai",
    model: "Solaris",
    compatibility: ["Hyundai Solaris HC", "Kia Rio FB"],
    price: 760,
    availability: "в наличии",
    delivery: "Можно добавить в корзину-заявку сразу",
    analogs: ["W 811/80", "26300-35505"],
    condition: "новая",
    quality: "заводской аналог",
    stock: "12 шт.",
    description: "Расходник для быстрого заказа без сложной применимости.",
    specs: {
      Тип: "масляный",
      Установка: "двигатель",
      Состояние: "новый",
      Бренд: "аналог заводского качества"
    }
  },
  {
    id: "audi-q5-engine-control",
    slug: "audi-q5-engine-control",
    name: "Блок управления двигателем",
    oem: "8R0 907 115 ZM",
    article: "ZP-ELC-7115",
    manufacturer: "Bosch",
    category: "Электрика",
    categorySlug: "electric",
    brand: "Audi",
    brandSlug: "audi",
    model: "Q5",
    compatibility: ["Audi Q5 8R", "Audi Q5 FY"],
    price: 42800,
    availability: "под заказ",
    delivery: "Проверка номера блока и совместимости перед оплатой",
    analogs: ["8R0907115", "ZP-ELC-7115B"],
    condition: "контрактная",
    quality: "проверенная контрактная",
    stock: "по запросу",
    description: "Карточка показывает сценарий сложного электронного узла с ручной сверкой номера и комплектации.",
    specs: {
      Тип: "ECU",
      Программирование: "требуется проверка",
      Разъемы: "по фото и маркировке",
      Возврат: "после согласования условий"
    }
  },
  {
    id: "bmw-g20-front-drive",
    slug: "bmw-g20-front-drive",
    name: "Привод передний правый",
    oem: "31 60 8 ZP 120",
    article: "ZP-TRN-8120R",
    manufacturer: "GKN",
    category: "Трансмиссия",
    categorySlug: "transmission",
    brand: "BMW",
    brandSlug: "bmw",
    model: "3 Series",
    compatibility: ["BMW 3 Series G20 xDrive", "BMW 3 Series G21 xDrive"],
    price: 39200,
    availability: "1-3 дня",
    delivery: "Подтверждение по модификации и приводу",
    analogs: ["31608605412", "ZP-TRN-05412"],
    condition: "контрактная",
    quality: "проверенная контрактная",
    stock: "1 шт.",
    description: "Позиция для раздела трансмиссии с акцентом на проверку модификации.",
    specs: {
      Сторона: "правая",
      Привод: "полный",
      Комплектность: "вал в сборе",
      Проверка: "пыльники, люфт, шлицы"
    }
  },
  {
    id: "glc-ac-compressor",
    slug: "glc-ac-compressor",
    name: "Компрессор кондиционера",
    oem: "A 000 830 ZP40",
    article: "ZP-ENG-8340",
    manufacturer: "Denso",
    category: "Двигатель",
    categorySlug: "engine",
    brand: "Mercedes-Benz",
    brandSlug: "mercedes-benz",
    model: "GLC",
    compatibility: ["Mercedes-Benz GLC X253", "Mercedes-Benz GLC X254"],
    price: 45100,
    availability: "уточнить",
    delivery: "Срок зависит от поставщика и состояния узла",
    analogs: ["A0008301402", "ZP-AC-1402"],
    condition: "восстановленная",
    quality: "проверенная контрактная",
    stock: "подбор",
    description: "Узел для заявки с проверкой состояния, шкива, разъемов и гарантии.",
    specs: {
      Система: "кондиционирование",
      Состояние: "восстановленный узел",
      Проверка: "шкив, муфта, герметичность",
      Гарантия: "по условиям поставщика"
    }
  },
  {
    id: "duster-rear-shock",
    slug: "duster-rear-shock",
    name: "Амортизатор задний",
    oem: "56210-ZP000",
    article: "ZP-SUS-2100",
    manufacturer: "KYB",
    category: "Подвеска и рулевое",
    categorySlug: "suspension-steering",
    brand: "Renault",
    brandSlug: "renault",
    model: "Duster",
    compatibility: ["Renault Duster HS", "Renault Duster HM"],
    price: 6200,
    availability: "в наличии",
    delivery: "Резерв в день обращения",
    analogs: ["344703", "ZP-SUS-4703"],
    condition: "новая",
    quality: "заводской аналог",
    stock: "4 шт.",
    description: "Новая позиция для регулярного ремонта подвески.",
    specs: {
      Ось: "задняя",
      Тип: "газомасляный",
      Количество: "1 шт.",
      Рекомендация: "менять парой"
    }
  },
  {
    id: "vesta-ac-radiator",
    slug: "vesta-ac-radiator",
    name: "Радиатор кондиционера",
    oem: "8450 000 ZP1",
    article: "ZP-CLM-0001",
    manufacturer: "Luzar",
    category: "Двигатель",
    categorySlug: "engine",
    brand: "Lada",
    brandSlug: "lada",
    model: "Vesta",
    compatibility: ["Lada Vesta 2180", "Lada Vesta NG"],
    price: 9400,
    availability: "1-3 дня",
    delivery: "Поставка со склада партнера",
    analogs: ["8450008025", "ZP-CLM-8025"],
    condition: "новая",
    quality: "заводской аналог",
    stock: "3 шт.",
    description: "Пример локального ассортимента для российских автомобилей.",
    specs: {
      Система: "кондиционер",
      Материал: "алюминий",
      Комплектность: "радиатор без осушителя",
      Состояние: "новый"
    }
  },
  {
    id: "rav4-tail-lamp-right",
    slug: "rav4-tail-lamp-right",
    name: "Фонарь задний правый",
    oem: "81551-42ZP0",
    article: "ZP-LGT-42R",
    manufacturer: "Koito",
    category: "Кузов и оптика",
    categorySlug: "body-lighting",
    brand: "Toyota",
    brandSlug: "toyota",
    model: "RAV4",
    compatibility: ["Toyota RAV4 XA50"],
    price: 21300,
    availability: "под заказ",
    delivery: "Фото и состояние подтверждаются до резерва",
    analogs: ["81551-42180", "ZP-LGT-2180R"],
    condition: "контрактная",
    quality: "проверенная контрактная",
    stock: "поставщик",
    description: "Кузовная позиция с обязательной проверкой стороны, цвета и креплений.",
    specs: {
      Сторона: "правая",
      Тип: "наружный фонарь",
      Проверка: "крепления, стекло, разъем",
      Состояние: "контрактная"
    }
  },
  {
    id: "rio-front-bumper",
    slug: "rio-front-bumper",
    name: "Бампер передний",
    oem: "86511-H0ZP0",
    article: "ZP-BDY-H011",
    manufacturer: "Mobis",
    category: "Кузов и оптика",
    categorySlug: "body-lighting",
    brand: "Kia",
    brandSlug: "kia",
    model: "Rio",
    compatibility: ["Kia Rio FB", "Kia Rio X"],
    price: 18700,
    availability: "уточнить",
    delivery: "Проверка цвета, креплений и комплектации",
    analogs: ["86511-H0100", "ZP-BDY-H010"],
    condition: "контрактная",
    quality: "проверенная контрактная",
    stock: "по запросу",
    description: "Пример крупной кузовной детали, которую удобно оформлять через корзину-заявку.",
    specs: {
      Сторона: "перед",
      Комплектность: "без решеток и ПТФ",
      Проверка: "геометрия, крепления",
      Доставка: "транспортная компания"
    }
  }
];

export const reviews = [
  {
    name: "Алексей",
    city: "Москва",
    text: "Нашел редкую фару и получил фото до оплаты. Для MVP оставили как пример будущих реальных отзывов."
  },
  {
    name: "Марина",
    city: "Тверь",
    text: "Менеджер сверил артикул, предложил аналог и помог выбрать доставку до пункта выдачи."
  },
  {
    name: "Илья",
    city: "Нижний Новгород",
    text: "Понравилось, что заказ оформили как резерв: сначала подтвердили состояние и срок, потом оплату."
  }
];

export const formatPrice = (value: number) =>
  new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0
  }).format(value);

export const normalize = (value: string) => value.trim().toLowerCase();

export const findPartBySlug = (slug: string) => parts.find((part) => part.slug === slug);

export const getPartsByBrandSlug = (brandSlug: string) =>
  parts.filter((part) => part.brandSlug === brandSlug);

export const findBrandBySlug = (slug: string) => brands.find((brand) => brand.slug === slug);

export const getFeaturedParts = () => parts.slice(0, 8);

export const getPartSearchText = (part: Part) =>
  [
    part.name,
    part.oem,
    part.article,
    part.manufacturer,
    part.category,
    part.brand,
    part.model,
    part.condition,
    part.quality,
    ...part.analogs,
    ...part.compatibility,
    ...Object.values(part.specs)
  ]
    .join(" ")
    .toLowerCase();
