import os

# ── API Keys (set via environment variables or .env) ──
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")

# ── Ollama (local LLM — no API key needed) ──
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# ── Scheduler ──
SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "1"))

# ── Database ──
DB_PATH = os.getenv("DB_PATH", "/app/data/jobs.db")

# ── Output ──
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")

# ── Companies to track ──
COMPANIES = {
    "tech_saas": [
        {"name": "Databricks", "linkedin_id": "databricks"},
        {"name": "Snowflake", "linkedin_id": "snowflake-computing"},
        {"name": "ServiceNow", "linkedin_id": "servicenow"},
        {"name": "Workday", "linkedin_id": "workday"},
        {"name": "Atlassian", "linkedin_id": "atlassian"},
        {"name": "HubSpot", "linkedin_id": "hubspot"},
        {"name": "Okta", "linkedin_id": "okta-inc-"},
        {"name": "MongoDB", "linkedin_id": "mongodbinc"},
        {"name": "Elastic", "linkedin_id": "elastic-co"},
        {"name": "Splunk", "linkedin_id": "splunk"},
        {"name": "Datadog", "linkedin_id": "datadog"},
        {"name": "Twilio", "linkedin_id": "twilio-inc-"},
        {"name": "Zscaler", "linkedin_id": "zscaler"},
        {"name": "Cloudflare", "linkedin_id": "cloudflare"},
        {"name": "CrowdStrike", "linkedin_id": "crowdstrike"},
    ],
    "fintech": [
        {"name": "Stripe", "linkedin_id": "stripe"},
        {"name": "Square (Block)", "linkedin_id": "joinsquare"},
        {"name": "Plaid", "linkedin_id": "plaid-"},
        {"name": "Robinhood", "linkedin_id": "robinhood"},
        {"name": "Coinbase", "linkedin_id": "coinbase"},
        {"name": "SoFi", "linkedin_id": "sofi"},
        {"name": "Affirm", "linkedin_id": "affirm"},
        {"name": "Marqeta", "linkedin_id": "marqeta"},
        {"name": "Chime", "linkedin_id": "chaborchime"},
        {"name": "Brex", "linkedin_id": "braborex"},
    ],
    "healthcare": [
        {"name": "Epic Systems", "linkedin_id": "epic-systems"},
        {"name": "Cerner (Oracle Health)", "linkedin_id": "cerner-corporation"},
        {"name": "GE HealthCare", "linkedin_id": "gehealthcare"},
        {"name": "Philips", "linkedin_id": "philips"},
        {"name": "Allscripts", "linkedin_id": "allscripts"},
        {"name": "Medtronic", "linkedin_id": "medtronic"},
        {"name": "Change Healthcare", "linkedin_id": "change-healthcare"},
        {"name": "Hims & Hers", "linkedin_id": "haborhers"},
        {"name": "ResMed", "linkedin_id": "resmed"},
        {"name": "Guardant Health", "linkedin_id": "guardanthealth"},
    ],
    "consulting": [
        {"name": "ZS Associates", "linkedin_id": "zs-associates"},
        {"name": "Slalom", "linkedin_id": "slalom-consulting"},
        {"name": "EPAM Systems", "linkedin_id": "epam-systems"},
        {"name": "Capgemini", "linkedin_id": "capgemini"},
    ],
}

# Flatten for easy iteration
ALL_COMPANIES = []
for category, companies in COMPANIES.items():
    for company in companies:
        company["category"] = category
        ALL_COMPANIES.append(company)

# ── Job search filters ──
JOB_KEYWORDS = os.getenv("JOB_KEYWORDS", "software engineer,data engineer,backend,full stack,python,java")
JOB_LOCATION = os.getenv("JOB_LOCATION", "United States")
JOB_EXPERIENCE_LEVEL = os.getenv("JOB_EXPERIENCE_LEVEL", "")  # e.g., "entry_level,mid_senior"
