# Contribution Report — Abdulrab Almusali

**Student Name:** ABDULRAB ALMUSALI  
**Student ID:** 2409115801  
**GitHub Username:** AbdulrabAlmusali  
**Project:** JobScout

## 1. Job Matching and Scoring — `job_matcher.py`

My main contribution to JobScout is the Data Analysis component, which evaluates how well a user's profile matches the requirements of a job posting.

I implemented separate scoring functions for the main matching criteria:

- **`score_experience()`** — Compares the user's years of experience with the experience required by a job. It returns a score between 0.0 and 1.0 based on the proportion of the required experience. A job that requires zero years of experience receives a full experience score. Missing information is represented by `None` when the criterion cannot be evaluated.

- **`score_skills()`** — Compares the user's skills with the skills required by the job. Exact matches receive full credit, explicitly provided related skills receive partial credit, and unmatched requirements receive no credit.

- **`score_education()`** — Evaluates the user's education level and field against the job's education requirements. It considers the relative education level and whether the user's field matches the required field.

- **`score_certificates()`** — Compares the user's certificates with the certificates requested by the job. Exact matches receive full credit, explicitly related certificates receive partial credit, and missing certificates receive no credit.

- **`score_languages()`** — Compares the user's languages and proficiency levels with the job's language requirements. It considers the proficiency hierarchy of Basic, Conversational, Fluent, and Native, and accounts for required languages that are not listed in the user's profile.

For skills and certificates, I also implemented the shared helper function **`_score_named_requirements()`** to reuse the exact-match and related-match logic.

## 2. Overall Job Matching — `match_job()`

I implemented **`match_job()`** as the main function that combines the individual criterion scores and calculates an overall job-match percentage.

The function accepts the user's information and the job's requirements as separate parameters, rather than requiring the caller to pass complete profile or job dictionaries. This allows the rest of the project to provide the data to the analysis component when the modules are integrated.

The current prototype uses the following criterion weights:

| Criterion | Weight |
|---|---:|
| Experience | 0.30 |
| Skills | 0.28 |
| Education | 0.18 |
| Certificates | 0.08 |
| Languages | 0.08 |

The weights are normalized over the criteria that have available scores. Criteria that cannot be evaluated because information is missing are excluded from the calculation rather than automatically receiving a zero score.

The function returns:

- `match_percentage`: The overall job-fit percentage, or `None` if no criterion can be evaluated.
- `breakdown`: The individual percentage score for each criterion, with `None` for unavailable scores.

The percentage represents the degree of match between the available user information and the job requirements. It is not a probability of being hired.

## 3. Testing — `test_job_matcher.py`

I created a separate test file to verify the behavior of the scoring functions and the overall matching function.

The test suite covers:

- Experience comparisons, including missing information and jobs requiring no prior experience.
- Exact, related, missing, empty, and duplicate skill requirements.
- Education-level and education-field comparisons.
- Exact, related, and missing certificate requirements.
- Language proficiency comparisons and required languages missing from the user's profile.
- Overall match calculation, individual score breakdowns, and unavailable criteria.

**Test Result:** All 26 tests passed successfully, with 0 failures, during the test run.

## 4. Package Organization — `__init__.py`

I created the `__init__.py` file in the Data Analysis package to support organizing the directory as a Python package and to make package-based imports possible. The file does not require additional code for this basic purpose.

## 5. Libraries and Python Features Used

The implementation uses:

- **Python Standard Library**
  - `typing.Any`: Used for the return type annotation of the main matching function.

- **Python Type Hints**
  - Used to describe optional values, lists, tuples, dictionaries, and function return types.

- **Python Functions and Data Structures**
  - Used to separate the scoring logic into reusable functions and combine the results.

## 6. Scope of My Contribution

My assigned area is Data Analysis. My contribution covers the job-matching scoring logic, the overall match calculation, and the associated tests.

I am not claiming responsibility for the team's Data Acquisition, Notifications, or GUI implementation.

The scoring rules and weights documented here describe the current prototype implementation. Additional algorithm features discussed by the team, such as Must-have/Nice-to-have requirement handling and evidence-based adjustments, should only be described as implemented if they are added to my code and verified.

## 7. Key Contributions

My main contribution to JobScout was developing the Data Analysis logic used to compare a user's profile with job requirements.

Specifically, I implemented five criterion-specific scoring functions, a reusable helper for matching named requirements, and the `match_job()` function that calculates an overall match percentage with an individual score breakdown. I also created and ran a test suite containing 26 tests, all of which passed in the reported test run.

These components provide the project's job-matching functionality with a modular structure that can be called by other parts of the application during integration.