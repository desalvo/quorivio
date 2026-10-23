# Session dates — consolidated editor

The session dashboard uses one primary schedule editor: date, local start time, duration in minutes, and explicit IANA time zone. The backend continues to store the existing `session_appointments` records; no migration or API changes are required.

Dates without times saved through the older schedule API are not deleted. If present, a collapsed import section lets the presenter copy them into the new editable list, applying the currently entered local time, duration and zone. The presenter must save to persist. Duplicate entries with identical date/time/zone are ignored when added. All date entries appear in chronological date/start-time order. Existing old API endpoints remain available for compatibility.

Local verification: Python suite 121 passed, Node suite 107 passed. These are mostly unit/static contracts and are not equivalent to live Kubernetes acceptance. UI and timezone DST transition behavior require browser/real database checks. Full production build remains unverified because the npm dependencies are unavailable in this environment. RC 37.5% unchanged.

Acceptance in Kubernetes: create two dates at different times and zones; save; refresh; inspect global calendar day/week/month; import a preexisting legacy date; save and reload; verify no duplicates; check timezone and DST date boundary as applicable; verify old sessions are unaffected.
