import re
from collections import Counter


EMAIL_RE = re.compile(r"\b([a-z0-9._%+-]+)@([a-z0-9.-]+\.[a-z]{2,})\b", re.IGNORECASE)


def infer_pattern(email: str, first_name: str | None = None, last_name: str | None = None) -> str | None:
    local = email.split("@", 1)[0].lower()
    first = (first_name or "").lower()
    last = (last_name or "").lower()

    if first and last:
        if local == f"{first}.{last}":
            return "first.last"
        if local == f"{first}{last}":
            return "firstlast"
        if local == f"{first[0]}{last}":
            return "first_initial_last"
        if local == first:
            return "first"

    if "." in local:
        return "first.last"
    if len(local) > 2 and local[0].isalpha():
        return "unknown"
    return None


def extract_public_emails(text: str, domain: str | None = None) -> list[str]:
    found = []
    for local, email_domain in EMAIL_RE.findall(text):
        email = f"{local}@{email_domain}".lower()
        if not domain or email_domain.lower() == domain.lower():
            found.append(email)
    return sorted(set(found))


def dominant_pattern(emails: list[str]) -> tuple[str | None, int]:
    patterns = [pattern for email in emails if (pattern := infer_pattern(email))]
    if not patterns:
        return None, 0
    pattern, count = Counter(patterns).most_common(1)[0]
    confidence = 70 if count >= 2 else 50
    return pattern, confidence


def generate_email_from_pattern(first_name: str, last_name: str, domain: str, pattern: str) -> str | None:
    first = first_name.lower()
    last = last_name.lower()
    if pattern == "first.last":
        return f"{first}.{last}@{domain}"
    if pattern == "firstlast":
        return f"{first}{last}@{domain}"
    if pattern == "first_initial_last":
        return f"{first[0]}{last}@{domain}"
    if pattern == "first":
        return f"{first}@{domain}"
    return None
