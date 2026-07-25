import CartContents from "@/src/components/CartContents";

export default function CartPage() {
  return (
    <main className="page-shell">
      <section className="page-heading">
        <p className="eyebrow">Корзина Zemazap</p>
        <h1>Корзина работает как заявка менеджеру</h1>
        <p>
          В локальном макете товары сохраняются в браузере. После backend-этапа эта форма станет
          настоящим заказом с уведомлением менеджера и записью в базу.
        </p>
      </section>

      <CartContents />
    </main>
  );
}
