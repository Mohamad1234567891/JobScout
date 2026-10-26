"""Central regex library for the job scraping pipeline.

Generic patterns (numbers, tracking parameters, camelCase splitting, anti-bot
block signatures, heavy media and tracker routes, JavaScript state
assignments, junk paths) are carried over from ShopWise's RegexConstants;
job-specific patterns (job URLs, experience/education/certificate mentions)
are new.
"""

import re

# A number with . , ' as separators; a space only counts when exactly 3 digits
# follow ("1 299"). Carried over from ShopWise.
NUMBER_RE = re.compile(r"\d+(?:(?:[.,'’]| (?=\d{3}(?!\d)))\d+)*")

# Marketing/analytics query parameters to strip from URLs.
TRACKING_PARAM_RE = re.compile(
    r"^(utm_.*|gclid|fbclid|msclkid|yclid|gbraid|wbraid|_ga|_gl|srsltid|spm|scm|ref|ref_|"
    r"qid|sr|keywords|crid|sprefix|_pos|_sid|_ss|_psq)$", re.I)

# Splits camelCase class names into words.
CAMEL_RE = re.compile(r"([a-z])([A-Z])")

# Anti-bot block page signatures (Cloudflare, Akamai, DataDome, PerimeterX...).
BLOCK_RE = re.compile(
    r"<title>\s*(?:Just a moment|Attention Required|Access Denied|Robot Check|Pardon Our Interruption|Security Check|"
    r"Erişim Engellendi|Bot Verification|Are you a robot|Request Rejected)|cf-browser-verification|cf_chl_opt|"
    r"/_sec/cp_challenge|px-captcha|captcha-delivery\.com|_Incapsula_Resource|Request unsuccessful\. Incapsula|"
    r"/errors/validateCaptcha", re.I)

# Heavy media resources the browser never needs to download.
HEAVY_RE = re.compile(r"^[^?#]*\.(?:png|jpe?g|gif|webp|avif|svg|ico|bmp|woff2?|ttf|otf|eot|mp4|webm|mp3)(?:[?#]|$)",
                      re.I)

# Analytics and ad trackers, matched on the host name only.
TRACKER_RE = re.compile(
    r"^https?://[^/?#]*(?:google-analytics\.com|googletagmanager\.com|doubleclick\.net|facebook\.net|"
    r"hotjar|criteo|segment\.(?:io|com)|clarity\.ms|tiktok|snapchat|bat\.bing\.com|newrelic|"
    r"nr-data\.net|mc\.yandex|googlesyndication\.com|googleadservices\.com|amazon-adsystem\.com|"
    r"adnxs\.com|taboola\.com|outbrain\.com|scorecardresearch\.com)[^/?#]*(?:[/?#]|$)", re.I)

# JavaScript `= {` / `= [` state assignments inside script blocks.
ASSIGN_RE = re.compile(r"=\s*[\[{]")

# Variable name before an assignment (for embedded frontend state detection).
VARIABLE_BEFORE_RE = re.compile(r"([A-Za-z_$][\w$.]*)\s*$")

# State container names that hold embedded page data.
STATE_NAME_RE = re.compile(r"state|data|props|store|job|listing|search|initial|preload|apollo|redux|"
                           r"context|result|items|included|posting", re.I)

# Navigation/junk paths that are never job pages.
JUNK_PATH_RE = re.compile(r"/(?:login|signin|sign-in|register|signup|join|guest|apply|jobs/search|"
                          r"jobs/saved|jobs/collections|jobs/alerts|notifications|feed|messaging|"
                          r"help|learning|premium|sales|talent|advertising|marketing|"
                          r"cookie|privacy|legal|about|press|careers)(?:[/?#.]|$)", re.I)

# Auto-generated hash-like class tokens.
HASH_RE = re.compile(r"^(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{5,}$")

# ---------------------------------------------------------------------------
# Job-specific patterns
# ---------------------------------------------------------------------------

# LinkedIn job page URL: /jobs/view/<slug>-<numeric id>[/...]
JOB_URL_RE = re.compile(r"/jobs/view/(?P<slug>[^/?#\s]+?)-(?P<id>\d{5,})(?:/|[?#]|$)", re.I)

# Numeric job id inside urn:li:jobPosting:<id> entities.
JOB_URN_RE = re.compile(r"urn:li:job(?:Posting|posting):(?P<id>\d{5,})", re.I)

# "X years of experience" / "X+ years" / "X-Y years" (also "yrs"). When the
# "of ... experience" tail exists it is captured loosely (up to four words),
# so "6+ years of professional software development experience" survives
# whole; a bare "3+ years" matches too and is filtered later by context.
YEARS_EXPERIENCE_RE = re.compile(
    r"\b(?P<years>\d{1,2}(?:\s*[-+–]\s*\d{1,2})?)\+?\s*(?:years?|yrs?)\b"
    r"(?:\s+of\s+(?:\w[\w./-]*(?:\s+\w[\w./-]*){0,4})?\s*experience)?",
    re.I)

# "at least X years", "minimum of X years", "preferred X years".
EXPERIENCE_LEAD_RE = re.compile(
    r"\b(?:minimum|at\s+least|min\.?|preferred|ideally|required)\s+"
    r"(?:of\s+)?(?P<years>\d{1,2}\+?)\s*(?:-\s*\d{1,2})?\s*(?:years?|yrs?)\b",
    re.I)

# Explicit "no experience needed" style statements (entry level postings).
NO_EXPERIENCE_RE = re.compile(
    r"\b(?:no|zero)\s+(?:prior\s+|previous\s+|work\s+|professional\s+)?experience\b"
    r"|entry[\s-]level|fresh\s+graduates?|new\s+graduates?|no\s+experience\s+(?:required|needed|necessary)",
    re.I)

# Month-based experience ("6 months of experience", "6+ months").
MONTHS_EXPERIENCE_RE = re.compile(
    r"\b(?P<months>\d{1,2})\+?\s*months?\s+(?:of\s+)?(?:.*?\b)?experience\b|\b(?P<months2>\d{1,2})\+?\s*months?\b"
    r"(?=\s+(?:internship|co-op|coop|work))",
    re.I)

# Education degree mentions (Bachelor's, MSc, PhD, MBA, Associate...). The
# "degree in ..." branch is greedy (up to 80 chars) so "degree in Computer
# Science, Engineering or a related field" is captured whole.
EDUCATION_RE = re.compile(
    r"\b(?:bachelor(?:'s|s)?(?:\s+degree)?(?:\s+\(?b\.?s\.?c?\.?\)?)?|b\.?s\.?c?\.?|b\.?eng\.?|b\.?se\b|"
    r"master(?:'s|s)?(?:\s+degree)?(?:\s+\(?m\.?s\.?c?\.?\)?)?|m\.?s\.?c?\.?|m\.?eng\.?|m\.?se\b|mba|"
    r"ph\.?\s?d\.?|doctorate|doctoral(?:\s+degree)?|"
    r"associate(?:'s|s)?(?:\s+degree)?|undergraduate(?:\s+degree)?|graduate(?:\s+degree)?|"
    r"post[\s-]?graduate|high\s+school\s+(?:diploma|degree)|diploma|"
    r"(?:university|college)\s+degree|degree\s+in\s+[A-Za-z][A-Za-z0-9 ,'/+&-]{0,80}"
    r")\b",
    re.I)

# Certificate mentions: known certificate names/families plus a generic catch.
CERTIFICATE_RE = re.compile(
    r"\b(?:aws\s+(?:certified|certification)|microsoft\s+certified|azure\s+(?:certified|certification)|"
    r"google\s+cloud\s+(?:certified|certification)|gcp\s+(?:certified|certification)|"
    r"(?:pmp|project\s+management\s+professional)|prince2|capm|csm|psm|safe(?:\s+agilist)?|"
    r"cissp|cism|cisa|security\+|comptia(?:\s+\w+\+?)?|\ba\s?\+|network\+|ceh|oscp|casp\+?|"
    r"ccna|ccnp|ccie|jncia|jncis|itil|togaf|cobit|iso\s*27001|soc\s*2|"
    r"ckad|cka|kubernetes\s+(?:administrator|developer)|docker\s+(?:associate|certified)|"
    r"salesforce\s+(?:certified|administrator|developer)|servicenow\s+(?:certified|csa)|"
    r"sap\s+(?:certified|consultant)|oracle\s+(?:certified|ocp|oca)|"
    r"(?:lean\s+)?six\s+sigma(?:\s+\w+\s+belt)?|cfa|cpa|acca|cma|frm|"
    r"vmware|vcp|rhce|rhcsa|linux\+|lpic"
    r")\b",
    re.I)

# Generic "certification in X" / "certified as X" mentions. The connector is
# required so benefit phrases ("we pay for certification programs") do not
# match - named certificates are caught by CERTIFICATE_RE instead.
GENERIC_CERTIFICATE_RE = re.compile(
    r"\b(?:certification|certifications|certificate|certificates|certified)\b"
    r"\s+(?:in|of|as|with|such\s+as|like)\s+(?:[a-z][\w\s,'/+-]{0,40})",
    re.I)

# Percentage values (some postings express "how well you match" in text).
PERCENT_RE = re.compile(r"\b(\d{1,3})\s*%")

# "Posted H:MM:SS AM/PM" found in meta descriptions.
POSTED_META_RE = re.compile(r"Posted\s+(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)")

# "N applicants" counters.
APPLICANTS_RE = re.compile(r"\b(\d{1,3}(?:[.,]\d{3})*|\d+)\s*(?:applicants?|people)\b", re.I)

# LinkedIn og:title shape: "<Company> hiring <Title> in <Location> | LinkedIn".
OG_TITLE_RE = re.compile(r"^(?P<company>.+?)\s+hiring\s+(?P<title>.+?)\s+in\s+(?P<location>.+?)\s*\|\s*LinkedIn\s*$",
                         re.I)

# Page <title> fallback shape: "<Title> - <Company> | LinkedIn".
PAGE_TITLE_RE = re.compile(r"^(?P<title>.+?)\s*[-|]\s*(?P<company>.+?)\s*\|\s*LinkedIn\s*$", re.I)
