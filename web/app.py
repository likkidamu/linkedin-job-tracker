import os
import sqlite3
from flask import Flask, render_template, send_file, request, jsonify

DB_PATH = os.getenv("DB_PATH", "/app/data/jobs.db")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def dashboard():
    db = get_db()
    stats = {
        "total_jobs": db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],
        "total_resumes": db.execute("SELECT COUNT(*) FROM resumes").fetchone()[0],
        "unique_companies": db.execute("SELECT COUNT(DISTINCT company) FROM jobs").fetchone()[0],
        "total_scrapes": db.execute("SELECT COUNT(*) FROM scrape_log").fetchone()[0],
    }
    categories = db.execute(
        "SELECT company_category, COUNT(*) as cnt FROM jobs GROUP BY company_category"
    ).fetchall()
    recent_jobs = db.execute(
        "SELECT * FROM jobs ORDER BY scraped_at DESC LIMIT 10"
    ).fetchall()
    db.close()
    return render_template("dashboard.html", stats=stats, categories=categories, recent_jobs=recent_jobs)


@app.route("/jobs")
def jobs_list():
    db = get_db()
    company = request.args.get("company", "")
    category = request.args.get("category", "")
    search = request.args.get("search", "")

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if company:
        query += " AND company = ?"
        params.append(company)
    if category:
        query += " AND company_category = ?"
        params.append(category)
    if search:
        query += " AND (title LIKE ? OR company LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY scraped_at DESC"

    jobs = db.execute(query, params).fetchall()
    companies = db.execute("SELECT DISTINCT company FROM jobs ORDER BY company").fetchall()
    categories = db.execute("SELECT DISTINCT company_category FROM jobs ORDER BY company_category").fetchall()
    db.close()
    return render_template("jobs.html", jobs=jobs, companies=companies, categories=categories,
                           selected_company=company, selected_category=category, search_query=search)


@app.route("/resumes")
def resumes_list():
    db = get_db()
    resumes = db.execute("""
        SELECT r.*, j.title as job_title, j.url as job_url
        FROM resumes r
        LEFT JOIN jobs j ON r.job_id = j.job_id
        ORDER BY r.created_at DESC
    """).fetchall()
    db.close()
    return render_template("resumes.html", resumes=resumes)


@app.route("/resumes/download/<int:resume_id>")
def download_resume(resume_id):
    db = get_db()
    resume = db.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,)).fetchone()
    db.close()
    if resume and os.path.exists(resume["pdf_path"]):
        return send_file(resume["pdf_path"], as_attachment=True)
    return "Resume not found", 404


@app.route("/scrape-log")
def scrape_log():
    db = get_db()
    logs = db.execute("SELECT * FROM scrape_log ORDER BY started_at DESC LIMIT 50").fetchall()
    db.close()
    return render_template("scrape_log.html", logs=logs)


@app.route("/api/stats")
def api_stats():
    db = get_db()
    stats = {
        "total_jobs": db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],
        "total_resumes": db.execute("SELECT COUNT(*) FROM resumes").fetchone()[0],
        "unique_companies": db.execute("SELECT COUNT(DISTINCT company) FROM jobs").fetchone()[0],
        "top_companies": [dict(r) for r in db.execute(
            "SELECT company, COUNT(*) as job_count FROM jobs GROUP BY company ORDER BY job_count DESC LIMIT 10"
        ).fetchall()],
    }
    db.close()
    return jsonify(stats)


@app.route("/api/jobs")
def api_jobs():
    db = get_db()
    jobs = [dict(r) for r in db.execute(
        "SELECT job_id, title, company, company_category, location, url, posted_date, resume_generated, scraped_at FROM jobs ORDER BY scraped_at DESC"
    ).fetchall()]
    db.close()
    return jsonify(jobs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
