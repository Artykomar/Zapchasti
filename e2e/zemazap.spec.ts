import { expect, test } from "@playwright/test";

const productName = "Фильтр масляный";
const cookieNoticeName = "zemazap_cookie_notice";

test.beforeEach(async ({ context }) => {
  await context.addCookies([
    {
      name: cookieNoticeName,
      value: "acknowledged",
      url: "http://127.0.0.1:3100"
    }
  ]);
});

test("cookie notice appears on first visit and stays dismissed", async ({ context, page }) => {
  await context.clearCookies();
  await page.goto("/");

  const notice = page.getByRole("dialog", { name: "Файлы cookie" });
  await expect(notice).toBeVisible();
  await notice.getByRole("button", { name: "Понятно" }).click();
  await expect(notice).toBeHidden();
  await expect.poll(async () => (await context.cookies()).some((cookie) => cookie.name === cookieNoticeName)).toBe(true);

  await page.reload();
  await expect(page.getByRole("dialog", { name: "Файлы cookie" })).toHaveCount(0);
});

test("customer can find a product and submit a cart request", async ({ page }) => {
  await page.goto("/catalog");
  await expect(
    page.getByRole("heading", { level: 1, name: "Автозапчасти по маркам, категориям и артикулам" })
  ).toBeVisible();

  await page.getByPlaceholder(/Поиск по номеру/).fill("ZP-SRV-3500");
  const product = page.getByRole("article").filter({ hasText: productName });
  await expect(product).toHaveCount(1);
  await product.getByRole("button", { name: "В корзину" }).click();
  await expect(product.getByRole("button", { name: "В корзине" })).toBeVisible();

  await page.goto("/cart");
  const cartItem = page.getByRole("article").filter({ hasText: productName });
  await cartItem.getByRole("button", { name: "Увеличить" }).click();
  await expect(cartItem.getByLabel(`Количество ${productName}`)).toContainText("2");

  await page.getByLabel("Имя").fill("Тестовый клиент");
  await page.getByLabel("Телефон или мессенджер").fill("79990000000");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Оформить заявку" }).click();
  await expect(page.getByText(/Заявка сохранена в базе:/)).toBeVisible();
});

test("customer can submit a standalone part request", async ({ page }) => {
  await page.goto("/request");
  await page.getByLabel("Имя").fill("Тестовый клиент");
  await page.getByLabel("Телефон или мессенджер").fill("79990000001");
  await page.getByLabel("Автомобиль").fill("Hyundai Solaris 2020");
  await page.getByLabel("Что нужно найти").fill("Нужен масляный фильтр по артикулу");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Отправить заявку" }).click();
  await expect(page.getByText(/Заявка сохранена в базе:/)).toBeVisible();
});

test("favorites persist in this browser and can be removed", async ({ page }) => {
  await page.goto("/catalog");
  await page.getByPlaceholder(/Поиск по номеру/).fill("ZP-SRV-3500");
  const product = page.getByRole("article").filter({ hasText: productName });
  await product.getByRole("button", { name: "Добавить товар в избранное" }).click();
  await expect(product.getByRole("button", { name: "Удалить товар из избранного" })).toBeVisible();

  await page.goto("/izbrannoe");
  await expect(page.getByRole("article").filter({ hasText: productName })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("article").filter({ hasText: productName })).toBeVisible();
  await page.getByRole("button", { name: "Удалить" }).click();
  await expect(page.getByText("Избранного пока нет")).toBeVisible();
});

test("admin handoff and theme stay unified across the storefront and Django", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Включить тёмную тему" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.getByRole("link", { name: "войти от имени администратора" }).click();
  await expect(page).toHaveURL(/127\.0\.0\.1:8100\/admin\/login/);
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.locator('input[name="username"]').fill("e2e_admin");
  await page.locator('input[name="password"]').fill("zemazap-e2e-only");
  await page.locator('input[type="submit"]').click();
  await expect(page).toHaveURL(/127\.0\.0\.1:8100\/admin\/owner\/$/);
  await expect(page.getByRole("heading", { level: 1, name: "Центр управления" })).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");

  await page.goto("http://127.0.0.1:8100/admin/leads/customerrequest/");
  await expect(page.locator("#nav-sidebar")).toBeVisible();
  await expect(page.locator('link[href$="warehouse/admin.css"]')).toHaveCount(1);
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.getByRole("button", { name: "Включить светлую тему" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");

  await page.goto("http://127.0.0.1:3100/");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
});

test("payment-return pages never trust the browser redirect", async ({ page }) => {
  await page.goto("/payment/success");
  await expect(page.getByRole("heading", { level: 1, name: "Платеж проверяется" })).toBeVisible();
  await expect(page.getByText(/Возврат браузера из банка сам по себе не подтверждает оплату/)).toBeVisible();

  await page.goto("/payment/fail");
  await expect(page.getByRole("heading", { level: 1, name: "Платеж не завершен" })).toBeVisible();
});
