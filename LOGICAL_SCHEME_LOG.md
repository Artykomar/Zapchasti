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
P:[/delivery]>{published legal text|safe fallback before approval}
P:[/privacy-policy|/personal-data-consent|/terms]>{published LegalDocument,version|safe fallback}
P:[/about|/reviews]>{trust content,moderated real reviews only,non-transactional}
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

## 5. `zemazap_production_flow_2026_08_23`

```text
X:[DNS+ALB+HTTPS+WAF]>B:[Caddy :8080]
B:[Caddy]>?{path}
?{/admin|/static|/media|/api/payments|/api/imports}>B:[Django/Gunicorn]
?{other}>B:[Next.js standalone]
B:[Next server routes]>B:[Django internal :8000]
B:[Django Admin publish LegalDocument]>D:[approved versioned plain text]
D:[published LegalDocument]>B:[safe site-settings API]>P:[policy|consent|terms|delivery]
B:[deploy preflight]>?{7 approved documents present}>[rollout|stop]
B:[Django]>D:[Managed PostgreSQL|Object Storage]
B:[scheduler every minute]>[reconcile payments|deliver notifications|retry failed receipts]
B:[scheduler daily]>[retention/anonymization]

R:[Manager + create_payment_link]>A:[admin create payment link]>X:[Alfa register]
X:[Alfa callback + secret]>B:[server-to-server status]>D:[Payment+Order journal]
R:[Accountant + reconcile_payment]>A:[manual status refresh]>X:[Alfa status]
R:[Refund operator]>A:[retry failed refund]>B:[read provider refunded amount]
?{already refunded}>D:[reconcile without resend]
?{not refunded}>X:[refund.do]

?{paid && fiscal mock}>D:[Receipt=validated]
?{paid && fiscal alfa}>D:[Receipt=pending_confirmation]
!:[pending_confirmation is not a fiscal success; verify KKT/OFD externally]
!:[production remains disabled until real legal/company/cloud/bank/KKT data and staging acceptance]
```

## 6. `zemazap_local_acceptance_2026_08_23`

```text
B:[Playwright]>[Next :3100 + Django :8100 + disposable SQLite]
B:[E2E]>[catalog/cart request|standalone request|favorites persistence/remove|admin handoff/login|payment-return safety]
D:[frontend catalog definitions]>[types+helpers only]
D:[catalog products]>[Django API; demo seed only for local/E2E]
D:[favorites]>[localStorage current browser only; MVP decision]

B:[portable PostgreSQL 18.6 :55432 loopback-only]>D:[UTF8 zemazap_rehearsal]
B:[Django acceptance]>[migrations|checks|full backend suite|idempotent RBAC bootstrap]
B:[operations rehearsal]>[scheduler once|retention dry-run|external delivery disabled]
B:[pg_dump]>D:[custom-format backup]>B:[pg_restore]>D:[verified 12 parts+5 roles]
!:[no Docker, no Windows service, no production credentials/data]
```
