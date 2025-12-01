# API Overview

This page explains the general API layout, authentication and includes example requests.

## Base URL
When the Django server is running locally:

http://127.0.0.1:8000/

The API root (router) is mounted at:
/api/

The SPA client (Vite + Vue + Vuetify) expects the ``VITE_API_BASE_URL`` variable to point to the host that serves Django. Example ``.env`` contents for the front-end:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## CORS & Auth

- CORS is enabled via ``django-cors-headers`` for ``http://localhost:5173`` and ``http://127.0.0.1:5173`` with credentials support (cookies + Token header).
- Authentication flows rely on Djoser token endpoints:
  - ``POST /api/auth/token/login/`` — obtain token
  - ``POST /api/auth/token/logout/`` — revoke token
  - ``POST /api/auth/users/`` — registration
  - ``GET/PATCH /api/auth/users/me/`` — profile view/update
  - ``POST /api/auth/users/set_password/`` — change password

## Approved UI Interfaces

Согласованный с преподавателем перечень экранов (пункт 4 задания):

1. **Auth**: логин, регистрация, смена пароля, редактирование профиля.
2. **Dashboard**: обзор фонда, процентное распределение, ключевые показатели.
3. **Funds**: CRUD фондов, адресов и типов.
4. **Collections/Indexes**: CRUD комплектов и вспомогательных картотек.
5. **Items**: карточки музейных предметов, фильтры, создание авторов.
6. **Movement Acts**: учёт актов движения и строк движений (включая внешние организации/выставки).
7. **Reports**: пять аналитических запросов, описанных в задании (выставки по фондам, размеры комплектов и т.д.).

Каждый экран взаимодействует с DRF ViewSet’ами напрямую через Axios, токен авторизации подставляется автоматически.

## Domain Endpoints

| Сущность | Endpoint |
| --- | --- |
| Адреса | ``/api/addresses/`` |
| Фонды | ``/api/funds/`` (+ ``/exhibitions_count/``, ``/full_report/``) |
| Картотеки | ``/api/auxiliary-indexes/`` |
| Комплекты | ``/api/collections/`` (+ ``/{id}/items_count/``) |
| Авторы | ``/api/authors/`` |
| Предметы | ``/api/items/`` (+ отчётные действия) |
| Организации | ``/api/organizations/`` |
| Выставки | ``/api/exhibitions/`` |
| Участие в выставках | ``/api/exhibition-participations/`` |
| Акт движения | ``/api/movement-acts/`` |
| Строки движения | ``/api/movements/`` |

Бэкенд реализует полный CRUD для каждой сущности, а также специализированные запросы:

1. ``GET /api/funds/exhibitions_count/`` — количество выставок по фондам.
2. ``GET /api/collections/`` → ``items_count`` — размер комплектов.
3. ``GET /api/items/{id}/related_by_exhibitions/`` — связанные предметы.
4. ``GET /api/items/written_off_count_by_fund/`` — списанные предметы по фондам за период.
5. ``GET /api/items/fund_volume_percentage/`` — доля фондов.
6. ``GET /api/funds/full_report/`` — расширенный отчёт для генератора ведомостей.

## Front-end Integration

Vue 3 + Pinia + Vuetify интерфейсы используют следующие сервисы:

- ``src/services/http.js`` создаёт два axios-клиента (``/api`` и ``/api/auth``) и управляет токеном.
- ``src/stores/auth.js`` оборачивает регистрацию, авторизацию, изменение профиля и пароля.
- Каждая страница вызывает DRF-ендпоинты и выводит ответ таблицами Vuetify.

При сборке фронтенда необходимо установить зависимости:

```
npm install
npm run dev
```

или эквивалентные команды для ``pnpm``/``yarn``.
