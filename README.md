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

> The frontend calls the API at `http://localhost:8000/api` (hardcoded in
> `frontend/portal.js`). If you serve the backend from a different host or
> port, update `API_BASE` there and add the new frontend origin to
> `CORS_ALLOWED_ORIGINS` in `backend/config/settings.py`.

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
