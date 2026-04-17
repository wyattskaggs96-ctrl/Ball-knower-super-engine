# Mobile Command Center (V1) Guide

## What this is
Ball Knower Mobile Command Center is a phone-friendly web page for one-tap access to the top recommendation for:
- views
- followers
- shares

Each card includes:
- topic
- hook
- caption
- hashtags
- why selected
- best window

## Local run (developer)
From repo root:

```bash
python main.py mobile-refresh
python main.py mobile-serve --host 0.0.0.0 --port 8000
```

Open:
- `http://localhost:8000` (same machine)
- `http://<your-computer-local-ip>:8000` (phone on same Wi-Fi)

## Deploy to Render
1. Push this repo to GitHub.
2. In Render, create a **Web Service** from the repo.
3. Use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app/mobile_server.py`
4. Render injects `PORT`; server reads it automatically.
5. After deploy, open your Render URL (for example `https://ball-knower-mobile.onrender.com`).

## Access from phone
- Open the Render URL directly in iPhone Safari.
- Optional local mode: use your computer LAN URL (`http://<local-ip>:8000`) while on same Wi-Fi.

## Run Engine button behavior (V1)
- UI button calls `POST /run-engine`.
- Endpoint runs the existing mobile refresh pipeline and rewrites `data/exports/mobile_command_center.json`.
- UI then reloads latest recommendations from `GET /mobile_command_center.json`.

## Save to Home Screen (iPhone)
1. Open the page in Safari.
2. Tap **Share**.
3. Tap **Add to Home Screen**.
4. Name it "Ball Knower" and tap **Add**.

## What V1 does
- Mobile-first stacked cards for views/followers/shares.
- One-button refresh from existing engine outputs.
- One-tap copy buttons for hook, caption, and hashtags.

## What V1 does not do yet
- No auth/login.
- No remote job queue or async worker.
- No push notifications.
- No persistent mobile app cache/offline mode.
- Not a native iOS app.
