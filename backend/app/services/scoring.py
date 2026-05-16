from app.schemas.analysis import FitScore, ScoreBreakdown
from app.schemas.job import ParsedJob
from app.schemas.resume import ParsedResumeProfile
from app.utils.text import canonical_skill, flatten_skill_groups


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
