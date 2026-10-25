CREATE TABLE IF NOT EXISTS organizations(id uuid PRIMARY KEY, name text NOT NULL);
CREATE TABLE IF NOT EXISTS users(id uuid PRIMARY KEY,organization_id uuid NOT NULL REFERENCES organizations(id),email text NOT NULL UNIQUE,password_hash text NOT NULL,role text NOT NULL CHECK(role IN ('platform_admin','org_admin','presenter','moderator')),created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS sessions(id uuid PRIMARY KEY,organization_id uuid NOT NULL REFERENCES organizations(id),owner_id uuid NOT NULL REFERENCES users(id),title text NOT NULL,join_code text UNIQUE NOT NULL,join_secret text UNIQUE NOT NULL,status text NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','ready','active','paused','closed')),current_activity_id uuid,expires_at timestamptz NOT NULL,created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS activities(id uuid PRIMARY KEY,session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,type text NOT NULL CHECK(type IN ('poll','quiz')),title text NOT NULL,options jsonb NOT NULL,correct_option_id text,duration_seconds integer,opened_at timestamptz,status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','open','closed')),position integer NOT NULL,UNIQUE(session_id,position));
CREATE TABLE IF NOT EXISTS participants(id uuid PRIMARY KEY,session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,token_hash text NOT NULL UNIQUE,created_at timestamptz NOT NULL DEFAULT now(),UNIQUE(id,session_id));
CREATE TABLE IF NOT EXISTS responses(id uuid PRIMARY KEY,activity_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,participant_id uuid NOT NULL REFERENCES participants(id) ON DELETE CASCADE,option_id text NOT NULL,correct boolean NOT NULL DEFAULT false,submitted_at timestamptz NOT NULL DEFAULT now(),UNIQUE(activity_id,participant_id));
CREATE INDEX IF NOT EXISTS idx_activities_session ON activities(session_id);
CREATE INDEX IF NOT EXISTS idx_responses_activity ON responses(activity_id);
CREATE INDEX IF NOT EXISTS idx_sessions_org ON sessions(organization_id);

-- Additive schema evolution; default retention is 90 days (administrator may select 1-3650).
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS retention_days integer NOT NULL DEFAULT 60;

-- Identity approval, privacy and presentation configuration (additive migrations).
ALTER TABLE users ADD COLUMN IF NOT EXISTS approved boolean NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password boolean NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at timestamptz;
-- Invalidate already issued login cookies following security-sensitive administrative recovery.
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_revoked_at timestamptz;
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK(role IN ('platform_admin','org_admin','presenter','moderator','user'));
UPDATE users SET approved=true WHERE role='platform_admin';
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS allow_anonymous boolean NOT NULL DEFAULT true;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS closed_at timestamptz;
ALTER TABLE sessions ALTER COLUMN retention_days SET DEFAULT 60;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS theme jsonb NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE activities ADD COLUMN IF NOT EXISTS page_design jsonb NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE activities ADD COLUMN IF NOT EXISTS result_design jsonb NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE participants ADD COLUMN IF NOT EXISTS pseudonym text;
ALTER TABLE participants ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES users(id) ON DELETE SET NULL;
CREATE TABLE IF NOT EXISTS platform_settings(key text PRIMARY KEY,value text NOT NULL,updated_at timestamptz NOT NULL DEFAULT now());
INSERT INTO platform_settings(key,value) VALUES('closed_session_retention_days','60') ON CONFLICT DO NOTHING;

ALTER TABLE sessions ADD COLUMN IF NOT EXISTS show_results boolean NOT NULL DEFAULT false;

-- Collaborative authoring, portable definitions and non-destructive response invalidation.
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS reference_date date NOT NULL DEFAULT CURRENT_DATE;
CREATE TABLE IF NOT EXISTS session_presenters(session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,added_at timestamptz NOT NULL DEFAULT now(),PRIMARY KEY(session_id,user_id));
ALTER TABLE activities ADD COLUMN IF NOT EXISTS revision integer NOT NULL DEFAULT 1;
-- Separate compare-and-swap version for editable page layout, independent of live quiz revisions.
ALTER TABLE activities ADD COLUMN IF NOT EXISTS design_revision integer NOT NULL DEFAULT 1;
ALTER TABLE responses ADD COLUMN IF NOT EXISTS invalidated_at timestamptz;
ALTER TABLE responses ADD COLUMN IF NOT EXISTS invalidated_by uuid REFERENCES users(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_session_presenters_user ON session_presenters(user_id);
INSERT INTO platform_settings(key,value) VALUES('max_upload_mb','100') ON CONFLICT DO NOTHING;

-- Private session asset metadata; binary content resides on an explicit persistent volume.
CREATE TABLE IF NOT EXISTS session_assets(
 id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
 uploaded_by uuid REFERENCES users(id) ON DELETE SET NULL,
 mime_type text NOT NULL, byte_size bigint NOT NULL CHECK(byte_size>0),
 sha256 text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_session_assets_session ON session_assets(session_id);

-- Keep invalidated answers for audit but permit one NEW active response after invalidation.
-- The original table constraint must be replaced before creating the partial unique index.
ALTER TABLE responses DROP CONSTRAINT IF EXISTS responses_activity_id_participant_id_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_responses_active_vote ON responses(activity_id,participant_id) WHERE invalidated_at IS NULL;


-- Quiz modes preserve legacy option_id for already-recorded votes.
ALTER TABLE activities ADD COLUMN IF NOT EXISTS answer_mode text NOT NULL DEFAULT 'single' CHECK(answer_mode IN ('single','multiple','text','file'));
ALTER TABLE activities ADD COLUMN IF NOT EXISTS answer_required boolean NOT NULL DEFAULT true;
ALTER TABLE activities ADD COLUMN IF NOT EXISTS correct_option_ids jsonb NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE responses ADD COLUMN IF NOT EXISTS answer_payload jsonb;
CREATE TABLE IF NOT EXISTS page_reactions (
  session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  activity_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
  participant_id uuid NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
  emoji text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(activity_id,participant_id)
);
CREATE INDEX IF NOT EXISTS idx_reactions_session ON page_reactions(session_id);

-- Satisfaction widget (one vote per participant per activity; distinct from quiz answers and emoticons).
CREATE TABLE IF NOT EXISTS page_ratings(
 session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
 activity_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
 participant_id uuid NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
 score integer NOT NULL CHECK(score BETWEEN 0 AND 10),
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(activity_id,participant_id)
);
CREATE INDEX IF NOT EXISTS idx_page_ratings_session ON page_ratings(session_id,activity_id);

-- Interactive audience tools. A participant can contribute one word per page,
-- submit moderated questions and vote once on each approved question.
CREATE TABLE IF NOT EXISTS audience_words (
 session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
 activity_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
 participant_id uuid NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
 word text NOT NULL CHECK(char_length(word) BETWEEN 1 AND 48),
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(activity_id,participant_id)
);
CREATE INDEX IF NOT EXISTS idx_audience_words_session ON audience_words(session_id,activity_id);
CREATE TABLE IF NOT EXISTS audience_questions (
 id uuid PRIMARY KEY,
 session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
 activity_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
 participant_id uuid NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
 body text NOT NULL CHECK(char_length(body) BETWEEN 5 AND 500),
 status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
 created_at timestamptz NOT NULL DEFAULT now(),
 moderated_at timestamptz
);
CREATE INDEX IF NOT EXISTS idx_audience_questions_activity ON audience_questions(activity_id,status);
CREATE TABLE IF NOT EXISTS audience_question_votes (
 question_id uuid NOT NULL REFERENCES audience_questions(id) ON DELETE CASCADE,
 participant_id uuid NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(question_id,participant_id)
);

-- Presenter identity and widget-scoped satisfaction: additive migration for existing databases.
ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name text;
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url text;
ALTER TABLE page_ratings ADD COLUMN IF NOT EXISTS widget_id text NOT NULL DEFAULT 'legacy-rating';
ALTER TABLE page_ratings ADD COLUMN IF NOT EXISTS target_kind text NOT NULL DEFAULT 'question';
ALTER TABLE page_ratings ADD COLUMN IF NOT EXISTS target_id uuid;
ALTER TABLE page_ratings DROP CONSTRAINT IF EXISTS page_ratings_pkey;
ALTER TABLE page_ratings ADD PRIMARY KEY(activity_id,participant_id,widget_id);
CREATE INDEX IF NOT EXISTS idx_ratings_target ON page_ratings(session_id,target_kind,target_id,widget_id);

-- Rich widget configuration is stored in activities.page_design JSONB; no extra SQL migration is required.

ALTER TABLE page_ratings ADD COLUMN IF NOT EXISTS comment_text text;

-- Independent question widgets: one confirmed answer per participant and widget.
CREATE TABLE IF NOT EXISTS widget_answers (
 id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
 activity_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
 participant_id uuid NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
 widget_id text NOT NULL, answer_mode text NOT NULL CHECK(answer_mode IN ('single','multiple','text','file')),
 answer_payload jsonb NOT NULL, submitted_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(activity_id,participant_id,widget_id)
);
CREATE INDEX IF NOT EXISTS idx_widget_answers_stats ON widget_answers(session_id,activity_id,widget_id);

-- Widget definition revisions preserve interpretations of live answers.
CREATE TABLE IF NOT EXISTS widget_revisions (
 activity_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
 widget_id text NOT NULL,
 revision integer NOT NULL CHECK (revision >= 1),
 definition jsonb NOT NULL,
 changed_by uuid REFERENCES users(id) ON DELETE SET NULL,
 changed_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(activity_id,widget_id,revision)
);
ALTER TABLE widget_answers ADD COLUMN IF NOT EXISTS revision integer NOT NULL DEFAULT 1;
ALTER TABLE widget_answers DROP CONSTRAINT IF EXISTS widget_answers_activity_id_participant_id_widget_id_key;
CREATE UNIQUE INDEX IF NOT EXISTS widget_answers_one_per_revision ON widget_answers(activity_id,participant_id,widget_id,revision);
CREATE INDEX IF NOT EXISTS widget_answers_revision_stats ON widget_answers(session_id,activity_id,widget_id,revision);
-- Timed widget results are independent per widget and definition revision.
ALTER TABLE widget_answers ADD COLUMN IF NOT EXISTS correct boolean;
ALTER TABLE widget_answers ADD COLUMN IF NOT EXISTS elapsed_ms bigint;
CREATE INDEX IF NOT EXISTS idx_widget_timed_ranking ON widget_answers(activity_id,widget_id,revision,elapsed_ms) WHERE correct=true;

-- Preserve ownership of anonymous uploads; presenter assets keep a NULL participant_id.
ALTER TABLE session_assets ADD COLUMN IF NOT EXISTS participant_id uuid REFERENCES participants(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_session_assets_participant ON session_assets(session_id,participant_id);

-- Safe integrated image-slide presentation pages (no historical answer mutation).
ALTER TABLE activities DROP CONSTRAINT IF EXISTS activities_type_check;
ALTER TABLE activities ADD CONSTRAINT activities_type_check CHECK(type IN ('poll','quiz','slide','timed_quiz'));
CREATE TABLE IF NOT EXISTS presentation_slide_assets(
 activity_id uuid PRIMARY KEY REFERENCES activities(id) ON DELETE CASCADE,
 asset_id uuid NOT NULL REFERENCES session_assets(id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_presentation_slide_asset ON presentation_slide_assets(asset_id);

-- Optional authenticator-based second factor; secrets encrypted using AUTH_SECRET-derived key.
ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_enabled boolean NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_secret text;
ALTER TABLE users ADD COLUMN IF NOT EXISTS totp_pending_secret text;

-- One-use, short-lived password reset links: never store the bearer token itself.
CREATE TABLE IF NOT EXISTS password_reset_tokens (
 id bigserial PRIMARY KEY,
 user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 token_hash text NOT NULL UNIQUE,
 expires_at timestamptz NOT NULL,
 used_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS password_reset_user_idx ON password_reset_tokens(user_id,expires_at);

-- One-time MFA recovery codes, keyed hashes only; consumed atomically on login.
CREATE TABLE IF NOT EXISTS mfa_recovery_codes (user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE, code_hash text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (user_id,code_hash));

-- OIDC subject binding; email never grants an automatic identity link.
CREATE TABLE IF NOT EXISTS oidc_identities(provider text NOT NULL,subject text NOT NULL,user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,linked_at timestamptz NOT NULL DEFAULT now(),PRIMARY KEY(provider,subject),UNIQUE(provider,user_id));

-- Cross-replica, single-use OAuth authorization state and global API rate limits.
CREATE TABLE IF NOT EXISTS auth_flows(
 state_hash text PRIMARY KEY,
 kind text NOT NULL CHECK(kind IN ('oidc','social')),
 provider text NOT NULL,
 nonce text,
 verifier text,
 link_user uuid REFERENCES users(id) ON DELETE CASCADE,
 expires_at timestamptz NOT NULL
);
CREATE INDEX IF NOT EXISTS auth_flows_expiry ON auth_flows(expires_at);
CREATE TABLE IF NOT EXISTS api_rate_windows(
 client_hash text NOT NULL,
 bucket bigint NOT NULL,
 hits integer NOT NULL CHECK(hits>0),
 PRIMARY KEY(client_hash,bucket)
);
CREATE INDEX IF NOT EXISTS api_rate_windows_expiry ON api_rate_windows(bucket);

-- Stable platform identity and optional unique nickname. Existing installations receive
-- a deterministic bootstrap owner only after role and email have been verified.
ALTER TABLE users ADD COLUMN IF NOT EXISTS nickname text;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_primary_admin boolean NOT NULL DEFAULT false;
CREATE UNIQUE INDEX IF NOT EXISTS users_nickname_unique ON users(lower(nickname)) WHERE nickname IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS users_one_primary_admin ON users(is_primary_admin) WHERE is_primary_admin=true;
CREATE TABLE IF NOT EXISTS session_schedule_dates(session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,scheduled_date date NOT NULL,PRIMARY KEY(session_id,scheduled_date));

-- SMTP credentials encrypted using AUTH_SECRET, never returned by API.
CREATE TABLE IF NOT EXISTS smtp_configuration(id integer PRIMARY KEY CHECK(id=1), encrypted_config text NOT NULL, updated_at timestamptz NOT NULL DEFAULT now());

-- Scheduled appointments with explicit local wall-clock time, duration and IANA timezone.
CREATE TABLE IF NOT EXISTS session_appointments(id uuid PRIMARY KEY,session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,scheduled_date date NOT NULL,start_time time NOT NULL,duration_minutes integer NOT NULL CHECK(duration_minutes BETWEEN 5 AND 1440),time_zone text NOT NULL DEFAULT 'Europe/Rome',created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS session_appointments_user_calendar ON session_appointments(scheduled_date,start_time,session_id);
-- Upgrade check constraints from previously deployed releases.
DO $$ DECLARE constraint_name text; BEGIN
 SELECT c.conname INTO constraint_name FROM pg_constraint c JOIN pg_class t ON c.conrelid=t.oid WHERE t.relname='sessions' AND c.contype='c' AND pg_get_constraintdef(c.oid) LIKE '%status%';
 IF constraint_name IS NOT NULL THEN EXECUTE format('ALTER TABLE sessions DROP CONSTRAINT %I',constraint_name); END IF;
 ALTER TABLE sessions ADD CONSTRAINT sessions_status_valid CHECK (status IN ('draft','ready','active','paused','closed'));
END $$;

-- Topic questions are separate from poll/quiz answers; presenters can display 10 per page.
CREATE TABLE IF NOT EXISTS topic_widget_questions (
 id uuid PRIMARY KEY, session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
 activity_id uuid NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
 widget_id text NOT NULL, participant_id uuid NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
 body text NOT NULL CHECK(char_length(body) BETWEEN 5 AND 2000),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS topic_widget_questions_lookup ON topic_widget_questions(session_id,activity_id,widget_id,created_at);

-- Server-authoritative duration of quiz responses (milliseconds).
ALTER TABLE responses ADD COLUMN IF NOT EXISTS elapsed_ms bigint;
CREATE INDEX IF NOT EXISTS responses_timed_rank ON responses(activity_id,elapsed_ms,submitted_at,id) WHERE correct=true AND invalidated_at IS NULL;

-- Optional email second factor: per-user, single-use, database-backed challenges.
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_mfa_enabled boolean NOT NULL DEFAULT false;
CREATE TABLE IF NOT EXISTS email_mfa_challenges(
 id uuid PRIMARY KEY,user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 digest char(64) NOT NULL,expires_at timestamptz NOT NULL,
 attempts integer NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 5),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_email_mfa_challenges_expiry ON email_mfa_challenges(expires_at);

-- Prevent concurrent logins issuing multiple valid OTP challenges for one account.
-- Existing installations may contain overlapping challenges from earlier concurrent logins.
DELETE FROM email_mfa_challenges a USING email_mfa_challenges b
 WHERE a.user_id=b.user_id AND (a.created_at,a.id)<(b.created_at,b.id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_email_mfa_challenges_user ON email_mfa_challenges(user_id);

-- Prove ownership of the account email before enabling email MFA.
-- Independent of TOTP and of login challenges; one outstanding enrollment per user.
CREATE TABLE IF NOT EXISTS email_mfa_enrollments(
 id uuid PRIMARY KEY,user_id uuid NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
 digest char(64) NOT NULL,expires_at timestamptz NOT NULL,
 attempts integer NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 5),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_email_mfa_enrollments_expiry ON email_mfa_enrollments(expires_at);

CREATE TABLE IF NOT EXISTS live_connections(id uuid PRIMARY KEY,session_id uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,participant_id uuid REFERENCES participants(id) ON DELETE CASCADE,last_seen timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS live_connections_recent_idx ON live_connections(session_id,last_seen);
