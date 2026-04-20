from __future__ import annotations

import sqlite3

from .config import VisualizerConfig


SCHEMA_SQL = """
create table if not exists runs (
  run_id text primary key,
  session_id text,
  objective text not null,
  status text not null,
  started_at text not null,
  finished_at text,
  model text,
  workspace text,
  summary text
);

create table if not exists events (
  event_id text primary key,
  run_id text not null,
  session_id text,
  event_type text not null,
  phase text,
  agent text,
  status text,
  ts text not null,
  title text,
  payload_json text not null,
  foreign key (run_id) references runs(run_id)
);
create index if not exists idx_events_run_ts on events(run_id, ts);
create index if not exists idx_events_type on events(event_type);

create table if not exists file_impacts (
  id integer primary key autoincrement,
  run_id text not null,
  event_id text,
  path text not null,
  change_type text not null,
  summary text,
  agent text,
  phase text,
  ts text not null,
  foreign key (run_id) references runs(run_id)
);
create index if not exists idx_file_impacts_run on file_impacts(run_id);

create table if not exists approvals (
  approval_id text primary key,
  run_id text not null,
  tool_name text not null,
  arguments_json text,
  status text not null,
  requested_at text not null,
  resolved_at text,
  resolution_note text,
  foreign key (run_id) references runs(run_id)
);

create table if not exists verification_results (
  id integer primary key autoincrement,
  run_id text not null,
  kind text not null,
  command text,
  status text not null,
  duration_ms integer,
  details_json text,
  ts text not null,
  foreign key (run_id) references runs(run_id)
);
"""


def connect(config: VisualizerConfig) -> sqlite3.Connection:
    config.ensure_directories()
    conn = sqlite3.connect(config.sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(config: VisualizerConfig) -> None:
    with connect(config) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
