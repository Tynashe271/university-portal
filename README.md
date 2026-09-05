# University Portal (Anyschool High School)

A monorepo combining:

- **[backend/](backend/)** — Django REST API (students, courses, admissions,
  fees, attendance, schedule, announcements, and more). See
  [backend/README.md](backend/README.md) for the full API reference.
- **[frontend/](frontend/)** — the Anyschool High School site and portals
  (public site, online application, applicant status portal, admissions
  staff portal, student portal), rendered as Laravel Blade views and wired
  to talk to the backend over its REST API. See
  [frontend/README.md](frontend/README.md) for how it's put together —
  it holds no data of its own; all real logic is the Django API.

Each half keeps its own git history from before the merge (the backend's
prior commit and the frontend's prior 12 commits are both still reachable —
see `git log --graph --all`).

## Running it locally

**Backend** — from `backend/`:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

API available at `http://localhost:8000/`. Default accounts: `admin` /
`admin123` (admin), `student1` / `student123` (student).

**Frontend** — from `frontend/` (first time only: `composer install` then
`cp .env.example .env && php artisan key:generate`), serve it on port 5500
(the backend's CORS config allows this origin):

```bash
php artisan serve --port=5500
```

Site available at `http://localhost:5500/`.

> The frontend resolves the API host at runtime (see the top of
> `frontend/public/portal.js` / `frontend/public/app.js`) rather than
> hardcoding it: it uses `http://localhost:8000/api` for local dev, the
> known Render backend when viewed from the deployed Render frontend, and
> otherwise guesses `<same host>:8000/api` (e.g. for a LAN IP). To point it
> somewhere else, hand-edit the `<meta name="api-base" content="...">` tag
> in the relevant Blade layout (`frontend/resources/views/layouts/`) — any
> value other than the localhost default takes precedence over the
> automatic guess. Either way, add the frontend's origin to
> `CORS_ALLOWED_ORIGINS` (or the `CORS_EXTRA_ORIGINS` env var in
> production) in `backend/config/settings.py`.

## Deploying it for real

[render.yaml](render.yaml) is a Render Blueprint that provisions all three
pieces — the Django backend, the Laravel frontend, and a Postgres database —
from one file: in the Render dashboard, **New → Blueprint**, connect this
repo, and **Apply**. It expects the backend and frontend services to be
named `anyschool-backend` / `anyschool-frontend` (that's what the frontend's
runtime API-host guess above looks for); renaming either means updating
that hostname in `portal.js`/`app.js`, or just hand-editing the `api-base`
meta tag instead. Render has no native PHP runtime, so the frontend deploys
as a Docker web service — see `frontend/Dockerfile` and
[frontend/README.md](frontend/README.md).

**Free-tier caveats** (all from Render's own limits, not this app): the
free Postgres database expires 30 days after creation and has to be
recreated to keep going for free; both free web services spin down after 15
minutes idle (the first request after that takes ~30-50s to wake it back
up); and anything written to the backend's local disk — uploaded admission
documents/photos in `MEDIA_ROOT` — is lost on every redeploy, since the
free tier has no persistent disk. That last one needs real object storage
(e.g. `django-storages` + an S3-compatible bucket) before uploads can be
trusted to survive; it isn't wired up here.

Everything the backend needs from the environment (`SECRET_KEY`, `DEBUG`,
`ALLOWED_HOSTS`, `DATABASE_URL`, `CORS_EXTRA_ORIGINS`) is read in
`backend/config/settings.py` with sensible local-dev defaults when unset —
see the comments right above each one there.

## Notes on the integration

- Public application submission and applicant status lookup are open
  endpoints (no login); listing all applications and approving/rejecting
  them requires an admin-role account.
- The applicant portal signs in with **application reference + parent/
  guardian email** rather than a password — the admissions model has no
  password field.
- Document uploads on the application form are not yet wired to the
  backend (the relevant `FileField`s exist on the model but the frontend
  currently submits JSON, not multipart form data).
