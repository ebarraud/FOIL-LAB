# FOIL LAB work tracking

When actually starting a transcript analysis or verification session, run:
`python video-analysis/analysis_activity.py VIDEO_ID in_progress --step "Concrete work being performed"`
Publish the activity files and generated progress.json so the public dashboard reflects real activity. Refresh the marker during sustained work; it expires after 20 minutes.

Before ending or interrupting the session, record `completed` or `paused` using the same command and publish the resulting files. Never leave an active marker merely because work is planned. A completed session does not itself mean a validated analysis or a rule integrated into the recommendation engine; those require evidence records and appropriate tests.
