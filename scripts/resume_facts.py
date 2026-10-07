"""resume_facts.py - read candidate facts straight out of the PINNED RESUME PDF.

THE SINGLE SOURCE OF TRUTH
--------------------------
The candidate's own resume PDF is the only admissible source of candidate facts.
`candidate-profile.json` names that file and its SHA256 and holds nothing else.
There is no Word profile, no pre-extracted text file, no cached report: the PDF is
read at runtime, every time, by this module.

`kilo-bridge-setup.ps1 -Launch` verifies the hash and calls report() for its preflight.
The PDF is not attached to the agent; lanes call candidate_fact() / candidate_skills()
to parse it at runtime. One command, one source, no sidecar facts.

WHY PDF TEXT IS PARSED RATHER THAN STORED
-----------------------------------------
Storing the facts anywhere else would create a second source of truth that drifts
from the document the candidate actually maintains. So this module locates each
fact by a STRUCTURAL ANCHOR in the document and never stores a candidate value of
its own. If an anchor is absent the fact is UNCONFIRMED, the key is simply missing
from the returned dict, and the caller must treat it as BLOCKED.

PDF PARSING
-----------
pypdf. It is verified by the launcher before the mission starts (see
`require_pypdf`), because a resume is the one input that must never be half-read.
"""
from __future__ import annotations

import hashlib
import io
import re
import subprocess
import sys
from pathlib import Path

try:                                   # encoding-safe stdout (Windows cp1252)
    _previous_stdout = sys.stdout
    sys.stdout = io.TextIOWrapper(_previous_stdout.buffer, encoding="utf-8", errors="replace")
    _previous_stdout.detach()          # keep it from closing the shared buffer
except Exception:
    pass

SEP = "\u00b7"          # the header's middle-dot separator

# ---------------------------------------------------------------------------
# Anchors. Document SHAPE only - no candidate value appears anywhere below.
# ---------------------------------------------------------------------------

_AT = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PLUS_PHONE = re.compile(r"\+\d[\d\s\-]{6,}\d")
_NAME_LINE = re.compile(r"^([A-Z][A-Z]{2,}(?:[ ][A-Z][A-Z]{2,}){0,3})$", re.M)
_HEADLINE = re.compile(r"^(?:[A-Z][^\n|]{3,}\s*\|\s*){1,4}[A-Za-z][^\n|]{2,}$", re.M)
_YEARS = re.compile(r"(\d{2})\+?\s*(?:years|yrs)", re.I)
# How a resume separates items inside one line: commas, the middot the header and
# the stacks use, and a SPACED slash. A bare slash is never a separator.
_SPLIT_ITEMS = re.compile(r"[,;·]")

# Grid headings and layout words that are structure, not skills.
_NOT_A_SKILL = {"ai", "domains", "skills", "stack", "top skills", "domain",
                "core competencies", "competencies", "leadership & strategy"}

# Long forms and near-duplicates folded onto the single term a posting uses.
# Keys are normalised the same way canonical() normalises a value: lowercase,
# punctuation collapsed to single spaces.
_CANONICAL = (
    (("retrieval augmented generation", "rag"), "RAG"),
    (("large language model", "llm"), "LLM"),
    (("generative ai", "genai"), "Generative AI"),
    (("vector database", "vector db"), "Vector Database"),
    (("agentic ai",), "Agentic AI"),
    (("ai agent",), "AI Agents"),
    (("apache hadoop", "hadoop"), "Hadoop"),
    (("microservices architecture",), "Microservices"),
    (("rest api",), "REST APIs"),
    (("natural language processing",), "NLP"),
    (("machine learning",), "Machine Learning"),
    (("node js", "nodejs"), "Node.js"),
    (("javascript",), "JavaScript"),
)
# Availability wording stops at the separator: 'Open to Remote only | Immediate
# Joiner' must yield the work model, not both fields.
_AVAIL = re.compile(r"(immediate joiner|available now)", re.I)
_MODEL = re.compile(r"open to\s+([^.\n|§]+)", re.I)
# A trailing availability clause is not part of the work model.
_MODEL_TAIL = re.compile(
    r"\s*(?:·|,)?\s*(?:immediate joiner|available now)\s*$", re.I)


def _text_lines(path):
    """Every visible text line of the document, in page order."""
    import pypdf

    reader = pypdf.PdfReader(str(path))
    lines = []
    for page in reader.pages:
        for line in (page.extract_text() or "").splitlines():
            line = line.strip()
            if line:
                lines.append(line)
    return lines, len(reader.pages)


def _contact_parts(lines):
    """Label the header line that carries the '@' separator-delimited chunks.

    Labels come from what each chunk IS, never from a hardcoded value: the chunk
    with '@' is the email, one beginning '+' is the phone, and so on. The order the
    operator writes them in does not matter.
    """
    parts = {}
    for line in lines:
        if "@" not in line or SEP not in line:
            continue
        for chunk in (c.strip() for c in line.split(SEP)):
            if not chunk:
                continue
            if _AT.search(chunk):
                parts["EMAIL"] = _AT.search(chunk).group(0)
            elif chunk.lstrip().startswith("+"):
                parts["PHONE"] = chunk
            elif re.match(r"^(open to|immediate|available)", chunk, re.I):
                parts.setdefault("AVAILABILITY", chunk)
            else:
                parts["LOCATION"] = chunk
    return parts


# Country calling codes this module knows how to split off the front of a number.
# This is international dialling knowledge, not a candidate value.
_COUNTRY_CODES = {
    "1": "US/CA", "7": "RU/KZ", "20": "EG", "27": "ZA", "30": "GR", "31": "NL",
    "32": "BE", "33": "FR", "34": "ES", "39": "IT", "40": "RO", "41": "CH",
    "43": "AT", "44": "GB", "45": "DK", "46": "SE", "47": "NO", "48": "PL",
    "49": "DE", "51": "PE", "52": "MX", "53": "CU", "54": "AR", "55": "BR",
    "56": "CL", "57": "CO", "58": "VE", "60": "MY", "61": "AU", "62": "ID",
    "63": "PH", "64": "NZ", "65": "SG", "66": "TH", "81": "JP", "82": "KR",
    "84": "VN", "86": "CN", "90": "TR", "91": "IN", "92": "PK", "93": "AF",
    "94": "LK", "95": "MM", "98": "IR", "211": "SS", "212": "MA", "213": "DZ",
    "216": "TN", "218": "LY", "220": "GM", "221": "SN", "233": "GH", "234": "NG",
    "251": "ET", "254": "KE", "255": "TZ", "256": "UG", "260": "ZM", "263": "ZW",
    "351": "PT", "352": "LU", "353": "IE", "358": "FI", "370": "LT", "371": "LV",
    "372": "EE", "380": "UA", "381": "RS", "385": "HR", "386": "SI", "420": "CZ",
    "421": "SK", "852": "HK", "853": "MO", "855": "KH", "856": "LA", "880": "BD",
    "886": "TW", "961": "LB", "962": "JO", "963": "SY", "964": "IQ", "965": "KW",
    "966": "SA", "967": "YE", "968": "OM", "971": "AE", "972": "IL", "973": "BH",
    "974": "QA", "975": "BT", "976": "MN", "977": "NP", "992": "TJ", "993": "TM",
    "994": "AZ", "995": "GE", "996": "KG", "998": "UZ",
}


def _split_phone(value):
    """(country code, subscriber number) from a +CC ... number string.

    The country code is matched against the real calling-code table, longest first,
    so '+91 ...' splits as India rather than being guessed from digit count.
    """
    match = _PLUS_PHONE.search(value or "")
    if not match:
        return None, None
    raw = re.sub(r"\s+", " ", match.group(0).strip())
    digits = re.sub(r"\D", "", raw)
    for length in (3, 2, 1):
        candidate = digits[:length]
        if candidate in _COUNTRY_CODES:
            # The subscriber number is the part AFTER the country code, with the
            # country's own trunk prefix (a leading 0 in most of Europe) removed.
            # The code is returned separately so a portal's country selector can be
            # set independently of the number field.
            local = digits[length:]
            while len(local) > 10 and local[0] == "0":
                local = local[1:]
            return "+" + candidate, local
    return None, raw


def _section(lines, heading):
    """Lines of a headed section, up to the next all-caps heading."""
    for index, line in enumerate(lines):
        if line.casefold() == heading.casefold():
            out = []
            for follow in lines[index + 1:]:
                if re.match(r"^[A-Z][A-Z &/.,-]{3,}$", follow) and len(follow.split()) <= 6:
                    break
                out.append(follow)
            return out
    return []


def _split_items(text):
    """Split one line of a resume into individual items.

    Commas, semicolons and the middot are always separators. A slash separates
    only when it is padded with spaces, because this resume writes 'CI/CD',
    'SQL/NoSQL' and 'NLP/NLG' without spaces and those are single terms. A
    parenthesised qualifier is unwrapped rather than treated as an item, so
    'AWS (EC2 / S3 / Lambda)' yields AWS, EC2, S3 and Lambda.
    """
    for chunk in _SPLIT_ITEMS.split(text):
        chunk = chunk.strip()
        if not chunk:
            continue
        head, sep, inner = chunk.partition("(")
        if sep and inner.endswith(")"):
            head = head.strip()
            if head:
                yield head
            for item in re.split(r"\s+/\s+", inner[:-1]):
                if item.strip():
                    yield item.strip()
            continue
        for item in re.split(r"\s+/\s+", chunk):
            if item.strip():
                yield item.strip()


def _skills(lines):
    """Skills, from the resume's own skill declarations.

    Anchors: the per-role 'Top Skills:' and 'Stack:' lines, and the CORE COMPETENCIES
    grid. Long forms are folded onto the term a job posting actually uses, so the
    match gate scores the way a recruiter reads. Nothing is added from outside the
    document.
    """
    found, seen = [], set()

    def canonical(value):
        low = re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()
        for keys, name in _CANONICAL:
            for key in keys:
                # Exact, plural ('LLMs'), or the key followed by a qualifier
                # ('RAG pipelines'). A bare prefix match would wrongly swallow
                # unrelated terms that merely start with the same letters.
                if low == key or low == key + "s" or low.startswith(key + " "):
                    return name, name.casefold()
        return value, low

    def add(value):
        value = re.sub(r"\s+", " ", value).strip(" .,-–—;")
        # An inline qualifier is context, not a separate skill: 'Team Leadership
        # (30+)' -> 'Team Leadership'. But keep a qualified acronym whole.
        qualifier = re.search(r"\(([^()]*)\)", value)
        if qualifier:
            inner = qualifier.group(1).strip()
            value = (value[:qualifier.start()] + qualifier.group(1)).strip()
        if len(value) < 3 or not re.search(r"[A-Za-z]", value):
            return
        if value.casefold() in _NOT_A_SKILL:
            return
        # A qualified form is both the base term and the qualified term.
        candidates = [value]
        base = re.sub(r"[^A-Za-z0-9+/&.\- ]+", "", value).strip(" .,-")
        if base and base != value:
            candidates.append(base)
        for candidate in candidates:
            name, key = canonical(candidate)
            if key and key not in seen:
                seen.add(key)
                found.append(name)

    # Split on the separators the resume actually uses. A BARE slash is part of
    # the term ('CI/CD', 'SQL/NoSQL', 'NLP/NLG') and is never a separator; only a
    # slash padded with spaces, as in 'AI / GenAI / Agentic AI', divides items.
    for line in lines:
        for label in ("Top Skills:", "Stack:"):
            if label in line:
                for chunk in _split_items(line.split(label, 1)[1]):
                    add(chunk)

    for line in _section(lines, "CORE COMPETENCIES"):
        for chunk in _split_items(line):
            add(chunk)

    return found


def facts(path) -> dict:
    """Every fact confirmable from the resume, as {KEY: value}.

    A key is absent when the document does not state it. There are no defaults and
    no fallbacks to any other file.
    """
    lines, _pages = _text_lines(path)
    blob = "\n".join(lines)
    out = {}

    contact = _contact_parts(lines)
    out.update({k: v for k, v in contact.items() if v})

    if contact.get("PHONE"):
        code, number = _split_phone(contact["PHONE"])
        if code:
            out["PHONE_COUNTRY_CODE"] = code
        if number:
            # Both forms are kept: the bare national number for a portal that
            # already has the country selected, and the E.164 form for one that
            # does not. Agents pick by what the field accepts.
            out["PHONE"] = number
            out["PHONE_E164"] = code + number

    for line in lines[:8]:                       # the name sits in the header block
        match = _NAME_LINE.match(line)
        if match and "@" not in line:
            out["NAME"] = " ".join(match.group(1).split()).title()
            break

    for line in lines[:8]:
        if "|" in line and not line.isupper():
            out.setdefault("HEADLINE", re.sub(r"\s+", " ", line).strip())
            break

    years = _YEARS.search(blob)
    if years:
        out["YEARS_EXPERIENCE"] = years.group(1)

    avail = _AVAIL.search(blob)
    if avail:
        out["AVAILABILITY"] = "Immediate Joiner" if "joiner" in avail.group(0).lower() else "Available Now"

    model = _MODEL.search(blob)
    if model:
        # 'Open to Remote only | Immediate Joiner' -> 'Open to Remote only'
        wording = re.sub(r"\s+", " ", model.group(1).replace(SEP, " "))
        wording = _MODEL_TAIL.sub("", wording).strip().strip(".,;")
        if wording:
            out["WORK_MODEL"] = "Open to " + wording

    education = _section(lines, "EDUCATION & CERTIFICATIONS")
    joined = "\n".join(education)
    degree = re.search(r"(?:B\.?Tech\.?|M\.?Tech\.?|B\.?E\.?|MBA|B\.?Sc\.?|Ph\.?D\.?)"
                       r"[^\n]*(?:Engineering|Science|Technology|Business)?", joined, re.I)
    if degree:
        out["EDUCATION_DEGREE"] = re.sub(r"\s+", " ", degree.group(0)).strip(" -–—|")
    institute = re.search(r"(?:University|Institute|College|School)[^\n|]*", joined)
    if institute:
        head = joined[:institute.start()]
        tail = head.splitlines()[-1] if head.splitlines() else ""
        name = (tail + institute.group(0)).strip(" ,|–—")
        if name:
            out["EDUCATION_INSTITUTE"] = re.sub(r"\s+", " ", name)
    year = re.search(r"\|\s*(\d{4})\b", joined) or re.search(r"\b(19|20)\d{2}\b", joined)
    if year:
        digits = re.search(r"\b((?:19|20)\d{2})\b", joined)
        if digits:
            out["EDUCATION_YEAR"] = digits.group(1)

    certs = re.findall(r"([A-Z][A-Za-z .+]+(?:Level\s*\d|\d{1,3}\s*/\s*\d{2,3}))", joined)
    if certs:
        out["CERTIFICATIONS"] = [re.sub(r"\s+", " ", c).strip() for c in certs]

    employers = []
    for line in lines:
        match = re.search(r"^(?:[A-Z][a-z]+\s+){1,2}([A-Z][A-Za-z&.]*(?:\s+[A-Z][A-Za-z&.]*){0,2})"
                          r"\s*(?:—|--|-|\|)", line)
        if match:
            value = match.group(1).strip()
            if len(value) > 2 and value not in employers:
                employers.append(value)
    if employers:
        out["EMPLOYERS"] = employers

    skills = _skills(lines)
    if skills:
        out["SKILL"] = skills
    return out


# ---------------------------------------------------------------------------
# Verification and reporting (called by the launcher preflight)
# ---------------------------------------------------------------------------

def verify(path, expected_sha256):
    """(ok, message) - the resume must exist and match the recorded hash."""
    path = Path(path)
    if not path.is_file():
        return False, "resume missing: %s" % path
    actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    return actual == str(expected_sha256).upper(), "resume sha256=%s" % actual


REPORT_KEYS = ("NAME", "PHONE", "PHONE_COUNTRY_CODE", "EMAIL", "LOCATION",
               "YEARS_EXPERIENCE", "AVAILABILITY", "WORK_MODEL",
               "EDUCATION_DEGREE", "EDUCATION_INSTITUTE", "EDUCATION_YEAR")


def report(path):
    """Confirmation table for the launcher preflight: fact or BLOCKED, per key."""
    found = facts(path)
    lines = []
    for key in REPORT_KEYS:
        value = found.get(key)
        lines.append("  %-22s %s" % (key, value if value else "UNCONFIRMED -> BLOCKED"))
    lines.append("  %-22s %d confirmed" % ("SKILLS", len(found.get("SKILL") or [])))
    lines.append("  %-22s %d found" % ("EMPLOYERS", len(found.get("EMPLOYERS") or [])))
    return "\n".join(lines)


def require_pypdf(python_executable=None):
    """(ok, message) - the mission refuses to read a resume it cannot fully parse."""
    try:
        import pypdf  # noqa: F401
        return True, "pypdf %s" % pypdf.__version__
    except ImportError:
        pass
    exe = python_executable or sys.executable
    try:
        subprocess.check_call([exe, "-m", "pip", "install", "--quiet", "pypdf"])
        import pypdf  # noqa: F401
        return True, "pypdf %s (installed)" % pypdf.__version__
    except Exception as exc:
        return False, "pypdf unavailable (%s). Install it with: %s -m pip install pypdf" % (exc, exe)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: resume_facts.py <resume.pdf>")
    print(report(sys.argv[1]))
