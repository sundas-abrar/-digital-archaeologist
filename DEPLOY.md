# Deploying Digital Archaeologist

Two services: the Next.js **frontend** and the FastAPI **backend**. They
deploy separately and talk to each other over HTTPS.

## 0. Before you deploy \u2014 read this

This app can **execute uploaded code** (Testing/QA panel, Agent Mode).
That's fine on your own machine; on a public URL it means anyone who
finds the link could upload a project and run commands on your server.
To prevent that, this build adds a **shared password gate**:

- The whole frontend is behind a password page (`/gate`).
- The backend independently rejects any API call (except `/api/health`)
  that doesn't include the same password.
- Both checks are **off automatically** if you don't set a password
  (e.g. running locally) \u2014 nothing changes for local development.

You choose the password yourself in step 3 and 4 below. **Use the same
value on both services.**

Also note: uploaded archives are stored on local disk
(`backend/storage/`). On most free hosting tiers that storage doesn't
survive a redeploy or restart \u2014 fine for demos, not for anything you
need to keep long-term.

---

## 1. Push to GitHub

Both `frontend/` and `backend/` can live in one repo. Each hosting step
below points at the same repo but a different **root directory**.

```bash
git init
git add .
git commit -m "Digital Archaeologist"
git remote add origin <your-repo-url>
git push -u origin main
```

(Make sure `.gitignore` in both `frontend/` and `backend/` is in place
so `node_modules`, `venv`, `.next`, and `storage/` don't get committed
\u2014 they already are in this project.)

---

## 2. Deploy the backend (Railway)

[Railway](https://railway.app) is the simplest option for a FastAPI app
that needs a persistent-ish process (not a serverless function) and
lets you run shell commands via subprocess (Vercel's serverless
functions can't do this reliably).

1. New Project \u2192 Deploy from GitHub repo \u2192 pick this repo.
2. Set **Root Directory** to `backend`.
3. Railway auto-detects Python. If it asks for a start command, use
   what's in `backend/Procfile`:
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (Railway \u2192 Variables):
   - `GROQ_API_KEY` \u2014 your key from console.groq.com/keys (optional,
     enables real AI narratives instead of the template fallback)
   - `SITE_PASSWORD` \u2014 pick a password. **Write it down** \u2014 you'll
     enter the same value on the frontend in step 3.
   - `ALLOWED_ORIGINS` \u2014 leave blank for now, come back after step 3.
5. Deploy. Railway gives you a URL like `https://your-app.up.railway.app`.
   **Copy it.**
6. Visit `https://your-app.up.railway.app/api/health` \u2014 you should see
   `{"status": "ok", ...}`. This route is intentionally not
   password-gated so you (and the hosting platform) can always check
   it's alive.

(Render is a fine alternative \u2014 same idea: root directory `backend`,
build command `pip install -r requirements.txt`, start command from
`Procfile`, same environment variables.)

---

## 3. Deploy the frontend (Vercel)

1. [vercel.com](https://vercel.com) \u2192 New Project \u2192 import the same
   GitHub repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset: Next.js (auto-detected).
4. Add environment variables (Vercel \u2192 Settings \u2192 Environment Variables):
   - `NEXT_PUBLIC_API_URL` = the Railway URL from step 2
     (e.g. `https://your-app.up.railway.app`)
   - `SITE_PASSWORD` = the **exact same value** you set on Railway.
5. Deploy. Vercel gives you a URL like `https://your-app.vercel.app`.

---

## 4. Connect them: allow the frontend's origin on the backend

Go back to Railway \u2192 Variables \u2192 set:

```
ALLOWED_ORIGINS=https://your-app.vercel.app
```

(Comma-separate multiple origins if you also have a custom domain.)
Redeploy/restart the backend service for this to take effect.

---

## 5. Test it

1. Open your Vercel URL. You should land on `/gate`.
2. Enter the password you set in steps 2 and 3.
3. Upload a small `.zip`, run it through the dashboard, try the
   Testing/QA and Agent Mode tabs.
4. If something fails with a network/CORS error, double check
   `NEXT_PUBLIC_API_URL` (frontend) and `ALLOWED_ORIGINS` (backend)
   match exactly, including `https://` and no trailing slash.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Stuck on `/gate` even with the right password | `SITE_PASSWORD` differs between Vercel and Railway \u2014 must match exactly |
| `401` errors after logging in | Same as above, or the backend hasn't picked up a new `SITE_PASSWORD` yet (redeploy it) |
| CORS error in the browser console | `ALLOWED_ORIGINS` on the backend doesn't include your exact Vercel URL |
| Findings/QA/Agent work locally but nothing happens when deployed | The uploaded session's files were on a previous instance/restart and got wiped \u2014 re-upload |
| "groq package isn't installed" or AI features silently fall back | `GROQ_API_KEY` isn't set on Railway, or `requirements.txt` didn't install `groq` \u2014 check the Railway build logs |
