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
