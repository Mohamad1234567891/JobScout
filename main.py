"""JobScout data-acquisition smoke test.

No GUI or CLI yet: this driver stands in for the app's job search space.
It takes a hardcoded user input (the job the user is searching for), runs the
LinkedIn scraping pipeline, and prints the important extracted fields of
every job found.
"""

import asyncio
import time

from src.Core.DataAcquisition import scraper

# ---------------------------------------------------------------------------
# Stand-in for the app's job search space. In the future the GUI will collect
# the job title, the user's experience and education degree etc.; the data
# acquisition only needs the job title to search.
# ---------------------------------------------------------------------------
USER_SEARCH_INPUT = "AI Engineer"


def _print_list(items):
    """Prints a list of extracted values as readable bullet points."""
    if items:
        for item in items:
            print(f"      - {item}")
    else:
        print("      - (none found)")


def print_job(job, number):
    """Prints the important fields of one extracted job."""
    print("=" * 78)
    print(f"JOB #{number}")
    print("=" * 78)
    print(f"  Job title:     {job.get('job_title') or 'N/A'}")
    print(f"  Company:       {job.get('company_name') or 'N/A'}")
    print(f"  Location:      {job.get('location') or 'N/A'}")
    print(f"  Posted:        {job.get('posted_date') or job.get('posted_time_ago') or 'N/A'}"
          + (f" (at {job['posted_at']})" if job.get("posted_at") else ""))
    print(f"  Applicants:    {job.get('applicants') or 'N/A'}")
    print(f"  Seniority:     {job.get('seniority_level') or 'N/A'}")
    print(f"  Employment:    {job.get('employment_type') or 'N/A'}")
    if job.get("industries"):
        print(f"  Industries:    {job['industries']}")
    print(f"  Job id:        {job.get('job_id') or 'N/A'}")
    print(f"  URL:           {job.get('job_url') or 'N/A'}")

    if job.get("failed"):
        print("  (the job page could not be fetched - only listing data is shown)")
        return

    if job.get("requires_login"):
        print("  (this posting requires a LinkedIn sign-in to view - only listing data is shown)")
        return

    print("  Employer requires:")
    print("    Experience: ")
    _print_list(job.get("experience_requirements") or [])
    print("    Education: ")
    _print_list(job.get("education_requirements") or [])
    print("    Certificates: ")
    _print_list(job.get("certificates") or [])
    print("    Skills (mentioned): ")
    if job.get("skills"):
        print(f"      - {', '.join(job['skills'])}")
    else:
        print("      - (none found)")

    description = job.get("description") or ""
    print(f"  Description:   {description[:400]}{'...' if len(description) > 400 else ''}")
    print()


async def main():
    start_time = time.perf_counter()

    jobs, stats = await scraper.scrape_search_space(USER_SEARCH_INPUT)

    print()
    if jobs:
        for number, job in enumerate(jobs, start=1):
            print_job(job, number)
        print(f"[+] Done: {len(jobs)} jobs found for '{USER_SEARCH_INPUT}'.")
    else:
        print("[-] No jobs were found.")

    if stats:
        print(f"[*] Crawling session: {time.perf_counter() - start_time:.1f}s "
              f"({stats['http']} fast requests, {stats['browser']} browser pages).")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[!] Stopped by user.")
