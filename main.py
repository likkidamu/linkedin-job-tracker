import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

from config import ALL_COMPANIES, SCRAPE_INTERVAL_HOURS, DB_PATH
from database import JobDatabase
from scraper import LinkedInJobScraper
from resume_tailor import ResumeTailor
from pdf_generator import PDFGenerator

load_dotenv()

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/app/data/scraper.log", mode="a"),
    ],
)
logger = logging.getLogger("main")

# ── Initialize components ──
db = JobDatabase(DB_PATH)
scraper = LinkedInJobScraper()
tailor = ResumeTailor(base_resume_path="/app/base_resume.json")
pdf_gen = PDFGenerator(template_dir="/app/templates")


def run_pipeline():
    """
    Full pipeline:
    1. Scrape jobs from all 39 companies
    2. Store new jobs in database
    3. Tailor resume for each new job
    4. Generate PDF
    """
    logger.info("=" * 60)
    logger.info("PIPELINE STARTED at %s", datetime.utcnow().isoformat())
    logger.info("=" * 60)

    log_id = db.start_scrape_log()
    total_found = 0
    total_new = 0
    total_resumes = 0

    try:
        # ── Step 1: Scrape ──
        logger.info("Step 1: Scraping jobs from %d companies...", len(ALL_COMPANIES))
        all_jobs = scraper.scrape_all_companies(ALL_COMPANIES)
        total_found = len(all_jobs)
        logger.info("Found %d total job postings", total_found)

        # ── Step 2: Store new jobs ──
        logger.info("Step 2: Storing new jobs in database...")
        for job in all_jobs:
            is_new = db.insert_job(job)
            if is_new:
                total_new += 1

        logger.info("New jobs added: %d (duplicates skipped: %d)",
                     total_new, total_found - total_new)

        # ── Step 3: Generate resumes for new jobs ──
        pending_jobs = db.get_jobs_without_resume()
        logger.info("Step 3: Generating resumes for %d jobs...", len(pending_jobs))

        for job in pending_jobs:
            try:
                logger.info("  Tailoring resume for: %s at %s",
                            job["title"], job["company"])

                tailored_resume = tailor.tailor_resume(job)
                pdf_path = pdf_gen.generate_pdf(
                    resume_data=tailored_resume,
                    company=job["company"],
                    job_title=job["title"],
                    job_id=job["job_id"],
                )
                db.mark_resume_generated(
                    job["job_id"], pdf_path, job["company"], job["title"]
                )
                total_resumes += 1

            except Exception as e:
                logger.error("  Failed for %s at %s: %s",
                             job["title"], job["company"], e)

        # ── Done ──
        db.finish_scrape_log(log_id, len(ALL_COMPANIES), total_found,
                             total_new, total_resumes)

        stats = db.get_stats()
        logger.info("-" * 40)
        logger.info("PIPELINE COMPLETED")
        logger.info("  This run: %d found, %d new, %d resumes",
                     total_found, total_new, total_resumes)
        logger.info("  All time: %d jobs, %d resumes, %d companies",
                     stats["total_jobs"], stats["total_resumes"],
                     stats["unique_companies"])
        logger.info("=" * 60)

    except Exception as e:
        logger.error("PIPELINE FAILED: %s", e, exc_info=True)
        db.finish_scrape_log(log_id, len(ALL_COMPANIES), total_found,
                             total_new, total_resumes, status="failed",
                             error=str(e))


def main():
    logger.info("LinkedIn Job Tracker starting...")
    logger.info("Tracking %d companies", len(ALL_COMPANIES))
    logger.info("Schedule: every %d hour(s)", SCRAPE_INTERVAL_HOURS)

    # Run once immediately on startup
    run_pipeline()

    # Schedule recurring runs
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_pipeline,
        "interval",
        hours=SCRAPE_INTERVAL_HOURS,
        id="scrape_pipeline",
        next_run_time=None,  # Don't run immediately (we just did)
    )

    logger.info("Scheduler started. Next run in %d hour(s). Press Ctrl+C to stop.",
                SCRAPE_INTERVAL_HOURS)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
