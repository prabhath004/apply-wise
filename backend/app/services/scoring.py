import json
from typing import Protocol

from pydantic import ValidationError

from app.core.errors import AppError
from app.schemas.analysis import FitScore, ScoreBreakdown
from app.schemas.job import JobInput
from app.schemas.job import ParsedJob
from app.schemas.resume import ParsedResumeProfile
from app.utils.text import canonical_skill, flatten_skill_groups


class JsonCompletionClient(Protocol):
    async def json_completion(self, system_prompt: str, user_prompt: str) -> dict:
        pass


def _truncate(value: str, limit: int = 12000) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "\n[Truncated for model context]"


def recommendation_for_score(score: int) -> str:
    if score >= 85:
        return "Strong Apply"
    if score >= 70:
        return "Apply"
    if score >= 55:
        return "Maybe"
    return "Low Fit"


def score_fit(resume: ParsedResumeProfile, job: ParsedJob) -> FitScore:
    resume_skills = set(flatten_skill_groups(resume.skills.model_dump()))
    required_skills = {canonical_skill(skill) for skill in job.required_skills}

    if required_skills:
        matching = sorted(resume_skills & required_skills)
        missing = sorted(required_skills - resume_skills)
        skills_score = round((len(matching) / len(required_skills)) * 100)
    else:
        matching = []
        missing = []
        skills_score = 50

    has_resume_evidence = bool(resume.experience or resume.projects or resume.skills.model_dump())
    experience_score = 72 if has_resume_evidence else 45
    if job.years_experience_min and job.years_experience_min >= 5:
        experience_score = min(experience_score, 55)

    if job.seniority in {"entry_level", "internship", None}:
        seniority_score = 82
    elif job.seniority == "senior":
        seniority_score = 45
    else:
        seniority_score = 65

    education_score = 85 if resume.education else 55
    domain_score = 75 if job.domain == "software" and resume_skills else 55

    if job.clearance_required:
        seniority_score = min(seniority_score, 50)

    overall = round(
        skills_score * 0.40
        + experience_score * 0.25
        + seniority_score * 0.15
        + education_score * 0.10
        + domain_score * 0.10
    )

    strengths = []
    if matching:
        strengths.append(f"Resume matches key skills: {', '.join(matching[:6])}.")
    if resume.education:
        strengths.append("Resume includes education evidence relevant to early-career technical roles.")
    if has_resume_evidence:
        strengths.append("Resume includes technical skills or project evidence that can support the application.")

    risks = []
    if missing:
        risks.append(f"Required skills not clearly found on the resume: {', '.join(missing[:6])}.")
    if job.clearance_required:
        risks.append("The job mentions clearance requirements, which may limit eligibility.")
    if job.visa_signals.mentions_no_sponsorship or job.visa_signals.mentions_us_citizenship:
        risks.append("The job description includes work authorization language that should be reviewed carefully.")

    return FitScore(
        overall=overall,
        recommendation=recommendation_for_score(overall),
        breakdown=ScoreBreakdown(
            skills=skills_score,
            experience=experience_score,
            seniority=seniority_score,
            domain=domain_score,
            education=education_score,
        ),
        matching_skills=matching,
        missing_skills=missing,
        strengths=strengths,
        risks=risks,
    )


async def score_fit_with_openai(
    llm_client: JsonCompletionClient,
    resume_text: str,
    parsed_resume: ParsedResumeProfile,
    job_input: JobInput,
    parsed_job: ParsedJob,
    local_score: FitScore,
) -> FitScore:
    system_prompt = """
You are a careful job-fit evaluator for an early-career technical job seeker.
Return only valid JSON. Do not include markdown.

You must evaluate holistic fit, not keyword overlap alone. Consider:
- required and preferred skills
- responsibilities and likely day-to-day work
- relevant experience, internships, projects, and transferable evidence
- seniority and years of experience expectations
- education signals
- domain alignment
- visa, citizenship, sponsorship, or clearance risks if present in the job text

Rules:
- Do not claim the candidate will get the job.
- Do not invent resume facts, company facts, or missing evidence.
- If evidence is weak, say so clearly in risks.
- Use recommendation thresholds exactly:
  85-100 Strong Apply
  70-84 Apply
  55-69 Maybe
  0-54 Low Fit
- Scores must be integers from 0 to 100.
- The breakdown must contain skills, experience, seniority, domain, and education.
- matching_skills and missing_skills should be concise arrays of strings.
- strengths and risks should be specific, evidence-based sentences.
""".strip()

    user_prompt = json.dumps(
        {
            "expected_json_shape": {
                "overall": 82,
                "recommendation": "Apply",
                "breakdown": {
                    "skills": 80,
                    "experience": 75,
                    "seniority": 85,
                    "domain": 70,
                    "education": 80,
                },
                "matching_skills": ["Python"],
                "missing_skills": ["Kubernetes"],
                "strengths": ["Specific evidence-backed strength."],
                "risks": ["Specific evidence-backed risk."],
            },
            "local_keyword_score_for_reference": local_score.model_dump(),
            "parsed_resume_for_reference": parsed_resume.model_dump(),
            "parsed_job_for_reference": parsed_job.model_dump(),
            "job": job_input.model_dump(),
            "resume_text": _truncate(resume_text),
        },
        ensure_ascii=True,
    )

    raw = await llm_client.json_completion(system_prompt, user_prompt)
    try:
        score = FitScore.model_validate(raw)
    except ValidationError as exc:
        raise AppError(
            "invalid_fit_score_response",
            "OpenAI returned a fit score that did not match the expected schema.",
            status_code=502,
        ) from exc

    expected_recommendation = recommendation_for_score(score.overall)
    if score.recommendation != expected_recommendation:
        score = score.model_copy(update={"recommendation": expected_recommendation})
    return score
