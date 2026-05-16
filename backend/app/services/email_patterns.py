import re
from collections import Counter
from dataclasses import dataclass


EMAIL_RE = re.compile(r"\b([a-z0-9._%+-]+)@([a-z0-9.-]+\.[a-z]{2,})\b", re.IGNORECASE)
GENERIC_LOCAL_PARTS = {
    "admin",
    "careers",
    "contact",
    "hello",
    "hr",
    "info",
    "jobs",
    "legal",
    "media",
    "noreply",
    "no-reply",
    "press",
    "privacy",
    "recruiting",
    "sales",
    "security",
    "support",
}


@dataclass(frozen=True)
class EmailPatternEvidence:
    pattern: str | None
    confidence: int
    count: int
    total: int
    samples: list[str]
    reason: str | None


def infer_pattern(email: str, first_name: str | None = None, last_name: str | None = None) -> str | None:
    local = email.split("@", 1)[0].lower()
    if local in GENERIC_LOCAL_PARTS:
        return None

    first = (first_name or "").lower()
    last = (last_name or "").lower()

    if first and last:
        if local == f"{first}.{last}":
            return "first.last"
        if local == f"{first}_{last}":
            return "first_last"
        if local == f"{first}-{last}":
            return "first-last"
        if local == f"{first}{last}":
            return "firstlast"
        if local == f"{first[0]}{last}":
            return "first_initial_last"
        if local == first:
            return "first"

    if "." in local:
        return "first.last"
    if "_" in local:
        return "first_last"
    if "-" in local:
        return "first-last"
    if len(local) > 2 and local[0].isalpha():
        return "unknown"
    return None


def extract_public_emails(text: str, domain: str | None = None) -> list[str]:
    found = []
    for local, email_domain in EMAIL_RE.findall(text):
        email = f"{local}@{email_domain}".lower()
        if local.lower() in GENERIC_LOCAL_PARTS:
            continue
        if not domain or email_domain.lower() == domain.lower():
            found.append(email)
    return sorted(set(found))


def dominant_pattern_evidence(emails: list[str]) -> EmailPatternEvidence:
    usable = [email for email in sorted(set(emails)) if infer_pattern(email) not in (None, "unknown")]
    patterns = [pattern for email in usable if (pattern := infer_pattern(email))]
    if not patterns:
        return EmailPatternEvidence(None, 0, 0, len(set(emails)), [], None)

    pattern, count = Counter(patterns).most_common(1)[0]
    samples = [email for email in usable if infer_pattern(email) == pattern][:5]
    if count >= 5:
        confidence = 90
    elif count >= 3:
        confidence = 85
    elif count >= 2:
        confidence = 75
    else:
        confidence = 55

    reason = f"Company uses {pattern} format based on {count} public employee email{'s' if count != 1 else ''}."
    return EmailPatternEvidence(pattern, confidence, count, len(set(emails)), samples, reason)


def dominant_pattern(emails: list[str]) -> tuple[str | None, int]:
    evidence = dominant_pattern_evidence(emails)
    return evidence.pattern, evidence.confidence


def generate_email_from_pattern(first_name: str, last_name: str, domain: str, pattern: str) -> str | None:
    first = first_name.lower()
    last = last_name.lower()
    if pattern == "first.last":
        return f"{first}.{last}@{domain}"
    if pattern == "first_last":
        return f"{first}_{last}@{domain}"
    if pattern == "first-last":
        return f"{first}-{last}@{domain}"
    if pattern == "firstlast":
        return f"{first}{last}@{domain}"
    if pattern == "first_initial_last":
        return f"{first[0]}{last}@{domain}"
    if pattern == "first":
        return f"{first}@{domain}"
    return None
