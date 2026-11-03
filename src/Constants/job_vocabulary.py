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

Vocabulary for the requirement understanding engine.

Large curated word/phrase sets used to recognize skills, certificates,
degrees, fields of study, languages and soft skills inside job description
text. Everything is lowercase so callers can match against lowercased text.

"""

# ---------------------------------------------------------------------------
# Skills: technical + domain + tooling keywords. Multi-word entries are
# matched as phrases, so keep them canonical ("machine learning" not "ml").
# ---------------------------------------------------------------------------
SKILLS = {
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "bash", "shell scripting",
    "powershell", "dart", "lua", "haskell", "elixir", "clojure", "groovy", "objective-c", "sql",
    "t-sql", "pl/sql", "nosql", "html", "css", "sass", "assembly",
    # Web / app frameworks
    "react", "react native", "angular", "vue", "vue.js", "svelte", "next.js", "nuxt", "django",
    "flask", "fastapi", "spring", "spring boot", "node.js", "express", "rails", "laravel",
    "asp.net", "flask", "graphql", "rest", "restful apis", "microservices", "grpc", "websockets",
    "flutter", "xamarin", "electron",
    # Data & ML
    "machine learning", "deep learning", "reinforcement learning", "supervised learning",
    "unsupervised learning", "neural networks", "convolutional neural networks", "cnn", "rnn",
    "lstm", "transformers", "llm", "llms", "large language models", "generative ai", "genai",
    "nlp", "natural language processing", "computer vision", "ocr", "speech recognition",
    "recommender systems", "ranking", "search", "information retrieval", "rag",
    "retrieval-augmented generation", "retrieval augmented generation", "fine-tuning", "prompt engineering",
    "feature engineering", "model deployment", "mlops", "model serving", "model training",
    "model evaluation", "a/b testing", "ab testing", "experimentation", "time series",
    "forecasting", "anomaly detection", "clustering", "classification", "regression",
    "bayesian methods", "causal inference", "optimization", "statistical modeling",
    "statistics", "probability", "linear algebra", "calculus", "discrete mathematics",
    "data science", "data analysis", "data engineering", "data pipelines", "etl", "elt",
    "data warehousing", "data modeling", "data visualization", "data mining", "data governance",
    "data quality", "feature store", "vector databases", "embeddings", "graph neural networks",
    "computer science", "algorithms", "data structures", "distributed systems",
    "distributed computing", "parallel computing", "high performance computing",
    # ML libraries / tools
    "pytorch", "tensorflow", "keras", "jax", "scikit-learn", "sklearn", "xgboost", "lightgbm",
    "catboost", "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly", "nltk", "spacy",
    "hugging face", "langchain", "llamaindex", "openai", "anthropic", "llama", "gpt",
    "onnx", "mlflow", "wandb", "weights & biases", "dvc", "kubeflow", "airflow", "dbt",
    "ray", "horovod", "cuda", "triton",
    # Data stores / infra
    "postgresql", "postgres", "mysql", "sqlite", "sql server", "oracle", "mariadb", "mongodb",
    "cassandra", "dynamodb", "redis", "elasticsearch", "opensearch", "solr", "kafka", "rabbitmq",
    "sqs", "sns", "spark", "pyspark", "databricks", "hadoop", "hive", "snowflake", "bigquery",
    "redshift", "s3", "presto", "trino", "flink", "beam", "delta lake", "iceberg", "neo4j",
    "graph databases", "timescaledb", "clickhouse", "druid", "pinot", "memcached",
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "google cloud platform",
    "cloud", "cloud computing", "serverless", "lambda", "ec2", "ecs", "eks", "cloudformation",
    "docker", "kubernetes", "k8s", "helm", "terraform", "pulumi", "ansible", "chef", "puppet",
    "jenkins", "github actions", "gitlab ci", "circleci", "ci/cd", "continuous integration",
    "continuous delivery", "devops", "git", "github", "gitlab", "bitbucket", "linux", "unix",
    "windows server", "nginx", "apache", "istio", "service mesh", "prometheus", "grafana",
    "datadog", "elk stack", "logstash", "kibana", "vault", "consul", "packer", "vagrant",
    # Security
    "cybersecurity", "security", "information security", "application security", "penetration testing",
    "threat modeling", "encryption", "cryptography", "identity and access management", "iam",
    "siem", "soc", "zero trust", "owasp", "firewalls", "vpn", "authentication", "oauth", "saml",
    # Analytics / BI / business
    "excel", "power bi", "tableau", "looker", "qlik", "google analytics", "sql analytics",
    "business intelligence", "bi", "metrics", "kpis", "dashboarding", "spreadsheets",
    "financial modeling", "budgeting", "forecasting", "market research", "seo", "sem",
    "digital marketing", "content marketing", "product management", "project management",
    "program management", "agile", "scrum", "kanban", "lean", "six sigma", "jira", "confluence",
    "asana", "trello", "crm", "salesforce", "hubspot", "erp", "sap", "servicenow", "workday",
    # Domains
    "fintech", "e-commerce", "healthcare", "biotech", "pharma", "insurance", "banking",
    "payments", "telecom", "automotive", "manufacturing", "logistics", "supply chain",
    "retail", "media", "gaming", "robotics", "iot", "embedded systems", "blockchain",
    "cryptocurrency", "quantitative finance", "algorithmic trading", "risk management",
    "compliance", "audit", "legal", "tax", "accounting", "human resources", "recruiting",
    # Soft / professional
    "communication", "written communication", "verbal communication", "presentation",
    "leadership", "teamwork", "collaboration", "problem solving", "problem-solving",
    "analytical skills", "critical thinking", "attention to detail", "organization",
    "time management", "adaptability", "flexibility", "creativity", "initiative",
    "self-motivation", "interpersonal skills", "stakeholder management", "negotiation",
    "mentoring", "coaching", "ownership", "accountability", "decision-making", "prioritization",
    "multitasking", "customer service", "conflict resolution", "emotional intelligence",
    "resilience", "curiosity", "growth mindset", "documentation", "technical writing",
    "public speaking", "facilitation", "cross-functional collaboration", "strategic thinking",
    "business acumen", "sales", "account management", "consulting", "research",
    # Software craft
    "programming", "software development", "software engineering", "software development lifecycle",
    "sdlc", "testing", "unit testing", "integration testing", "end-to-end testing", "test automation",
    "tdd", "bdd", "code review", "code reviews", "refactoring", "debugging",
    "performance optimization", "system design", "architecture", "software architecture",
    "database design", "api design", "api development", "rest api", "version control",
    "code quality", "pair programming", "open source", "technical leadership", "tech lead",
    "people management", "hiring", "interviewing", "user experience", "ux", "developer experience",
    "product design", "prototyping", "wireframing",
    # Operations / reliability
    "sre", "site reliability", "reliability", "capacity planning", "incident management",
    "postmortems", "monitoring", "observability", "logging", "alerting", "load balancing",
    "networking", "dns", "scaling", "high availability", "fault tolerance", "caching",
    "streaming", "batch processing", "data ingestion", "data transformation", "data storage",
    "devsecops", "infrastructure as code", "cloud infrastructure",
    # Modern AI
    "ml engineering", "ai engineering", "prompt design", "ai agents", "agentic workflows",
    "vector search", "semantic search", "knowledge graphs", "graphrag", "synthetic data",
    "data labeling", "data annotation", "model monitoring", "model drift", "bias mitigation",
    "fairness", "explainability", "interpretability", "responsible ai", "ai safety",
    "ai ethics", "governance", "regulatory compliance", "data privacy", "gdpr compliance",
}

# Canonical names for common aliases (alias -> canonical).
SKILL_ALIASES = {
    "ml": "machine learning", "ai": "artificial intelligence", "k8s": "kubernetes",
    "node": "node.js", "nodejs": "node.js", "next": "next.js", "gen ai": "generative ai",
    "cloud services": "cloud computing", "ci cd": "ci/cd", "js": "javascript", "ts": "typescript",
    "py": "python", "db": "databases", "databases": "databases",
}

# ---------------------------------------------------------------------------
# Certificates and certification families.
# ---------------------------------------------------------------------------
CERTIFICATES = {
    # Cloud
    "aws certified", "aws certification", "aws certified solutions architect",
    "aws certified developer", "aws certified sysops administrator", "aws certified devops engineer",
    "aws certified machine learning", "aws certified data analytics", "aws certified security",
    "aws certified cloud practitioner", "aws certified ai practitioner",
    "azure fundamentals", "azure administrator", "azure developer", "azure ai engineer",
    "azure data scientist", "azure data engineer", "azure solutions architect", "azure security engineer",
    "azure devops engineer", "az-900", "az-104", "az-204", "az-305", "ai-900", "ai-102",
    "dp-100", "dp-203", "dp-900", "az-500", "pl-300",
    "google cloud", "gcp certification", "associate cloud engineer", "professional cloud architect",
    "professional data engineer", "professional machine learning engineer", "professional cloud developer",
    "professional cloud devops engineer", "professional cloud security engineer", "professional cloud network engineer",
    "cloud digital leader",
    # Project / agile / ITSM
    "pmp", "project management professional", "prince2", "capm", "pmi-acp",
    "certified scrum master", "csm", "psm", "psm i", "psm ii", "professional scrum master",
    "scrum product owner", "cspo", "pspo", "safe", "safe agilist", "safe scrum master",
    "itil", "itil 4", "itil foundation", "togaf", "cobit", "iso 27001", "iso 9001", "soc 2",
    "istqb", "scaled agile",
    # Security
    "cissp", "cism", "cisa", "crisc", "security+", "network+", "a+", "cybersecurity analyst",
    "cysa+", "casp+", "pen test", "pentest+", "ceh", "certified ethical hacker", "oscp",
    "offensive security", "giac", "gcih", "gsec", "ccsp", "sscp", "ccnp security", "ccie security",
    # Networking / systems
    "ccna", "ccnp", "ccie", "juniper", "jncia", "jncis", "network+", "comptia",
    "rhce", "rhcsa", "linux+", "lpic", "vmware", "vcp", "vcsa", "citrix", "f5", "palos",
    # Cloud-native / DevOps
    "cka", "ckad", "cks", "certified kubernetes administrator", "certified kubernetes application developer",
    "kubernetes certification", "docker certified associate", "docker dca",
    "terraform associate", "hashicorp certified", "hashicorp vault associate",
    "linux foundation certified", "lfcs", "lfce",
    # Data / analytics
    "databricks certified", "databricks associate", "databricks professional",
    "snowflake snowpro", "snowpro core", "snowflake certification",
    "tableau desktop specialist", "tableau certified", "power bi certification", "power bi data analyst",
    "cloudera", "hdpca", "cdp",
    # Vendor / enterprise
    "salesforce certified", "salesforce administrator", "salesforce developer", "salesforce architect",
    "servicenow certified", "servicenow csa", "servicenow cad",
    "sap certified", "sap consultant", "oracle certified", "ocp", "oca", "oracle cloud",
    "microsoft certified", "mcsa", "mcse", "mcp", "mct",
    # Quality / process / business
    "six sigma", "lean six sigma", "six sigma green belt", "six sigma black belt",
    "six sigma yellow belt", "lean",
    "cfa", "cpa", "acca", "cma", "frm", "cfa charter", "chartered financial analyst",
    "series 7", "series 63", "finra",
    "cpsm", "apics", "cpim", "cscp", "pmp certification", "green belt", "black belt",
    # Health / safety / other
    "hipaa", "gdpr", "pci dss", "nist",
}

# Generic words that should NOT become certificate names on their own.
NOT_A_CERTIFICATE = {"relevant", "industry", "professional", "appropriate", "additional", "current",
                     "valid", "active", "recognized", "standard", "required", "nice", "relevant industry",
                     "industry standard", "professional certifications"}

# ---------------------------------------------------------------------------
# Education: degree tokens mapped to their level.
# ---------------------------------------------------------------------------
PHD_DEGREES = ("phd", "ph.d", "ph.d.", "ph d", "doctorate", "doctoral", "doctor of philosophy", "dphil")
MASTER_DEGREES = ("master", "masters", "master's", "msc", "m.sc", "m.sc.", "m.s", "m.s.", "ms", "ma",
                  "m.eng", "meng", "mba", "mphil", "postgraduate", "post-graduate", "graduate degree")
BACHELOR_DEGREES = ("bachelor", "bachelors", "bachelor's", "bsc", "b.sc", "b.sc.", "b.s", "b.s.", "bs",
                    "ba", "b.eng", "beng", "bse", "undergraduate", "undergrad", "college degree")
ASSOCIATE_DEGREES = ("associate", "associate's", "associates", "aas", "a.s.", "as")
HIGH_SCHOOL_DEGREES = ("high school", "high-school", "diploma", "ged", "gcse", "a-level", "a levels",
                       "hnd", "hnc", "btec", "apprenticeship")
OTHER_EDUCATION = ("bootcamp", "coding bootcamp", "nanodegree", "mooc", "certificate program",
                   "continuing education", "professional development", "university degree")

# Degree tokens (lowercase) -> canonical degree name used in output.
DEGREE_NAMES = {
    "phd": "PhD", "ph.d": "PhD", "ph.d.": "PhD", "ph d": "PhD", "doctorate": "Doctorate",
    "doctoral": "Doctoral degree", "doctor of philosophy": "PhD", "dphil": "DPhil",
    "master": "Master's degree", "masters": "Master's degree", "master's": "Master's degree",
    "msc": "MSc", "m.sc": "MSc", "m.sc.": "MSc", "m.s": "MS", "m.s.": "MS", "ms": "MS",
    "ma": "MA", "m.eng": "MEng", "meng": "MEng", "mba": "MBA", "mphil": "MPhil",
    "postgraduate": "Postgraduate degree", "post-graduate": "Postgraduate degree",
    "graduate degree": "Graduate degree",
    "bachelor": "Bachelor's degree", "bachelors": "Bachelor's degree", "bachelor's": "Bachelor's degree",
    "bsc": "BSc", "b.sc": "BSc", "b.sc.": "BSc", "b.s": "BS", "b.s.": "BS", "bs": "BS",
    "ba": "BA", "b.eng": "BEng", "beng": "BEng", "bse": "BSE",
    "undergraduate": "Undergraduate degree", "undergrad": "Undergraduate degree",
    "college degree": "College degree",
    "associate": "Associate's degree", "associate's": "Associate's degree",
    "associates": "Associate's degree", "aas": "AAS", "a.s.": "AS", "as": "AS",
    "high school": "High school diploma", "high-school": "High school diploma",
    "diploma": "Diploma", "ged": "GED", "gcse": "GCSE", "a-level": "A-Levels", "a levels": "A-Levels",
    "hnd": "HND", "hnc": "HNC", "btec": "BTEC", "apprenticeship": "Apprenticeship",
    "bootcamp": "Bootcamp", "coding bootcamp": "Coding bootcamp", "nanodegree": "Nanodegree",
    "mooc": "Online course", "certificate program": "Certificate program",
    "continuing education": "Continuing education", "professional development": "Professional development",
    "university degree": "University degree",
}

# Degree token -> level bucket (used later by the match-scoring module).
DEGREE_LEVELS = {
    "phd": "phd", "ph.d": "phd", "ph.d.": "phd", "ph d": "phd", "doctorate": "phd",
    "doctoral": "phd", "doctor of philosophy": "phd", "dphil": "phd",
    "master": "master", "masters": "master", "master's": "master", "msc": "master",
    "m.sc": "master", "m.sc.": "master", "m.s": "master", "m.s.": "master", "ms": "master",
    "ma": "master", "m.eng": "master", "meng": "master", "mba": "master", "mphil": "master",
    "postgraduate": "master", "post-graduate": "master", "graduate degree": "master",
    "bachelor": "bachelor", "bachelors": "bachelor", "bachelor's": "bachelor", "bsc": "bachelor",
    "b.sc": "bachelor", "b.sc.": "bachelor", "b.s": "bachelor", "b.s.": "bachelor", "bs": "bachelor",
    "ba": "bachelor", "b.eng": "bachelor", "beng": "bachelor", "bse": "bachelor",
    "undergraduate": "bachelor", "undergrad": "bachelor", "college degree": "bachelor",
    "associate": "associate", "associate's": "associate", "associates": "associate",
    "aas": "associate", "a.s.": "associate", "as": "associate",
    "high school": "high_school", "high-school": "high_school", "diploma": "high_school",
    "ged": "high_school", "gcse": "high_school", "a-level": "high_school", "a levels": "high_school",
    "hnd": "high_school", "hnc": "high_school", "btec": "high_school", "apprenticeship": "high_school",
    "bootcamp": "bootcamp", "coding bootcamp": "bootcamp", "nanodegree": "bootcamp",
    "mooc": "bootcamp", "certificate program": "bootcamp", "continuing education": "bootcamp",
    "professional development": "bootcamp", "university degree": "unspecified",
}

# ---------------------------------------------------------------------------
# Fields of study (used to validate/capture the field of a degree mention).
# ---------------------------------------------------------------------------
FIELDS_OF_STUDY = {
    "computer science", "software engineering", "computer engineering", "electrical engineering",
    "information technology", "information systems", "management information systems",
    "data science", "machine learning", "artificial intelligence", "statistics", "mathematics",
    "applied mathematics", "physics", "engineering", "mechanical engineering", "civil engineering",
    "chemical engineering", "industrial engineering", "systems engineering", "aerospace engineering",
    "biomedical engineering", "robotics", "mechatronics", "operations research", "economics",
    "finance", "accounting", "business administration", "business", "marketing", "management",
    "psychology", "cognitive science", "linguistics", "computational linguistics", "bioinformatics",
    "cybersecurity", "information security", "network security", "biology", "chemistry",
    "neuroscience", "design", "human-computer interaction", "ux design", "graphic design",
    "quantitative finance", "actuarial science", "analytics", "business analytics", "health informatics",
    "nursing", "medicine", "law", "communications", "journalism", "education", "philosophy",
    "sociology", "political science", "history", "literature", "environmental science", "geography",
    "geology", "agriculture", "supply chain management", "logistics", "hospitality",
}

# ---------------------------------------------------------------------------
# Languages.
# ---------------------------------------------------------------------------
LANGUAGES = {
    "english", "german", "french", "spanish", "italian", "portuguese", "dutch", "turkish",
    "arabic", "chinese", "mandarin", "cantonese", "japanese", "korean", "russian", "polish",
    "czech", "swedish", "norwegian", "danish", "finnish", "greek", "hebrew", "hindi", "urdu",
    "bengali", "vietnamese", "thai", "indonesian", "malay", "romanian", "hungarian", "ukrainian",
    "persian", "farsi", "swahili", "estonian", "latvian", "lithuanian", "serbian", "croatian",
    "slovak", "slovenian", "bulgarian", "catalan", "welsh", "irish", "icelandic", "afrikaans",
    "kurdish", "azerbaijani", "kazakh", "uzbek", "georgian", "armenian", "mongolian",
}

# ---------------------------------------------------------------------------
# Section heading phrases (lowercased).
# ---------------------------------------------------------------------------
REQUIRED_HEADINGS = (
    "qualifications", "requirements", "what we are looking for", "what we're looking for",
    "what you need", "what you'll need", "what youll need", "who you are", "about you",
    "your background", "your profile", "profile", "minimum qualifications", "must have",
    "must-have", "essential", "essential requirements", "experience", "education",
    "skills", "skills and experience", "experience and skills", "knowledge", "knowledge and skills",
    "competencies", "what we expect", "what you bring", "what you will bring", "what you'll bring",
    "ideal candidate", "candidate profile", "selection criteria", "we are looking for",
    "we're looking for", "successful candidate", "who we are looking for", "required skills",
    "required qualifications", "required experience", "key requirements", "the role",
    "what you will do", "what you'll do", "what you will work on", "what you'll work on",
    "responsibilities", "key responsibilities", "core responsibilities", "role and responsibilities",
    "what you'll be doing", "what you will be doing", "job description", "about the role",
    "the position", "position summary", "technical skills", "hard skills", "qualification",
    "requirement", "cultural fit", "day to day", "day-to-day", "your day to day", "the team",
)

PREFERRED_HEADINGS = (
    "nice to have", "nice-to-have", "nice to haves", "preferred qualifications",
    "preferred skills", "preferred experience", "preferred requirements", "preferred",
    "bonus", "bonus points", "bonus skills", "good to have", "good-to-have", "a plus",
    "pluses", "would be a plus", "will be a plus", "is a plus", "ideally", "desired",
    "desired skills", "desired qualifications", "even better", "advantageous", "valued",
    "beneficial", "familiarity", "extra points", "bonuses",
)

IGNORED_HEADINGS = (
    "about us", "about the company", "who we are", "our company", "about the team",
    "our culture", "life at", "why join", "why work with us", "why us", "what we offer",
    "we offer", "benefits", "perks", "perks and benefits", "job benefits", "compensation",
    "compensation and benefits", "salary", "salary range", "salary and benefits",
    "equal opportunity", "equal opportunity employer", "equal employment", "diversity",
    "diversity and inclusion", "diversity, equity and inclusion", "dei", "inclusion",
    "our commitment", "accommodation", "reasonable accommodation", "accommodations",
    "how to apply", "apply now", "application process", "interview process",
    "our mission", "our story", "our values", "our values and mission", "the company",
    "company overview", "about the position", "learn more", "follow us", "contact us",
    "privacy policy", "terms and conditions", "cookies", "notice", "eeo", "eeoc",
    "applicant privacy", "data privacy", "legal disclaimer", "disclaimer",
)

# ---------------------------------------------------------------------------
# Strong boilerplate signals on a single line (benefits/EEO leftovers).
# ---------------------------------------------------------------------------
BOILERPLATE_LINE_MARKERS = (
    "401k", "401(k)", "health insurance", "dental insurance", "vision insurance",
    "life insurance", "paid time off", "paid vacation", "sick leave", "parental leave",
    "maternity leave", "paternity leave", "stock options", "equity package", "bonus structure",
    "annual bonus", "performance bonus", "competitive salary", "we offer", "we provide",
    "you will receive", "you'll receive", "benefits include", "perks include", "salary range",
    "compensation package", "compensation range", "the salary for this", "base salary",
    "equal opportunity employer",
    "all qualified applicants", "without regard to", "reasonable accommodation", "accommodations",
    "we celebrate diversity", "we are committed to", "we're committed to", "we value diversity",
    "diverse workforce", "inclusive workplace", "harassment", "discrimination", "eeo statement",
    "veteran status", "disability status", "genetic information", "applicant privacy",
    "privacy policy", "employment laws", "federal, state", "you have rights",
    "click the following links", "apply via", "to apply", "submit your application",
    "submit your cv", "submit your resume", "send your cv", "send your resume",
    "express your interest", "attach your", "apply through", "we encourage you to apply",
    "we encourage applicants", "we'd love to hear from you", "we would love to hear from you",
    "sound like you", "get in touch", "refer a friend", "recruitment agency", "recruiters",
    "please note", "note that",
)

# ---------------------------------------------------------------------------
# Experience modifier words (before "experience") and proficiency prefixes.
# ---------------------------------------------------------------------------
EXPERIENCE_MODIFIERS = (
    "professional", "relevant", "work", "industry", "hands-on", "hands on", "commercial",
    "practical", "related", "software", "development", "engineering", "production",
    "prior", "previous", "proven", "demonstrated", "extensive", "significant", "solid",
    "strong", "deep", "direct", "applied", "real-world", "real world", "shipping",
)

PROFICIENCY_PREFIXES = (
    "strong", "solid", "excellent", "good", "great", "outstanding", "advanced", "deep",
    "proven", "exceptional", "sound", "superb", "working", "practical", "high", "broad",
)


# ---------------------------------------------------------------------------
# Related-item maps used by the matcher: when the user owns a related skill or
# certificate instead of the exact one, the match still gets partial credit.
# ---------------------------------------------------------------------------
RELATED_SKILLS = {
    "pytorch": ["tensorflow", "keras", "jax"],
    "tensorflow": ["pytorch", "keras", "jax"],
    "keras": ["pytorch", "tensorflow"],
    "react": ["vue", "angular", "svelte", "next.js"],
    "vue": ["react", "angular", "svelte"],
    "angular": ["react", "vue", "svelte"],
    "postgresql": ["mysql", "sqlite", "sql server", "mariadb"],
    "mysql": ["postgresql", "sqlite", "sql server"],
    "mongodb": ["cassandra", "dynamodb", "redis"],
    "elasticsearch": ["opensearch", "solr"],
    "kafka": ["rabbitmq", "sqs", "sns"],
    "spark": ["pyspark", "hadoop", "databricks"],
    "databricks": ["spark", "pyspark", "snowflake", "bigquery"],
    "snowflake": ["bigquery", "redshift", "databricks"],
    "bigquery": ["snowflake", "redshift"],
    "aws": ["azure", "gcp", "google cloud"],
    "azure": ["aws", "gcp", "google cloud"],
    "gcp": ["aws", "azure", "google cloud"],
    "google cloud": ["aws", "azure", "gcp"],
    "docker": ["kubernetes", "k8s"],
    "kubernetes": ["docker", "k8s"],
    "k8s": ["docker", "kubernetes"],
    "terraform": ["pulumi", "cloudformation"],
    "ansible": ["chef", "puppet"],
    "jenkins": ["github actions", "gitlab ci", "circleci"],
    "github actions": ["jenkins", "gitlab ci"],
    "fastapi": ["flask", "django"],
    "flask": ["fastapi", "django"],
    "django": ["fastapi", "flask"],
    "node.js": ["express", "javascript"],
    "pandas": ["numpy", "scipy"],
    "numpy": ["pandas", "scipy"],
    "scikit-learn": ["xgboost", "lightgbm"],
    "xgboost": ["scikit-learn", "lightgbm", "catboost"],
    "lightgbm": ["scikit-learn", "xgboost"],
    "machine learning": ["deep learning", "data science", "nlp", "computer vision"],
    "deep learning": ["machine learning", "nlp", "computer vision"],
    "data science": ["machine learning", "data analysis", "statistics"],
    "data analysis": ["data science", "statistics", "business intelligence"],
    "nlp": ["machine learning", "deep learning", "llm", "llms"],
    "computer vision": ["machine learning", "deep learning"],
    "llm": ["nlp", "generative ai", "transformers", "llms"],
    "llms": ["llm", "nlp", "generative ai"],
    "generative ai": ["llm", "llms", "deep learning"],
    "transformers": ["llm", "deep learning"],
    "mlops": ["devops", "model deployment", "kubernetes"],
    "devops": ["mlops", "ci/cd", "docker"],
    "ci/cd": ["devops", "jenkins", "github actions"],
    "power bi": ["tableau", "looker"],
    "tableau": ["power bi", "looker"],
    "sql": ["postgresql", "mysql", "sql server", "sqlite"],
    "javascript": ["typescript", "node.js"],
    "typescript": ["javascript", "node.js"],
    "java": ["c#", "kotlin", "scala"],
    "c#": ["java", "kotlin"],
    "go": ["golang", "rust"],
    "golang": ["go", "rust"],
    "linux": ["unix", "bash", "shell scripting"],
    "git": ["github", "gitlab", "bitbucket"],
    "github": ["git", "gitlab"],
    "scrum": ["agile", "kanban"],
    "agile": ["scrum", "kanban"],
    "kanban": ["agile", "scrum"],
}

RELATED_CERTIFICATES = {
    "aws certified": ["aws certified solutions architect", "azure fundamentals", "gcp certification"],
    "aws certified solutions architect": ["aws certified", "azure solutions architect", "professional cloud architect"],
    "azure fundamentals": ["aws certified", "gcp certification", "az-900"],
    "az-900": ["azure fundamentals", "aws certified cloud practitioner"],
    "azure solutions architect": ["aws certified solutions architect", "professional cloud architect"],
    "professional cloud architect": ["aws certified solutions architect", "azure solutions architect"],
    "gcp certification": ["aws certified", "azure fundamentals"],
    "pmp": ["prince2", "capm", "csm"],
    "prince2": ["pmp", "capm"],
    "capm": ["pmp", "prince2"],
    "csm": ["psm", "pmp", "safe agilist"],
    "psm": ["csm", "safe agilist"],
    "cissp": ["cism", "cisa", "security+"],
    "cism": ["cissp", "cisa"],
    "cisa": ["cissp", "cism"],
    "security+": ["network+", "cissp", "cysa+"],
    "network+": ["security+", "ccna", "a+"],
    "ccna": ["ccnp", "network+", "jncia"],
    "ccnp": ["ccna", "ccie"],
    "cka": ["ckad", "cks", "docker certified associate"],
    "ckad": ["cka", "cks"],
    "itil": ["cobit", "togaf"],
    "togaf": ["itil", "cobit"],
    "six sigma": ["lean six sigma", "pmp"],
    "lean six sigma": ["six sigma", "pmp"],
    "cfa": ["frm", "cma"],
    "frm": ["cfa"],
    "cpa": ["acca", "cma"],
    "acca": ["cpa", "cma"],
    "rhce": ["rhcsa", "linux+"],
    "rhcsa": ["rhce", "linux+"],
}


# ---------------------------------------------------------------------------
# Curated, GUI-friendly lists (short enough to browse in the dropdowns).
# ---------------------------------------------------------------------------
POPULAR_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "SQL",
    "Machine Learning", "Deep Learning", "NLP", "LLMs", "Generative AI", "Data Science",
    "Data Analysis", "Computer Vision", "PyTorch", "TensorFlow", "Pandas", "NumPy",
    "Scikit-learn", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "MLOps",
    "React", "Node.js", "FastAPI", "Django", "Linux", "Git", "Kafka", "Spark",
    "PostgreSQL", "MongoDB", "Snowflake", "Power BI", "Tableau", "Agile", "Scrum",
    "Communication", "Teamwork", "Leadership", "Problem Solving",
]

POPULAR_CERTIFICATES = [
    "AWS Certified", "AWS Certified Solutions Architect", "Azure Fundamentals", "GCP Certification",
    "PMP", "PRINCE2", "CSM", "PSM", "ITIL", "TOGAF", "CISSP", "CISM", "Security+",
    "Network+", "CCNA", "CCNP", "CKA", "CKAD", "Docker Certified Associate",
    "Six Sigma", "Lean Six Sigma", "CFA", "CPA", "RHCE", "RHCSA",
]

POPULAR_LANGUAGES = [
    "English", "German", "French", "Spanish", "Italian", "Portuguese", "Dutch",
    "Turkish", "Arabic", "Chinese", "Japanese", "Korean", "Russian", "Polish", "Hindi",
]

EDUCATION_LEVELS = ["High School", "Associate", "Bachelor", "Master", "PhD"]
LANGUAGE_LEVELS = ["Basic", "Conversational", "Fluent", "Native"]
WORKPLACE_OPTIONS = ["Remote", "Hybrid", "On-site"]


# ---------------------------------------------------------------------------
# Broad expansions so non-technical job searches work too. Display lists are
# kept sorted alphabetically (see the POPULAR_* reassignments below).
# ---------------------------------------------------------------------------

SKILLS |= {
    # Business, finance & administration
    "business development", "business strategy", "business analysis", "operations management",
    "office management", "administrative support", "data entry", "bookkeeping", "payroll",
    "invoicing", "accounts payable", "accounts receivable", "budgeting", "forecasting",
    "treasury", "financial analysis", "financial planning", "investment banking",
    "asset management", "wealth management", "insurance underwriting", "claims processing",
    "actuarial science", "auditing", "internal audit", "taxation", "tax preparation",
    "quickbooks", "xero", "sap", "oracle", "erp systems", "procurement", "purchasing",
    "vendor management", "contract management", "tender management", "cost control",
    # Marketing, sales & customer-facing
    "marketing strategy", "digital marketing", "content marketing", "email marketing",
    "social media marketing", "seo", "sem", "ppc", "google ads", "facebook ads", "meta ads",
    "brand management", "public relations", "copywriting", "editing", "proofreading",
    "content creation", "community management", "influencer marketing", "affiliate marketing",
    "market research", "surveys", "focus groups", "customer success", "account management",
    "sales", "inside sales", "outside sales", "cold calling", "lead generation", "negotiation",
    "customer service", "customer support", "technical support", "help desk", "complaint handling",
    "upselling", "cross-selling", "crm", "salesforce", "hubspot", "zendesk", "intercom",
    # HR, people & training
    "human resources", "recruiting", "talent acquisition", "sourcing", "onboarding",
    "employee relations", "performance management", "compensation and benefits",
    "training and development", "instructional design", "e-learning", "lms administration",
    "coaching", "mentoring", "facilitation", "workshops", "succession planning",
    "organizational development", "change management", "diversity and inclusion",
    # Legal & compliance
    "legal research", "paralegal", "litigation support", "contract drafting", "contract review",
    "intellectual property", "patents", "trademarks", "copyright", "immigration law",
    "corporate law", "compliance", "regulatory affairs", "risk management", "anti-money laundering",
    "know your customer", "data protection", "gdpr", "privacy law", "due diligence",
    # Healthcare & life sciences
    "healthcare", "nursing", "patient care", "clinical research", "clinical trials",
    "pharmaceuticals", "pharmacovigilance", "medical coding", "medical billing",
    "electronic health records", "epic", "cerner", "telemedicine", "public health",
    "epidemiology", "biostatistics", "bioinformatics", "genomics", "laboratory skills",
    "microscopy", "medical devices", "regulatory submission", "fda", "ema", "gcp",
    "good clinical practice", "physiotherapy", "occupational therapy", "dental assisting",
    "pharmacy", "radiology", "sonography", "emergency medicine", "first aid", "cpr",
    # Education, research & academia
    "teaching", "curriculum development", "lesson planning", "classroom management",
    "special education", "early childhood education", "esl", "tefl", "tesol", "tutoring",
    "academic writing", "academic research", "literature review", "data collection",
    "statistical analysis", "spss", "stata", "r programming", "qualitative research",
    "quantitative research", "peer review", "grant writing", "fundraising",
    "library science", "archival research", "museum curation",
    # Design, media & creative
    "graphic design", "illustration", "branding", "typography", "layout design",
    "ux design", "ui design", "user research", "usability testing", "wireframing",
    "prototyping", "figma", "sketch", "adobe photoshop", "adobe illustrator",
    "adobe indesign", "adobe premiere pro", "after effects", "final cut pro",
    "davinci resolve", "video editing", "video production", "audio engineering",
    "podcasting", "photography", "photo editing", "lightroom", "videography",
    "motion graphics", "animation", "3d modeling", "blender", "maya", "unity",
    "unreal engine", "game design", "game development", "music production",
    "songwriting", "screenwriting", "journalism", "reporting", "broadcasting",
    "script writing", "translation", "interpretation", "localization", "subtitling",
    # Engineering, construction & industry
    "mechanical engineering", "electrical engineering", "civil engineering",
    "chemical engineering", "industrial engineering", "structural engineering",
    "geotechnical engineering", "environmental engineering", "aerospace engineering",
    "automotive engineering", "manufacturing engineering", "process engineering",
    "quality assurance", "quality control", "inspection", "metrology", "lean manufacturing",
    "continuous improvement", "cad", "autocad", "solidworks", "revit", "bim",
    "plc programming", "scada", "industrial automation", "robotics", "cnc machining",
    "machining", "welding", "fabrication", "maintenance", "reliability engineering",
    "predictive maintenance", "safety engineering", "occupational health and safety",
    "hse", "risk assessment", "project planning", "site management", "surveying",
    "estimating", "quantity surveying", "construction management", "blueprint reading",
    # Transport, logistics & supply chain
    "supply chain management", "logistics", "inventory management", "warehouse management",
    "fleet management", "dispatch", "route planning", "freight forwarding", "customs clearance",
    "shipping", "import export", "demand planning", "production planning", "material planning",
    "distribution", "last mile delivery", "forklift operation", "commercial driving",
    "truck driving", "driving license", "aviation", "airline operations", "maritime",
    # Hospitality, food & retail
    "hospitality", "hotel management", "front office", "housekeeping", "restaurant management",
    "food service", "waiting", "bartending", "mixology", "barista", "culinary arts",
    "cooking", "baking", "pastry", "food safety", "servsafe", "haccp", "event planning",
    "event management", "wedding planning", "catering", "travel planning", "tourism",
    "tour guiding", "retail management", "visual merchandising", "inventory control",
    "cash handling", "point of sale", "store operations",
    # Public sector, security & community
    "public administration", "policy analysis", "government relations", "urban planning",
    "community outreach", "program management", "nonprofit management", "volunteer management",
    "social work", "case management", "counseling", "psychology", "childcare",
    "elder care", "caregiving", "criminal justice", "law enforcement", "security operations",
    "surveillance", "emergency management", "firefighting", "military", "intelligence analysis",
    # Sports, fitness & beauty
    "personal training", "fitness instruction", "nutrition", "dietetics", "sports coaching",
    "athletic training", "yoga instruction", "pilates", "physiology", "kinesiology",
    "cosmetology", "beauty therapy", "barbering", "nail care", "skincare", "makeup artistry",
    "hair styling", "spa therapy", "massage therapy",
    # Trades & agriculture
    "electrical work", "plumbing", "hvac", "carpentry", "masonry", "painting", "roofing",
    "landscaping", "gardening", "floristry", "pest control", "janitorial", "cleaning",
    "agriculture", "farming", "animal care", "veterinary assisting", "pet grooming",
    "zookeeping", "forestry", "fishing", "mining", "oil and gas", "energy management",
    "renewable energy", "solar installation", "wind energy", "utilities", "water treatment",
    "waste management", "environmental science", "sustainability", "esg reporting",
    # Office & general
    "microsoft office", "microsoft excel", "microsoft word", "microsoft powerpoint",
    "google workspace", "google sheets", "google docs", "outlook", "gmail", "slack",
    "microsoft teams", "zoom", "scheduling", "calendar management", "travel booking",
    "expense reporting", "typing", "shorthand", "dictation", "filing", "record keeping",
    "time management", "multitasking", "organization", "attention to detail",
    "problem solving", "critical thinking", "teamwork", "communication", "leadership",
    "presentation skills", "public speaking", "report writing", "documentation",
}

CERTIFICATES |= {
    # Healthcare & life sciences
    "bls", "acls", "pals", "cpr certification", "first aid certification", "cna",
    "licensed practical nurse", "registered nurse", "nclex", "ccrn", "cen",
    "emt", "paramedic", "pharmacy technician", "medical assistant", "phlebotomy",
    "usmle", "board certified", "rhia", "rhit", "cpc", "ccs", "cdip", "chda",
    "ich-gcp", "good clinical practice", "rac",
    # Education & languages
    "teaching license", "teaching certification", "tefl", "tesol", "celta", "delta",
    "ielts", "toefl", "toeic", "dele", "delf", "dalf", "goethe-zertifikat", "jlpt", "hsk",
    "microsoft certified educator", "google certified educator",
    # Finance, accounting & insurance
    "cfp", "chfc", "series 7", "series 63", "series 65", "series 66", "finra",
    "cma", "cfa", "cpa", "acca", "frm", "caia", "cipm", "cfa charter",
    "cpcu", "ains", "arm", "crcm", "cams",
    # HR & management
    "phr", "sphr", "shrm-cp", "shrm-scp", "pmi-acp", "pfmp", "pmi-rmp", "pgmp",
    "csm", "psm i", "psm ii", "pspo", "safe", "safe agilist", "kanban management professional",
    "lean six sigma", "six sigma green belt", "six sigma black belt", "six sigma yellow belt",
    # IT, cloud & security (extra)
    "comptia a+", "comptia network+", "comptia security+", "comptia cysa+", "comptia pentest+",
    "comptia casp+", "comptia cloud+", "comptia linux+", "comptia project+", "comptia server+",
    "cissp", "cissp-issap", "cissp-issep", "cism", "cisa", "crisc", "cgeit", "cdpse",
    "ccsp", "sscp", "gpen", "gwapt", "gcih", "gsec", "gsna", "ceh", "oscp", "osep",
    "ccna", "ccnp", "ccie", "devnet", "jncia", "jncis", "jncie",
    "microsoft az-900", "az-104", "az-204", "az-305", "az-400", "az-500", "ai-102",
    "dp-100", "dp-203", "dp-300", "dp-900", "pl-300", "sc-900", "sc-200", "ms-900",
    "mcsa", "mcse", "mcp", "mct", "microsoft certified",
    "aws certified cloud practitioner", "aws certified solutions architect",
    "aws certified developer", "aws certified sysops administrator", "aws certified devops engineer",
    "aws certified security", "aws certified machine learning", "aws certified data analytics",
    "aws certified advanced networking", "aws certified database",
    "gcp certification", "associate cloud engineer", "professional cloud architect",
    "professional data engineer", "professional machine learning engineer",
    "professional cloud developer", "professional cloud devops engineer",
    "professional cloud security engineer", "cloud digital leader",
    "alibaba cloud aca", "alibaba cloud acp", "huawei hcia", "huawei hcip",
    "cka", "ckad", "cks", "docker certified associate", "terraform associate",
    "hashicorp vault associate", "lfcs", "lfce", "rhce", "rhcsa", "linux+", "lpic",
    "itil 4 foundation", "itil", "cobit 2019", "cobit", "togaf",
    "iso 27001 lead auditor", "iso 27001", "iso 9001", "soc 2",
    # Data, analytics & quality
    "databricks certified", "snowflake snowpro", "tableau certified", "tableau desktop specialist",
    "power bi certification", "power bi data analyst", "cloudera certified", "cdmp",
    "google data analytics", "google advanced data analytics", "istqb", "csmq",
    # Design, marketing & other professional
    "google ads certification", "google analytics certification", "meta blueprint",
    "hubspot inbound", "hubspot marketing", "adobe certified expert", "adobe ace",
    "pmp", "prince2", "capm", "cpsm", "apics cpim", "apics cscp", "cltd", "scpro",
    "servsafe", "haccp certification", "food handler", "nasm",
    "ace personal trainer", "acsm", "nsca", "rei", "real estate license", "notary public",
    "cipp", "cipm", "cipt", "bar admission", "diploma in nursing", "diploma in education",
    "forklift certification", "cdl", "hazmat", "osha 30", "osha 10", "nebosh", "iosh",
}

# Popular lists are curated, alphabetically ordered subsets used by the GUI
# dropdowns and the CLI option lists.
POPULAR_SKILLS = sorted({
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "SQL",
    "Machine Learning", "Deep Learning", "NLP", "LLMs", "Generative AI", "Data Science",
    "Data Analysis", "Data Entry", "Computer Vision", "PyTorch", "TensorFlow", "Pandas",
    "NumPy", "Scikit-learn", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD",
    "MLOps", "React", "Node.js", "FastAPI", "Django", "Linux", "Git", "Kafka", "Spark",
    "PostgreSQL", "MongoDB", "Snowflake", "Power BI", "Tableau", "Agile", "Scrum",
    "Communication", "Teamwork", "Leadership", "Problem Solving", "Customer Service",
    "Sales", "Marketing", "Digital Marketing", "SEO", "Accounting", "Bookkeeping",
    "Financial Analysis", "Human Resources", "Recruiting", "Project Management",
    "Teaching", "Curriculum Development", "Graphic Design", "UX Design", "UI Design",
    "Video Editing", "Photography", "Copywriting", "Content Creation", "Public Speaking",
    "Nursing", "Patient Care", "Clinical Research", "Pharmacy", "Medical Coding",
    "Legal Research", "Compliance", "Risk Management", "Supply Chain", "Logistics",
    "Inventory Management", "Hospitality", "Event Planning", "Cooking", "Baking",
    "Construction", "CAD", "AutoCAD", "SolidWorks", "Welding", "Electrical Work",
    "Plumbing", "HVAC", "Carpentry", "Driving", "Warehouse Management", "Forklift Operation",
    "Personal Training", "Nutrition", "Cosmetology", "Massage Therapy", "Childcare",
    "Social Work", "Counseling", "Teaching English", "Translation", "Journalism",
})

POPULAR_CERTIFICATES = sorted({
    "AWS Certified", "AWS Certified Solutions Architect", "AWS Certified Cloud Practitioner",
    "Azure Fundamentals", "AZ-900", "AZ-104", "GCP Certification", "Associate Cloud Engineer",
    "PMP", "PRINCE2", "CAPM", "CSM", "PSM I", "PSM II", "ITIL", "ITIL 4 Foundation",
    "TOGAF", "CISSP", "CISM", "CISA", "Security+", "CompTIA Security+", "CompTIA A+",
    "CompTIA Network+", "CCNA", "CCNP", "CKA", "CKAD", "CKS", "Docker Certified Associate",
    "Terraform Associate", "RHCE", "RHCSA", "Six Sigma", "Lean Six Sigma",
    "Six Sigma Green Belt", "Six Sigma Black Belt", "CFA", "CPA", "ACCA", "CMA", "FRM",
    "CFP", "Series 7", "PHR", "SPHR", "SHRM-CP", "SHRM-SCP", "Google Ads Certification",
    "Google Analytics Certification", "Meta Blueprint", "HubSpot Inbound", "Tableau Certified",
    "Power BI Certification", "Databricks Certified", "Snowflake SnowPro", "ISTQB",
    "NCLEX", "BLS", "ACLS", "CPR Certification", "First Aid Certification", "CNA",
    "EMT", "Pharmacy Technician", "Medical Assistant", "RHIA", "RHIT", "CPC",
    "Teaching License", "TEFL", "TESOL", "CELTA", "IELTS", "TOEFL",
    "Real Estate License", "Notary Public", "CIPP", "CIPM", "CIPT", "Bar Admission",
    "ServSafe", "HACCP Certification", "Forklift Certification", "CDL", "OSHA 10",
    "OSHA 30", "NEBOSH", "ACE Personal Trainer", "NASM", "ACSM", "NSCA",
    "CPSM", "APICS CPIM", "APICS CSCP", "Google Data Analytics", "ISO 27001",
})


# ---------------------------------------------------------------------------
# Display formatting for option lists.
# ---------------------------------------------------------------------------

# Words rendered in uppercase inside display names ("aws certified" -> "AWS Certified").
WORD_ACRONYMS = {"aws", "gcp", "itil", "pmp", "csm", "psm", "sql", "llm", "llms", "nlp", "ml",
                 "ai", "ui", "ux", "api", "hr", "iso", "cpr", "emt", "cna", "cdl", "osha",
                 "hvac", "cad", "bim", "seo", "sem", "ppc", "esg", "hse", "crm", "erp", "kpi"}


def display_name(entry):
    """User-facing name for an option: 'machine learning' -> 'Machine Learning',
    'c++' and 'node.js' stay untouched, known acronyms become uppercase."""
    if " " in entry and all(ch.isalpha() or ch.isspace() for ch in entry):
        words = [word.upper() if word in WORD_ACRONYMS else word.capitalize()
                 for word in entry.split()]
        return " ".join(words)
    return entry
