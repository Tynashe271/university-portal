# Anyschool High School — frontend

A Laravel app that renders the public site and portals (public site, online
application, applicant status portal, admissions staff portal, student
portal) as Blade views. It holds no data of its own and has no database:
every dynamic bit — auth, admissions, courses, dashboards, file uploads —
is handled client-side by [public/portal.js](public/portal.js) /
[public/app.js](public/app.js), calling the Django REST API in
[../backend/](../backend/) directly from the browser. Laravel's job here is
purely serving the page shells and shared layout (header/nav/footer) —
see [../README.md](../README.md) for how the two halves fit together and
how to run the whole app locally.

## Structure

- `routes/web.php` — one `Route::view()` per page, extensionless
  (`/about`, not `/about.html`)
- `resources/views/layouts/site.blade.php` — the public-site shell (notice
  bar, header/nav, footer) shared by the marketing pages
- `resources/views/layouts/portal.blade.php` — a much thinner shell for the
  application/portal/admin pages, which each own their full body markup
- `resources/views/partials/` — the header/footer used by `layouts.site`
- `public/` — `styles.css`/`app.js` (marketing pages) and
  `portal.css`/`portal.js` (portal pages), plus `og.png`

## Running it locally

```bash
composer install
cp .env.example .env   # first time only
php artisan key:generate   # first time only
php artisan serve --port=5500
```

Site available at `http://localhost:5500/`. The backend's CORS config
already allows this origin (`backend/config/settings.py`).

## Deploying it

Render has no native PHP runtime, so this deploys as a Docker web service
via the `Dockerfile` here — see the root README's
[deployment section](../README.md#deploying-it-for-real) for the full
picture (this service alongside the Django backend and Postgres, all from
one `render.yaml`).
