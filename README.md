# University Portal (Anyschool High School)

A monorepo combining:

- **[backend/](backend/)** — Django REST API (students, courses, admissions,
  fees, attendance, schedule, announcements, and more). See
  [backend/README.md](backend/README.md) for the full API reference.
- **[frontend/](frontend/)** — the Anyschool High School static site and
  portals (public site, online application, applicant status portal,
  admissions staff portal, student portal), wired to talk to the backend
  over its REST API.

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

**Frontend** — from `frontend/`, serve the static files on port 5500 (the
backend's CORS config allows this origin):

```bash
python -m http.server 5500
```

Site available at `http://localhost:5500/`.

> The frontend resolves the API host at runtime (see the top of
> `frontend/portal.js` / `frontend/app.js`) rather than hardcoding it: it
> uses `http://localhost:8000/api` for local dev, the known Render backend
> when viewed from the deployed Render frontend, and otherwise guesses
> `<same host>:8000/api` (e.g. for a LAN IP). To point it somewhere else,
> hand-edit the `<meta name="api-base" content="...">` tag in the relevant
> HTML file(s) — any value other than the localhost default takes
> precedence over the automatic guess. Either way, add the frontend's
> origin to `CORS_ALLOWED_ORIGINS` (or the `CORS_EXTRA_ORIGINS` env var in
> production) in `backend/config/settings.py`.

## Deploying it for real

[render.yaml](render.yaml) is a Render Blueprint that provisions all three
pieces — the Django backend, the static frontend, and a Postgres database —
from one file: in the Render dashboard, **New → Blueprint**, connect this
repo, and **Apply**. It expects the backend and frontend services to be
named `anyschool-backend` / `anyschool-frontend` (that's what the frontend's
runtime API-host guess above looks for); renaming either means updating
that hostname in `portal.js`/`app.js`, or just hand-editing the `api-base`
meta tag instead.

**Free-tier caveats** (all from Render's own limits, not this app): the
free Postgres database expires 30 days after creation and has to be
recreated to keep going for free; the free web service spins down after 15
minutes idle (the first request after that takes ~30-50s to wake it back
up); and the free web service only has 512MB RAM and a small ephemeral
disk, so by default (see below) uploaded admission documents/photos in
`MEDIA_ROOT` are lost on every redeploy and can fail to save if the disk
fills up — this is the most common cause of "upload failed" reports from
real applicants.

**Fixing uploads for real: point them at object storage.** `django-storages`
is already wired up (`backend/config/settings.py`) — set these on the
backend service (Render dashboard → the service → Environment; the
blueprint above already declares them, just empty) and it switches from
local disk to an S3-compatible bucket, with no code changes needed:

- `AWS_STORAGE_BUCKET_NAME`
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_ENDPOINT_URL` — omit for real AWS S3; for an S3-compatible
  provider set it to that provider's endpoint

A free [Cloudflare R2](https://developers.cloudflare.com/r2/) bucket
(10 GB storage, no egress fees) works well here:
1. Cloudflare dashboard → R2 → **Create bucket**.
2. R2 → **Manage API tokens** → create a token with read/write access to
   that bucket → note the Access Key ID, Secret Access Key, and the
   account-specific endpoint it gives you
   (`https://<account-id>.r2.cloudflarestorage.com`).
3. Set the four env vars above on the Render backend service with those
   values and redeploy.

The bucket is kept private — uploaded certificates/documents are personal,
so the app serves them via time-limited signed URLs rather than public
links (see `AWS_QUERYSTRING_*` in `settings.py`) — and unset, everything
falls back to local disk exactly as before, so this is opt-in.

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
