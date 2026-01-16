#!/usr/bin/env bash
#
# Backfill mhr_registrations.summary_snapshot from mhr_account_reg_vw.
# Skip registrations with duplicate notes, which cause subqueries in the view
# to fail with:
#   "more than one row returned by a subquery used as an expression".

set -u

read -s -p "Postgres password: " PGPASSWORD
echo
export PGPASSWORD

# Update (host, port, database, user) if needed 
PSQL="psql -v ON_ERROR_STOP=1 -h localhost -p 5432 -d ppr -U postgres -At"

total=0
iter=0

trap 'unset PGPASSWORD' EXIT

while true; do
  iter=$((iter+1))
  start=$(date +%s)

  out="$($PSQL -c "
WITH skipped_candidates AS (
  SELECT registration_id
  FROM mhr_notes
  GROUP BY registration_id
  HAVING COUNT(*) > 1
),
batch AS (
  SELECT r.id
  FROM mhr_registrations r
  WHERE r.summary_snapshot IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM skipped_candidates sc WHERE sc.registration_id = r.id
  )
  ORDER BY r.id DESC
  LIMIT 2000
),
snaps AS (
  SELECT b.id, to_jsonb(v) AS payload
  FROM batch b
  JOIN mhr_account_reg_vw v ON v.registration_id = b.id
)
UPDATE mhr_registrations r
SET summary_snapshot = s.payload
FROM snaps s
WHERE r.id = s.id
RETURNING r.id;
" )"
  rc=$?

  end=$(date +%s)
  elapsed=$((end - start))

  if [ $rc -ne 0 ]; then
    echo "$(date '+%F %T') | iter=$iter | ERROR (unexpected): batch_time=${elapsed}s"
    echo "$out"
    break
  fi

  rows=$(printf "%s" "$out" | wc -l | tr -d ' ')
  total=$((total + rows))
  echo "$(date '+%F %T') | iter=$iter | updated=$rows | batch_time=${elapsed}s | total=$total"

  [ "$rows" -eq 0 ] && break
done
