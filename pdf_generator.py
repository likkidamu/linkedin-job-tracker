import os
import re
import logging
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from config import OUTPUT_DIR

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Renders a tailored resume dict into a professional PDF using
    Jinja2 HTML templates + WeasyPrint.
    """

    def __init__(self, template_dir: str = "templates", output_dir: str = None):
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template("resume.html")

    def generate_pdf(self, resume_data: dict, company: str,
                     job_title: str, job_id: str) -> str:
        """
        Generate a PDF resume and return the file path.

        Args:
            resume_data: Tailored resume dict (same structure as base_resume.json)
            company: Company name
            job_title: Job title
            job_id: Unique job ID (for filename)

        Returns:
            Absolute path to the generated PDF
        """
        # Render HTML from template
        html_content = self.template.render(
            resume=resume_data,
            company=company,
            job_title=job_title,
        )

        # Build filename: Company_JobTitle_JobID.pdf
        safe_company = _sanitize_filename(company)
        safe_title = _sanitize_filename(job_title)
        filename = f"{safe_company}_{safe_title}_{job_id[:8]}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        # Generate PDF
        HTML(string=html_content).write_pdf(filepath)
        logger.info(f"PDF generated: {filepath}")

        return filepath


def _sanitize_filename(name: str) -> str:
    """Remove special characters and limit length for safe filenames."""
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return name[:40]
