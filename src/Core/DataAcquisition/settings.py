"""Runtime tunables for the job scraping pipeline.

Adapted from ShopWise's Settings module with standard Python naming. Since
JobScout currently has no CLI/GUI driving these values, they are plain module
constants - the GUI can import and tweak them later.
"""

# ================================================================ SETTINGS
MAX_JOBS = 25           # job pages processed per search (None = every job found)
HTTP_PER_SITE = 6       # downloads at the same time on one site (6 = what Chrome does)
BROWSER_TABS = 4        # browser tabs running at the same time
REQUEST_TIMEOUT = 20    # seconds per download
JOB_TIME_LIMIT = 30     # seconds allowed for one job page
SCRAPE_TIME_LIMIT = 240  # seconds allowed for the whole scraping session
LOAD_MORE_CLICKS = 3    # "see more jobs" button clicks per listing page
VERBOSE = False         # print every job as JSON while running
##########################################################################
