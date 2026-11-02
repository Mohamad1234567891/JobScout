
from job_matcher import (
    score_experience,
    score_skills,
    score_education,
    score_certificates,
    score_languages,
    match_job
)


def run_test(name, actual, expected):
    status = "PASSED" if actual == expected else "FAILED"

    print(f"\n[{status}] {name}")
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")

    return actual == expected


def main():

    passed = 0
    failed = 0

    def check(name, actual, expected):
        nonlocal passed, failed

        if run_test(name, actual, expected):
            passed += 1
        else:
            failed += 1

    print("=" * 50)
    print("JOB MATCHER - TEST SUITE")
    print("=" * 50)

    # 1. Experience Tests
    print("\n--- EXPERIENCE TESTS ---")

    check("Experience exceeds requirement",
          score_experience(5, 3), 1.0)

    check("Experience is exactly half",
          score_experience(2, 4), 0.3)

    check("No experience required",
          score_experience(0, 0), 1.0)

    check("Missing user experience",
          score_experience(None, 3), None)

    check("Missing job requirement",
          score_experience(3, None), None)

    # 2. Skills Tests
    print("\n--- SKILLS TESTS ---")

    check("All skills match",
          score_skills(
              ["Python", "SQL"],
              ["Python", "SQL"]
          ), 1.0)

    check("One exact and one missing skill",
          score_skills(
              ["Python"],
              ["Python", "SQL"]
          ), 0.5)

    check("Related skill match",
          score_skills(
              ["PyTorch"],
              ["TensorFlow"],
              {"tensorflow": ["pytorch"]}
          ), 0.5)

    check("Empty requirements",
          score_skills(["Python"], []), None)

    check("Duplicate requirements ignored",
          score_skills(
              ["Python"],
              ["Python", "Python", "SQL"]
          ), 0.5)

    # 3. Education Tests
    print("\n--- EDUCATION TESTS ---")

    check("Exact education match",
          score_education(
              "Bachelor", "Computer Science",
              "Bachelor", "Computer Science"
          ), 1.0)

    check("One level below, same field",
          score_education(
              "Bachelor", "Computer Science",
              "Master", "Computer Science"
          ), 0.75)

    check("Higher education level",
          score_education(
              "PhD", "Computer Science",
              "Bachelor", "Computer Science"
          ), 1.0)

    check("Missing education",
          score_education(
              None, None, "Bachelor", "Computer Science"
          ), None)

    # 4. Certificates Tests
    print("\n--- CERTIFICATE TESTS ---")

    check("Exact certificate match",
          score_certificates(
              ["AWS Cloud Practitioner"],
              ["AWS Cloud Practitioner"]
          ), 1.0)

    check("Related certificate match",
          score_certificates(
              ["AWS Solutions Architect"],
              ["AWS Cloud Practitioner"],
              {
                  "aws cloud practitioner": [
                      "aws solutions architect"
                  ]
              }
          ), 0.5)

    check("Missing certificate",
          score_certificates(
              ["Google Certificate"],
              ["AWS Certificate"]
          ), 0.0)

    # 5. Language Tests
    print("\n--- LANGUAGE TESTS ---")

    check("Exact language level",
          score_languages(
              [("English", "Fluent")],
              [("English", "Fluent")]
          ), 1.0)

    check("One level below",
          score_languages(
              [("English", "Conversational")],
              [("English", "Fluent")]
          ), 0.5)

    check("Language not listed by user",
          score_languages(
              [("Arabic", "Native")],
              [("English", "Fluent")]
          ), 0.0)

    check("Language requirement without level",
          score_languages(
              [("English", "Basic")],
              [("English", None)]
          ), 1.0)

    # 6. Complete Job Matching Tests
    print("\n--- MATCH JOB TESTS ---")

    result = match_job(
        user_experience=3,
        required_experience=3,
        user_skills=["Python", "SQL"],
        required_skills=["Python", "SQL"],
        user_education_level="Bachelor",
        user_education_field="Computer Science",
        required_education_level="Bachelor",
        required_education_field="Computer Science",
        user_certificates=["AWS Certificate"],
        required_certificates=["AWS Certificate"],
        user_languages=[("English", "Fluent")],
        required_languages=[("English", "Fluent")]
    )

    check("All criteria match",
          result["match_percentage"], 100.0)

    check("All individual scores match",
          all(score == 100.0 for score in result["breakdown"].values()),
          True)

    # Missing criteria should be ignored
    result_missing = match_job(
        user_experience=3,
        required_experience=3,
        user_skills=None,
        required_skills=None,
        user_education_level=None,
        user_education_field=None,
        required_education_level=None,
        required_education_field=None,
        user_certificates=None,
        required_certificates=None,
        user_languages=None,
        required_languages=None
    )

    check("Missing criteria are ignored",
          result_missing["match_percentage"], 100.0)

    check("Unavailable breakdown values are None",
          all(
              score is None
              for name, score in result_missing["breakdown"].items()
              if name != "experience"
          ), True)

    # No available criteria
    result_empty = match_job(
        None, None,
        None, None,
        None, None, None, None,
        None, None,
        None, None
    )

    check("No available criteria",
          result_empty["match_percentage"], None)

    # Final Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")

    if failed == 0:
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed. Review the results above.")


if __name__ == "__main__":
    main()
