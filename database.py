import sqlite3
import os
from datetime import datetime


class JobDatabase:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_tables(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    company_category TEXT,
                    location TEXT,
                    description TEXT,
                    url TEXT,
                    posted_date TEXT,
                    experience_level TEXT,
                    scraped_at TEXT NOT NULL,
                    resume_generated INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    company TEXT NOT NULL,
                    title TEXT NOT NULL,
                    pdf_path TEXT NOT NULL,
                    tailored_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                );

                -- Add tailored_json column if missing (migration for existing DBs)
                CREATE TABLE IF NOT EXISTS _migration_check (id INTEGER);
                DROP TABLE IF EXISTS _migration_check;
            """)
            # Migration: add tailored_json column if it doesn't exist
            try:
                conn.execute("SELECT tailored_json FROM resumes LIMIT 0")
            except sqlite3.OperationalError:
                conn.execute("ALTER TABLE resumes ADD COLUMN tailored_json TEXT")

            conn.executescript("""
                CREATE TABLE IF NOT EXISTS scrape_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    companies_scraped INTEGER DEFAULT 0,
                    jobs_found INTEGER DEFAULT 0,
                    new_jobs INTEGER DEFAULT 0,
                    resumes_generated INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'running',
                    error TEXT
                );
            """)

    def insert_job(self, job: dict) -> bool:
        """Insert a job. Returns True if it's a new job, False if duplicate."""
        try:
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO jobs (job_id, title, company, company_category,
                                     location, description, url, posted_date,
                                     experience_level, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job["job_id"], job["title"], job["company"],
                    job.get("company_category", ""),
                    job.get("location", ""), job.get("description", ""),
                    job.get("url", ""), job.get("posted_date", ""),
                    job.get("experience_level", ""),
                    datetime.utcnow().isoformat()
                ))
            return True
        except sqlite3.IntegrityError:
            return False

    def get_jobs_without_resume(self) -> list[dict]:
        """Get all jobs that don't have a resume generated yet."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM jobs WHERE resume_generated = 0
                ORDER BY scraped_at DESC
            """).fetchall()
        return [dict(row) for row in rows]

    def mark_resume_generated(self, job_id: str, pdf_path: str, company: str, title: str,
                              tailored_json: str = None):
        with self._connect() as conn:
            conn.execute(
                "UPDATE jobs SET resume_generated = 1 WHERE job_id = ?",
                (job_id,)
            )
            conn.execute("""
                INSERT INTO resumes (job_id, company, title, pdf_path, tailored_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (job_id, company, title, pdf_path, tailored_json, datetime.utcnow().isoformat()))

    def start_scrape_log(self) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO scrape_log (started_at) VALUES (?)",
                (datetime.utcnow().isoformat(),)
            )
            return cursor.lastrowid

    def finish_scrape_log(self, log_id: int, companies: int, found: int,
                          new: int, resumes: int, status: str = "completed",
                          error: str = None):
        with self._connect() as conn:
            conn.execute("""
                UPDATE scrape_log
                SET completed_at = ?, companies_scraped = ?, jobs_found = ?,
                    new_jobs = ?, resumes_generated = ?, status = ?, error = ?
                WHERE id = ?
            """, (
                datetime.utcnow().isoformat(), companies, found,
                new, resumes, status, error, log_id
            ))

    def get_stats(self) -> dict:
        with self._connect() as conn:
            total_jobs = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
            total_resumes = conn.execute("SELECT COUNT(*) FROM resumes").fetchone()[0]
            total_scrapes = conn.execute("SELECT COUNT(*) FROM scrape_log").fetchone()[0]
            companies = conn.execute(
                "SELECT COUNT(DISTINCT company) FROM jobs"
            ).fetchone()[0]
        return {
            "total_jobs": total_jobs,
            "total_resumes": total_resumes,
            "total_scrapes": total_scrapes,
            "unique_companies": companies,
        }
# . Databricks
# 2. Snowflake
# 3. ServiceNow
# 4. Workday
# 5. Atlassian
# 6. HubSpot
# 7. Okta
# 8. MongoDB
# 9. Elastic
# 10. Splunk
# 11. Datadog
# 12. Twilio
# 13. Zscaler
# 14. Cloudflare
# 15. CrowdStrike
# 16. Stripe
# 17. Square (Block)
# 18. Plaid
# 19. Robinhood
# 20. Coinbase
# 21. SoFi
# 22. Affirm
# 23. Marqeta
# 24. Chime
# 25. Brex
# 26. Epic Systems
# 27. Cerner (Oracle Health)
# 28. GE HealthCare
# 29. Philips
# 30. Allscripts
# 31. Medtronic
# 32. Change Healthcare
# 33. Hims & Hers
# 34. ResMed
# 35. Guardant Health
# 36. ZS Associates
# 37. Slalom
# 38. EPAM Systems
# 39. Capgemini
# 40. Cognizant
# 41. LTIMindtree
# 42. Infosys
# 43. Tata Consultancy Services (TCS)
# 44. Wipro
# 45. HCL Technologies
# 46. Wayfair
# 47. Chewy
# 48. DoorDash
# 49. Instacart
# 50. Flexport
