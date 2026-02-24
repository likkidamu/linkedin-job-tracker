import requests
import logging
import time
from config import RAPIDAPI_KEY, JOB_KEYWORDS, JOB_LOCATION

logger = logging.getLogger(__name__)


class LinkedInJobScraper:
    """
    Fetches LinkedIn job postings via RapidAPI.

    Uses the 'linkedin-jobs-search' API on RapidAPI.
    Sign up at: https://rapidapi.com/jaypat87/api/linkedin-jobs-search

    Alternative APIs you can swap in:
      - Proxycurl: https://nubela.co/proxycurl/docs#jobs-api-job-search-endpoint
      - SerpAPI: https://serpapi.com/linkedin-jobs-api
      - JobsAPI: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
    """

    BASE_URL = "https://linkedin-jobs-search.p.rapidapi.com"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or RAPIDAPI_KEY
        if not self.api_key:
            raise ValueError(
                "RAPIDAPI_KEY is required. Get one at https://rapidapi.com"
            )
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "linkedin-jobs-search.p.rapidapi.com",
            "Content-Type": "application/json",
        }

    def search_jobs(self, company_name: str, keywords: str = None,
                    location: str = None, page: int = 1) -> list[dict]:
        """
        Search for jobs at a specific company.

        Returns a list of job dicts with keys:
            job_id, title, company, location, description, url,
            posted_date, experience_level
        """
        keywords = keywords or JOB_KEYWORDS
        location = location or JOB_LOCATION

        payload = {
            "search_terms": f"{keywords} {company_name}",
            "location": location,
            "page": str(page),
            "fetch_full_text": "yes",
        }

        try:
            response = requests.post(
                self.BASE_URL,
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            raw_jobs = response.json()

            if not isinstance(raw_jobs, list):
                logger.warning(f"Unexpected response for {company_name}: {type(raw_jobs)}")
                return []

            jobs = []
            for job in raw_jobs:
                # Filter: only include jobs that actually match the company
                job_company = (job.get("company_name") or "").lower()
                if company_name.lower().split()[0] not in job_company:
                    continue

                jobs.append({
                    "job_id": job.get("job_id", job.get("id", "")),
                    "title": job.get("job_title", job.get("title", "")),
                    "company": job.get("company_name", company_name),
                    "location": job.get("job_location", job.get("location", "")),
                    "description": job.get("job_description", job.get("description", "")),
                    "url": job.get("job_url", job.get("linkedin_job_url_cleaned", "")),
                    "posted_date": job.get("posted_date", job.get("list_date", "")),
                    "experience_level": job.get("job_experience_level", ""),
                })

            logger.info(f"Found {len(jobs)} jobs for {company_name}")
            return jobs

        except requests.exceptions.RequestException as e:
            logger.error(f"API error for {company_name}: {e}")
            return []

    def scrape_all_companies(self, companies: list[dict],
                             rate_limit_seconds: float = 2.0) -> list[dict]:
        """
        Scrape jobs for all companies with rate limiting.

        Args:
            companies: List of dicts with 'name' and 'category' keys
            rate_limit_seconds: Delay between API calls

        Returns:
            List of all job dicts with 'company_category' added
        """
        all_jobs = []

        for company in companies:
            name = company["name"]
            category = company.get("category", "unknown")

            logger.info(f"Scraping jobs for: {name} ({category})")
            jobs = self.search_jobs(company_name=name)

            for job in jobs:
                job["company_category"] = category

            all_jobs.extend(jobs)
            time.sleep(rate_limit_seconds)

        logger.info(f"Total jobs scraped: {len(all_jobs)} from {len(companies)} companies")
        return all_jobs


class JSearchScraper:
    """
    Alternative scraper using JSearch API (broader job search, not LinkedIn-specific).
    Sign up at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

    Good fallback if LinkedIn-specific API has issues.
    """

    BASE_URL = "https://jsearch.p.rapidapi.com/search"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or RAPIDAPI_KEY
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com",
        }

    def search_jobs(self, company_name: str, keywords: str = None,
                    location: str = None, page: int = 1) -> list[dict]:
        keywords = keywords or JOB_KEYWORDS
        location = location or JOB_LOCATION

        params = {
            "query": f"{keywords} at {company_name} in {location}",
            "page": str(page),
            "num_pages": "1",
        }

        try:
            response = requests.get(
                self.BASE_URL,
                headers=self.headers,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json().get("data", [])

            jobs = []
            for job in data:
                jobs.append({
                    "job_id": job.get("job_id", ""),
                    "title": job.get("job_title", ""),
                    "company": job.get("employer_name", company_name),
                    "location": f"{job.get('job_city', '')}, {job.get('job_state', '')}",
                    "description": job.get("job_description", ""),
                    "url": job.get("job_apply_link", ""),
                    "posted_date": job.get("job_posted_at_datetime_utc", ""),
                    "experience_level": job.get("job_required_experience", {}).get(
                        "experience_level", ""
                    ),
                })

            return jobs

        except requests.exceptions.RequestException as e:
            logger.error(f"JSearch API error for {company_name}: {e}")
            return []
