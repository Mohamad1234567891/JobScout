"""
This file is part of JobScout, an open-source job-search and job-match
engine that scrapes LinkedIn and scores every posting against your profile.

Copyright (c) 2026 Muhammed Bekiroğlu and the JobScout contributors.

Original JobScout repository: https://github.com/Mohamad1234567891/JobScout

Muhammed Bekiroğlu (JobScout team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
-------------------------------------------------------------------------------------------------------------------------------

Runtime tunables for the job scraping pipeline.

Since
JobScout currently has no CLI/GUI driving these values, they are plain module
constants - the GUI can import and tweak them later.

"""

# ================================================================ SETTINGS
# There is deliberately no job limit - every job found is processed.
HTTP_PER_SITE = 6       # downloads at the same time on one site (6 = what Chrome does)
BROWSER_TABS = 4        # browser tabs running at the same time
REQUEST_TIMEOUT = 20    # seconds per download
JOB_TIME_LIMIT = 30     # seconds allowed for one job page
SCRAPE_TIME_LIMIT = 240  # seconds allowed for the whole scraping session
LOAD_MORE_CLICKS = 3    # "see more jobs" button clicks per listing page
VERBOSE = False         # print every job as JSON while running
##########################################################################
