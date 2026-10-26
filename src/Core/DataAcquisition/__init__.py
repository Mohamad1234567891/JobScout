"""JobScout data acquisition package.

Fetches job listings from LinkedIn (plain impersonated HTTP first, headless
browser fallback) and extracts the important fields of every job: title,
company, location, posted date, employment type, seniority, and the
requirements the employer asks for (experience, education, certificates).
"""
