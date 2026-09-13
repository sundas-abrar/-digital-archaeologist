# Deploying Digital Archaeologist

This deploys the backend to **Render** (free tier, supports Docker + a
small persistent disk for `storage/`) and the frontend to **Vercel**
(free tier, built for Next.js). Both connect directly to your GitHub
repo, so once set up, every `git push` can auto-redeploy.

## 1. Deploy the backend (Render)

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. **New +** \u2192 **Blueprint** \u2192 pick your `digital-archaeologist` repo.
   Render will detect `render.yaml` at the repo root and pre-fill the
   service (free-tier Docker web service, `backend/` as root dir \u2014
   no credit card required for this).
3. Before deploying, set the environment variables it asks for:
   - `GROQ_API_KEY` \u2014 your key from console.groq.com/keys (optional;
     leave blank and AI interpretation just falls back to a template).
   - `ALLOWED_ORIGINS` \u2014 leave blank for now, you'll fill this in
     after step 2 gives you the Vercel URL.
4. Click **Apply** / **Create**. First build takes a few minutes.
5. Once live, copy the backend's URL, something like:
   `https://digital-archaeologist-backend.onrender.com`

**Note:** Render's free tier spins the service down after inactivity;
the first request after idling can take ~30-50s to wake up.

## 2. Deploy the frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
2. **Add New** \u2192 **Project** \u2192 pick the same repo.
3. Set **Root Directory** to `frontend` (Vercel auto-detects Next.js
   once you do).
4. Add an environment variable:
   - `NEXT_PUBLIC_API_URL` = the Render backend URL from step 1
     (e.g. `https://digital-archaeologist-backend.onrender.com`)
5. Click **Deploy**. You'll get a URL like
   `https://digital-archaeologist.vercel.app`.

## 3. Connect the two

Go back to Render \u2192 your backend service \u2192 Environment \u2192 set:
```
ALLOWED_ORIGINS=https://digital-archaeologist.vercel.app
```
Save \u2014 Render redeploys automatically. This lets the deployed frontend
actually call the deployed backend (CORS blocks it otherwise).

## 4. Test it

Open your Vercel URL, go to `/status` \u2014 it should show "Signal
confirmed" once the backend finishes waking up. Then try an upload.

## Notes

- **No credit card needed** on Render's free web-service tier or
  Vercel's free tier.
- Free tier has no persistent disk, so files in `backend/storage/`
  are wiped on every redeploy or when the free instance spins down
  from inactivity. Fine for demo use (upload \u2192 analyze \u2192 download
  report in one sitting); if you need sessions to survive longer,
  that needs a paid Render instance + disk (~$7-8/mo).
- Every `git push` to `main` auto-redeploys both services.
- Local development is unaffected \u2014 `NEXT_PUBLIC_API_URL` and
  `ALLOWED_ORIGINS` both default to localhost when unset.
