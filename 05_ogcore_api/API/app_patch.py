"""
app_patch.py
------------
Shows exactly what lines to add to MUIOGO's existing API/app.py
to register the OG-Core Blueprint.

DO NOT replace app.py — just add the two lines marked below.

Author: Tejas Singh Bhati
Project: OG-CLEWS Integration — GSoC 2026, UN DESA
"""

# ── ADD THIS IMPORT (after existing Route imports) ────────────────────────────
# Place after:
#   from Routes.DataFile.DataFileRoute import datafile_api

from Routes.OGCore.OGCoreRoute import ogcore_api           # ← ADD THIS


# ── ADD THIS REGISTRATION (after existing Blueprint registrations) ────────────
# Place after:
#   app.register_blueprint(syncs3_api)

app.register_blueprint(ogcore_api)                         # ← ADD THIS


# ── That's it. The following endpoints will now be available: ─────────────────
#
#   POST   /ogcore/run              → trigger an OG-Core run
#   GET    /ogcore/status/<run_id>  → poll run status
#   GET    /ogcore/results/<run_id> → get results for a completed run
#   POST   /ogcore/runs             → list all runs for active case
#   DELETE /ogcore/run/<run_id>     → delete a run