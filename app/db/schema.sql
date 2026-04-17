CREATE TABLE IF NOT EXISTS trend_candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  topic TEXT NOT NULL,
  summary TEXT NOT NULL,
  url TEXT,
  sport TEXT DEFAULT 'general',
  discovered_at TEXT NOT NULL,
  fingerprint TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS trend_scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_candidate_id INTEGER NOT NULL,
  recency REAL NOT NULL,
  audience_fit REAL NOT NULL,
  virality REAL NOT NULL,
  controversy REAL NOT NULL,
  recognition REAL NOT NULL,
  ease_of_execution REAL NOT NULL,
  clarity_1s_score REAL NOT NULL DEFAULT 0,
  star_power_score REAL NOT NULL DEFAULT 0,
  search_heat_score REAL NOT NULL DEFAULT 0,
  emotion_score REAL NOT NULL DEFAULT 0,
  pov_strength_score REAL NOT NULL DEFAULT 0,
  fan_identity_score REAL NOT NULL DEFAULT 0,
  rivalry_score REAL NOT NULL DEFAULT 0,
  sendability_score REAL NOT NULL DEFAULT 0,
  view_score REAL NOT NULL DEFAULT 0,
  follow_score REAL NOT NULL DEFAULT 0,
  share_score REAL NOT NULL DEFAULT 0,
  primary_goal TEXT NOT NULL DEFAULT 'views',
  total_score REAL NOT NULL,
  reasoning TEXT,
  recommended INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  FOREIGN KEY(trend_candidate_id) REFERENCES trend_candidates(id)
);

CREATE TABLE IF NOT EXISTS hooks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_candidate_id INTEGER NOT NULL,
  trend_score_id INTEGER,
  hook_text TEXT NOT NULL,
  style TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(trend_candidate_id) REFERENCES trend_candidates(id),
  FOREIGN KEY(trend_score_id) REFERENCES trend_scores(id)
);

CREATE TABLE IF NOT EXISTS content_packs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_candidate_id INTEGER NOT NULL,
  hook_id INTEGER NOT NULL,
  overlay_lines TEXT NOT NULL,
  caption TEXT NOT NULL,
  cta TEXT NOT NULL,
  creator_notes TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(trend_candidate_id) REFERENCES trend_candidates(id),
  FOREIGN KEY(hook_id) REFERENCES hooks(id)
);

CREATE TABLE IF NOT EXISTS performance_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content_pack_id INTEGER,
  platform TEXT NOT NULL,
  metric_name TEXT NOT NULL,
  metric_value REAL NOT NULL,
  logged_at TEXT NOT NULL,
  FOREIGN KEY(content_pack_id) REFERENCES content_packs(id)
);

CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  platform TEXT NOT NULL,
  post_timestamp TEXT NOT NULL,
  views REAL NOT NULL DEFAULT 0,
  likes REAL NOT NULL DEFAULT 0,
  comments REAL NOT NULL DEFAULT 0,
  shares REAL NOT NULL DEFAULT 0,
  saves REAL NOT NULL DEFAULT 0,
  profile_views REAL NOT NULL DEFAULT 0,
  followers_gained REAL NOT NULL DEFAULT 0,
  watch_time REAL NOT NULL DEFAULT 0,
  completion_rate REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS post_metadata (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  hook_type TEXT NOT NULL,
  topic_type TEXT NOT NULL,
  length_seconds REAL NOT NULL,
  teams_tagged TEXT NOT NULL DEFAULT '[]',
  players_tagged TEXT NOT NULL DEFAULT '[]',
  video_style TEXT NOT NULL,
  FOREIGN KEY(post_id) REFERENCES posts(id)
);

CREATE TABLE IF NOT EXISTS performance_metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  follower_conversion_rate REAL NOT NULL,
  engagement_rate REAL NOT NULL,
  comment_rate REAL NOT NULL,
  share_rate REAL NOT NULL,
  save_rate REAL NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(post_id) REFERENCES posts(id)
);

CREATE TABLE IF NOT EXISTS agent_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_name TEXT NOT NULL,
  status TEXT NOT NULL,
  run_started_at TEXT NOT NULL,
  run_finished_at TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS grouped_insights (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL,
  insight_type TEXT NOT NULL,
  insight_key TEXT NOT NULL,
  posts_count INTEGER NOT NULL,
  avg_views REAL NOT NULL,
  avg_follower_conversion_rate REAL NOT NULL,
  avg_engagement_rate REAL NOT NULL,
  avg_completion_rate REAL NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(run_id) REFERENCES agent_runs(id)
);

CREATE TABLE IF NOT EXISTS engine_recommendations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL,
  engine_target TEXT NOT NULL,
  action TEXT NOT NULL,
  focus TEXT NOT NULL,
  reason TEXT NOT NULL,
  priority TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(run_id) REFERENCES agent_runs(id)
);

CREATE TABLE IF NOT EXISTS post_sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  source TEXT NOT NULL,
  source_post_id TEXT,
  post_url TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(post_id) REFERENCES posts(id)
);
