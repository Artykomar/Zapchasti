# LOGICAL_SCHEME_LOG

Дата создания: 2026-08-15.

Назначение: компактный лог четырех логических схем для сравнения Zemazap и сайта-образца `https://scoda-pro.ru/`.

## Ключ шифра `LS-DSL-V1`

Это не криптографическое шифрование, а компактный логический DSL, чтобы схему можно было быстро читать, переносить и сравнивать.

- `R:` роль.
- `P:` публичная страница или экран.
- `A:` действие пользователя.
- `B:` backend/серверная операция.
- `D:` данные/хранилище.
- `X:` внешний сервис.
- `?` условие или развилка.
- `!` ограничение, риск или неготовая зона.
- `>` переход.
- `|` альтернативы.
- `[]` логический узел.
- `{}` данные, которые узел читает или пишет.
- `()` пояснение.

## 1. `zemazap_frontend_flow`

```text
R:[Покупатель]
P:[/]>{hero,search,brand-model-picker,popular-categories,featured-parts,delivery-guarantee}
A:[search|brand|category click]>P:[/catalog|/shop]
P:[/catalog]>{filters:q,brand,category,condition; cards; add-cart; favorite; product-link}
P:[/product-category/[brand]]>{brand intro; model/category/product list}>P:[/product/[slug]]
P:[/product/[slug]]>{price,availability,oem,article,analogs,compatibility,delivery,warranty}>A:[add cart|favorite|request]
A:[add cart]>D:[localStorage.cart]>P:[/cart]
A:[favorite]>D:[localStorage.favorites]>P:[/izbrannoe|/favorites]
P:[/cart]>{items,qty,total,name,phone,privacy-consent}>A:[submit request]>B:[POST /api/requests]>P:[success id]
P:[/request]>{name,phone,vehicle,request_text,privacy-consent}>B:[POST /api/requests]>P:[success id]
P:[/orders/[token]]>{confirmed order snapshot,total,status,payment_url?}>A:[pay if link]>X:[payment provider/mock]
P:[/payment/success|/payment/fail]>P:[contacts|order]
P:[/contacts]>{tel,mailto,MAX?,address,map-placeholder,legal-details}
P:[/delivery]>{reserve,payment,delivery,warranty,return terms draft}
P:[/privacy-policy|/personal-data-consent|/terms]>{legal drafts,versions}
P:[/about|/reviews]>{trust content,non-transactional}
!:[no public buybacks; no card data input; real contacts/legal data pending]
```

## 2. `zemazap_backend_flow`

```text
R:[Admin/Manager]>P:[/admin]>B:[Django Admin auth/users/groups]
D:[catalog]{Brand,CarModel,Generation,Category,Manufacturer,Supplier,Part,PartNumber,Compatibility,Specs,PriceOffer}
B:[GET /api/catalog]>D:[catalog]>P:[catalog/shop/home/product pages]
B:[GET /api/catalog/<slug>]>D:[Part snapshot]>P:[product page]
B:[POST /api/imports/prices staff-only]>D:[ImportRun,Part,PriceOffer]
B:[POST /api/requests]>D:[Customer,CustomerRequest,Items,Events,consent metadata]
B:[notify_manager]>X:[email detailed|Telegram PII-safe by default]
A:[admin create order from request]>B:[create_order_from_request]>D:[Order,OrderItem,StatusHistory,Comment]
A:[manager confirms order]>D:[Order.status=confirmed_by_manager]
B:[POST /api/payments/create-link staff-only]>?{PAYMENTS_ENABLED && confirmed && amount>0}>D:[Payment,Attempt,Event]>P:[/orders/[token] payment_url]
B:[POST /api/payments/mock/callback]>?{PAYMENTS_MODE=test}>D:[Payment.status,Order.status]
?{FISCALIZATION_ENABLED && payment succeeded}>B:[create_test_sale_receipt]>D:[FiscalReceipt,ReceiptItem,ReceiptEvent]
D:[core]{SiteSettings,LegalEntitySettings,feature flags,deploy checks}
!:[real Alfa API, real bank status check, real KKT/OFD, refunds/claims, monitoring, CI/CD, production infra pending]
```

## 3. `scoda_pro_visible_frontend_flow`

Источник: публично видимая структура `https://scoda-pro.ru/`, `/shop`, `/cart`, `/contacts`, `/delivery`, `/buybacks`, `/auth-page` на 2026-08-15.

```text
R:[Покупатель]
P:[/]>{header:favorite,cart,login,phones; nav; brand/model/category blocks; product highlights; contacts block}
P:[header]>A:[favorite]>P:[/izbrannoe/]
P:[header]>A:[cart]>P:[/cart/]
P:[header]>A:[login]>P:[/auth-page]
P:[header]>A:[phone click]>X:[tel:+7965...|+7903...|+7915...]
P:[nav]>P:[/shop/|/about/|/buybacks/|/reviews/|/delivery/|/contacts/]
P:[/shop/]>{woocommerce catalog; search; filters; pagination; product cards; add cart/favorite?}>P:[product]
P:[/product-category/{brand}/{model}/]>{VAG brand/model pages: Audi,Skoda,Seat,Volkswagen}>P:[product cards]
P:[product]>{photo,price,availability?,cart controls?,callback/request?}>P:[/cart/]
P:[/cart/]>{cart lines,qty,coupon/checkout-like flow?,contact form blocks}
P:[/auth-page]>{login/register/lost-password-like forms}
P:[/contacts/]>{phones,email,Telegram,WhatsApp,address,map,contact form}
P:[/delivery/]>{delivery/payment/service text,contact form,contacts/map block}
P:[/buybacks/]>{car buyback flow,steps,reviews,contact form}
P:[/reviews/]>{reviews,trust block,request/contact call to action}
P:[/privacy-policy]>{personal data policy}
!:[visible frontend includes buybacks/auto dismantling mechanics that Zemazap intentionally excludes]
```

## 4. `scoda_pro_inferred_backend_flow`

Основание: публичный HTML показывает WordPress/WooCommerce assets, Ajax search plugin, WooCommerce cart pages and forms. Закрытая админка не видна, поэтому это предположение.

```text
R:[Site Admin]>P:[/wp-admin? inferred]>B:[WordPress auth]
D:[WordPress]{pages,menus,theme blocks,media,forms,users}
D:[WooCommerce]{products,categories,attributes,prices,stock,cart,sessions,orders?}
B:[theme render]>P:[home,about,buybacks,reviews,delivery,contacts]
B:[WooCommerce catalog]>P:[/shop/,/product-category/.../,product pages]
B:[Ajax search plugin]>D:[products/search index]>P:[search suggestions/results]
B:[cart/session]>D:[WooCommerce cart/session]>P:[/cart/]
B:[forms plugin/custom theme forms]>D:[lead/request records or email notifications]>X:[email/CRM?]
B:[contacts block]>D:[theme options/contact settings]>X:[tel,mailto,Telegram,WhatsApp,map]
R:[Manager/Admin]>A:[manage products/orders/leads/pages]>B:[WordPress/WooCommerce admin]
!:[payment/acquiring/fiscalization not confirmed from public view]
!:[admin roles, CRM, notifications, order processing cannot be verified without access]
```
