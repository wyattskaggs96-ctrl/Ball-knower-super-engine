# Manual Analytics Intake Guide

## 1) Fill out this file
Use `data/manual_tiktok_analytics.csv` for each batch of TikTok post results.

## 2) Column definitions
- `post_id`: your internal ID for the post (required)
- `post_url`: TikTok URL (optional)
- `post_timestamp`: ISO timestamp, e.g. `2026-04-15T13:12:00Z` (required)
- `topic_type`: content topic category (required)
- `hook_type`: opening hook category (required)
- `video_style`: production format/style (required)
- `teams_tagged`: teams separated by `|` (optional)
- `players_tagged`: players separated by `|` (optional)
- `length_seconds`: video length in seconds (required)
- `views`: total views (required)
- `likes`, `comments`, `shares`, `saves`, `profile_views`, `followers_gained`: post metrics (optional, defaults to 0)
- `watch_time_seconds`: average watch time in seconds (optional, defaults to 0)
- `completion_rate`: completion as decimal, e.g. `0.57` (optional, defaults to 0)

## 3) Import manual analytics
```bash
python main.py feedback-import --file data/manual_tiktok_analytics.csv
```

## 4) Run feedback loop
```bash
python main.py feedback-run --source manual --file data/manual_tiktok_analytics.csv
```

Also supported:
- `python main.py feedback-run --source mock`
- `python main.py feedback-run --source all --file data/manual_tiktok_analytics.csv`

## 5) Find outputs
After a run, outputs are regenerated in `data/exports/`:
- `daily_feedback.md`
- `engine_recommendations.json`
- `weekly_review.md`
