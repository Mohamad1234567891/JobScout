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

Central configuration and semantic word sets used by the job scraping pipeline.

Keeps the region/domain knowledge and the multilingual requirement keyword
sets in one auditable place, mirroring the role a Constants package plays (priorities, second-level domains, semantic words).

"""

# Task priorities inside the slot managers: work already started (job pages)
# goes before opening new listing pages (NOW/NEXT priorities).
NOW, NEXT = 0, 1

# Second-level domain parts used to recognize two-part country domains
# (example.com.tr) so domain extraction always keeps the real site domain.
SECOND_LEVEL = {"co", "com", "net", "org", "gov", "edu", "ac", "or", "ne", "go", "gob", "ltd", "plc"}

# Schema.org types that identify a job posting inside JSON-LD blocks.
JOB_TYPES = {"jobposting", "job"}

# Schema.org keys whose presence marks a JSON-LD node as a job posting.
JOB_HINT_KEYS = {"title", "description", "hiringorganization", "joblocation", "joblocationtype",
                 "dateposted", "employmenttype", "applicantlocationrequirements", "directapply",
                 "baseSalary", "basesalary", "qualifications", "educationrequirements",
                 "experiencerequirements", "skills", "occupationalcategory"}

# Heading words that introduce the requirements block of a job description.
REQUIREMENT_SECTION_WORDS = {
    "qualification", "qualifications", "requirement", "requirements", "what we are looking for",
    "what you need", "what youll need", "what you'll need", "who you are", "about you",
    "your background", "profile", "minimum qualifications", "preferred qualifications",
    "must have", "must-have", "nice to have", "nice-to-have", "experience", "education",
    "skills", "knowledge", "competencies", "what we expect", "what you bring", "ideal candidate",
    "candidate profile", "essential", "selection criteria", "we are looking for", "we're looking for",
    "what you will bring", "successful candidate", "who we are looking for",
}

# Words that mark the start of the "nice to have" (preferred) part of a description.
PREFERRED_SECTION_WORDS = {"preferred", "bonus", "nice to have", "nice-to-have", "plus", "advantageous",
                           "bonus points", "a plus", "would be a plus", "ideally", "good to have",
                           "valued", "desired", "beneficial", "familiarity"}

# Education degree words used to detect what degree an employer asks for.
EDUCATION_WORDS = {
    "bachelor", "bachelors", "bachelor's", "bsc", "b.sc", "b.s.", "bs", "bse", "beng", "b.eng",
    "undergraduate", "undergrad",
    "master", "masters", "master's", "msc", "m.sc", "m.s.", "ms", "mse", "meng", "m.eng", "mba",
    "graduate degree", "postgraduate", "post-graduate",
    "phd", "ph.d", "ph.d.", "doctorate", "doctoral", "doctor of philosophy",
    "associate", "associate's", "associates",
    "high school", "diploma", "ged", "btec", "hnd", "hnc",
    "university degree", "degree in", "college degree", "tertiary education", "bachelor degree",
    "master degree", "engineering degree", "computer science degree", "cs degree",
}

# Certificate names and certification families an employer might require.
CERTIFICATE_WORDS = {
    "aws certified", "aws certification", "azure", "microsoft certified", "mcsa", "mcse", "mcp",
    "google cloud", "gcp", "professional cloud", "associate cloud",
    "pmp", "project management professional", "prince2", "capm", "scrum", "csm", "psm", "safe",
    "agile", "pmi-acp",
    "cissp", "cism", "cisa", "security+", "security plus", "comptia", "a+", "network+", "ceh",
    "oscp", "casp",
    "ccna", "ccnp", "ccie", "juniper", "jncia",
    "itil", "togaf", "cobit", "iso 27001", "soc 2",
    "ckad", "cka", "cna", "kubernetes", "docker",
    "salesforce", "servicenow", "sap", "oracle certified", "ocp", "oca",
    "six sigma", "lean six sigma", "cfa", "cpa", "acca", "cma", "frm",
    "cisco", "vmware", "vcp", "rhce", "rhcsa", "linux+", "lpic",
}

# Common skill keywords detected in descriptions (small, expandable set).
SKILL_WORDS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang", "rust", "sql",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "react", "angular", "vue",
    "node.js", "nodejs", "django", "flask", "spring", "machine learning", "deep learning",
    "llm", "nlp", "computer vision", "pytorch", "tensorflow", "pandas", "spark", "kafka",
    "git", "ci/cd", "linux", "excel", "power bi", "tableau", "scrum", "agile",
}

# Employment type words for detecting full/part time mentions in text.
EMPLOYMENT_TYPE_WORDS = {
    "full-time", "full time", "part-time", "part time", "contract", "temporary", "internship",
    "intern", "freelance", "remote", "hybrid", "on-site", "onsite", "permanent", "co-op", "coop",
}

# Seniority words for detecting the level asked in the title or criteria.
SENIORITY_WORDS = {
    "intern", "internship", "junior", "entry level", "entry-level", "associate", "mid-level",
    "mid level", "mid-senior", "senior", "sr", "lead", "principal", "staff", "manager",
    "director", "vp", "head of", "chief", "cto", "executive", "graduate", "new grad",
}

# Words that usually appear in the "about the company" or boilerplate part of
# a posting (used only for section splitting, kept light on purpose).
BOILERPLATE_SECTION_WORDS = {
    "about us", "about the company", "who we are", "our company", "equal opportunity",
    "diversity", "inclusion", "we offer", "benefits", "perks", "why join",
    "about the team", "our culture", "life at", "what we offer",
}

# Class/id attribute hints used to read an element's semantics.
HINT_ATTRIBUTES = ("class", "id", "itemprop", "data-testid", "data-test-id", "data-test", "data-qa",
                   "data-hook", "data-automation-id", "data-cy", "data-component", "aria-label", "role")

# Tags that never hold content worth reading.
INVISIBLE_TAGS = {"script", "style", "noscript", "template", "svg", "head", "title"}

# URL keys found inside embedded JSON job objects.
URL_KEYS = ("url", "joburl", "job_url", "jobpostingurl", "job_posting_url", "link", "href", "pdpurl",
            "seourl", "permalink", "uri", "weburl", "path", "trackingurl", "companyjobpostingurl")

# Title keys found inside embedded JSON job objects.
NAME_KEYS = ("name", "title", "jobtitle", "job_title", "position", "headline", "displayname")

# Company keys found inside embedded JSON job objects.
COMPANY_KEYS = ("company", "companyname", "company_name", "hiringcompany", "organization",
                "disambiguatingdescription")

# Location keys found inside embedded JSON job objects.
LOCATION_KEYS = ("location", "joblocation", "formattedlocation", "formatted_location", "city",
                 "workplace", "description")
