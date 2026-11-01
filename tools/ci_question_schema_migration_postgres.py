#!/usr/bin/env python3
"""Transactional schema-upgrade smoke on the real ephemeral CI PostgreSQL 18.

Construct a legacy widget_answers shadow table in a temporary schema, reuse the
actual migration clauses from schema.sql, assert that old records remain intact
and new subquestions gain separate uniqueness. Entire transaction rolls back.
"""
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]

def migration_script():
    schema=(ROOT/'apps/api/src/schema.sql').read_text()
    lines=[]
    for statement in (
        "ALTER TABLE widget_answers DROP CONSTRAINT IF EXISTS widget_answers_activity_id_participant_id_widget_id_key;",
        "ALTER TABLE widget_answers ADD COLUMN IF NOT EXISTS question_id text NOT NULL DEFAULT '';",
        "DROP INDEX IF EXISTS widget_answers_one_per_revision;",
        "CREATE UNIQUE INDEX IF NOT EXISTS widget_answers_one_per_question_revision ON widget_answers(activity_id,participant_id,widget_id,question_id,revision);",
    ):
        if statement not in schema:raise AssertionError('Migration missing a required historic step')
        lines.append(statement)
    return '\n'.join(lines)

def run():
    url=os.environ.get('DATABASE_URL','')
    parsed=urlsplit(url)
    if os.environ.get('QUORIVIO_CI_MULTI_QUESTION_TEST')!='1' or parsed.hostname not in ('localhost','127.0.0.1') or not parsed.port:
        raise RuntimeError('Refusing migration test outside disposable loopback PostgreSQL')
    sql='''BEGIN;
SET LOCAL search_path=pg_temp;
CREATE TEMP TABLE widget_answers (
 id uuid PRIMARY KEY,activity_id uuid NOT NULL,participant_id uuid NOT NULL,
 widget_id text NOT NULL,revision integer NOT NULL DEFAULT 1,
 answer_payload jsonb NOT NULL,
 UNIQUE(activity_id,participant_id,widget_id)
);
INSERT INTO widget_answers(id,activity_id,participant_id,widget_id,answer_payload)
VALUES('00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002',
'00000000-0000-0000-0000-000000000003','survey','{"optionIds":["a"]}');
'''+migration_script()+'''
DO $$ BEGIN
 IF (SELECT count(*) FROM widget_answers WHERE question_id='')<>1 THEN RAISE EXCEPTION 'legacy answer lost'; END IF;
END $$;
INSERT INTO widget_answers(id,activity_id,participant_id,widget_id,question_id,answer_payload)
VALUES('00000000-0000-0000-0000-000000000004','00000000-0000-0000-0000-000000000002',
'00000000-0000-0000-0000-000000000003','survey','sub1','{"optionIds":["b"]}');
DO $$ BEGIN
 IF (SELECT count(*) FROM widget_answers)<>2 THEN RAISE EXCEPTION 'independent response not persisted'; END IF;
END $$;
DO $$ BEGIN
 BEGIN
  INSERT INTO widget_answers(id,activity_id,participant_id,widget_id,question_id,answer_payload)
  VALUES('00000000-0000-0000-0000-000000000005','00000000-0000-0000-0000-000000000002',
  '00000000-0000-0000-0000-000000000003','survey','sub1','{}');
  RAISE EXCEPTION 'duplicate independent answer accepted';
 EXCEPTION WHEN unique_violation THEN NULL;
 END;
END $$;
ROLLBACK;
'''
    output=subprocess.run(['psql',url,'-X','-v','ON_ERROR_STOP=1','-q'],input=sql,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    if output.returncode:raise RuntimeError('PostgreSQL schema migration failed: '+output.stderr[-2000:])
    print('PASS PostgreSQL 18 legacy answer migration: historical IDs, independent uniqueness and rollback')

if __name__=='__main__':run()
