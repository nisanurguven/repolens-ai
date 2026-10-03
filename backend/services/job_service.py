import re
from io import BytesIO
from pypdf import PdfReader

MAX_PDF_SIZE = 5 * 1024 * 1024


SKILL_PATTERNS = {
    "React": [
        r"\breact(?:\.js)?\b"
    ],

    "JavaScript": [
        r"\bjavascript\b",
        r"\bjs\b"
    ],

    "TypeScript": [
        r"\btypescript\b",
        r"\bts\b"
    ],

    "HTML": [
        r"\bhtml5?\b"
    ],

    "CSS": [
        r"\bcss3?\b"
    ],

    "Python": [
        r"\bpython\b"
    ],

    "FastAPI": [
        r"\bfastapi\b"
    ],

    "Django": [
        r"\bdjango\b"
    ],

    "Flask": [
        r"\bflask\b"
    ],

    "Node.js": [
        r"\bnode(?:\.js)?\b"
    ],

    "Express": [
        r"\bexpress(?:\.js)?\b"
    ],

    "Next.js": [
        r"\bnext(?:\.js)?\b"
    ],

    "Vue": [
        r"\bvue(?:\.js)?\b"
    ],

    "Angular": [
        r"\bangular\b"
    ],

    "Java": [
        r"\bjava\b"
    ],

    "Kotlin": [
        r"\bkotlin\b"
    ],

    "C#": [
        r"\bc#\b",
        r"\bcsharp\b"
    ],

    ".NET": [
        r"\b\.net\b",
        r"\bdotnet\b"
    ],

    "SQL": [
        r"\bsql\b"
    ],

    "PostgreSQL": [
        r"\bpostgresql\b",
        r"\bpostgres\b"
    ],

    "MySQL": [
        r"\bmysql\b"
    ],

    "MongoDB": [
        r"\bmongodb\b"
    ],

    "Redis": [
        r"\bredis\b"
    ],

    "SQLAlchemy": [
        r"\bsqlalchemy\b"
    ],

    "Docker": [
        r"\bdocker\b"
    ],

    "Kubernetes": [
        r"\bkubernetes\b",
        r"\bk8s\b"
    ],

    "Git": [
        r"\bgit\b"
    ],

    "GitHub Actions": [
        r"\bgithub actions\b"
    ],

    "CI/CD": [
        r"\bci\s*/\s*cd\b",
        r"\bcontinuous integration\b",
        r"\bcontinuous delivery\b",
        r"\bcontinuous deployment\b"
    ],

    "REST API": [
        r"\brest(?:ful)?\s+api\b",
        r"\brest(?:ful)?\s+apis\b",
        r"\brest\b"
    ],

    "GraphQL": [
        r"\bgraphql\b"
    ],

    "AWS": [
        r"\baws\b",
        r"\bamazon web services\b"
    ],

    "Azure": [
        r"\bazure\b"
    ],

    "Google Cloud": [
        r"\bgcp\b",
        r"\bgoogle cloud\b"
    ],

    "Jest": [
        r"\bjest\b"
    ],

    "Vitest": [
        r"\bvitest\b"
    ],

    "Pytest": [
        r"\bpytest\b"
    ],

    "Cypress": [
        r"\bcypress\b"
    ],

    "Playwright": [
        r"\bplaywright\b"
    ],

    "Testing": [
        r"\bautomated testing\b",
        r"\bunit testing\b",
        r"\bintegration testing\b",
        r"\btest automation\b"
    ],

    "Redux": [
        r"\bredux\b"
    ],

    "Zustand": [
        r"\bzustand\b"
    ],

    "TanStack Query": [
        r"\btanstack query\b",
        r"\breact query\b"
    ],

    "Tailwind CSS": [
        r"\btailwind(?:\s+css)?\b"
    ]
}


PREFERRED_KEYWORDS = {
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "plus",
    "advantage",
    "optional",
    "tercihen",
    "tercih sebebi",
    "artı",
    "avantaj"
}


ROLE_PATTERNS = {
    "Frontend Developer": [
        r"\bfrontend developer\b",
        r"\bfront-end developer\b",
        r"\bfrontend engineer\b"
    ],

    "Backend Developer": [
        r"\bbackend developer\b",
        r"\bback-end developer\b",
        r"\bbackend engineer\b"
    ],

    "Full Stack Developer": [
        r"\bfull[\s-]?stack developer\b",
        r"\bfull[\s-]?stack engineer\b"
    ],

    "Software Engineer": [
        r"\bsoftware engineer\b"
    ],

    "Software Developer": [
        r"\bsoftware developer\b"
    ],

    "React Developer": [
        r"\breact developer\b"
    ],

    "Python Developer": [
        r"\bpython developer\b"
    ],

    "Mobile Developer": [
        r"\bmobile developer\b",
        r"\bandroid developer\b"
    ]
}


RELATED_SKILLS = {
    "REST API": {
        "FastAPI",
        "Express",
        "Django",
        "Flask"
    },

    "Testing": {
        "Automated Testing",
        "Jest",
        "Vitest",
        "Pytest",
        "Cypress",
        "Playwright"
    },

    "CI/CD": {
        "GitHub Actions"
    }
}


def extract_pdf_text(
    file_bytes: bytes
):
    if len(file_bytes) > MAX_PDF_SIZE:
        raise ValueError(
            "PDF file must be smaller than 5 MB."
        )

    try:
        reader = PdfReader(
            BytesIO(file_bytes)
        )
    except Exception as error:
        raise ValueError(
            "The uploaded PDF could not be read."
        ) from error

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    result = "\n".join(pages).strip()

    if not result:
        raise ValueError(
            "No readable text was found in the PDF. "
            "Scanned image-only PDFs are not supported yet."
        )

    return result


def clean_lines(text: str):
    return [
        line.strip(" \t•-*")
        for line in text.splitlines()
        if line.strip()
    ]


def detect_job_title(
    text: str
):
    search_area = "\n".join(
        clean_lines(text)[:20]
    ).lower()

    for role, patterns in ROLE_PATTERNS.items():
        for pattern in patterns:
            if re.search(
                pattern,
                search_area,
                re.IGNORECASE
            ):
                return role

    return "Unknown Role"


def detect_skills(
    text: str
):
    required = {}
    preferred = {}

    lines = clean_lines(text)

    current_section = "required"

    required_headers = {
        "required",
        "required skills",
        "requirements",
        "qualifications",
        "must have",
        "must-have",
        "zorunlu",
        "gereksinimler",
        "aranan nitelikler"
    }

    preferred_headers = {
        "preferred",
        "preferred skills",
        "nice to have",
        "nice-to-have",
        "bonus",
        "optional",
        "tercihen",
        "tercih edilen",
        "artı özellikler"
    }

    for line in lines:
        lower_line = (
            line.lower()
            .strip()
            .rstrip(":")
        )

        if lower_line in required_headers:
            current_section = "required"
            continue

        if lower_line in preferred_headers:
            current_section = "preferred"
            continue

        contains_preferred_keyword = any(
            keyword in lower_line
            for keyword in PREFERRED_KEYWORDS
        )

        for skill, patterns in SKILL_PATTERNS.items():
            matched = any(
                re.search(
                    pattern,
                    line,
                    re.IGNORECASE
                )
                for pattern in patterns
            )

            if not matched:
                continue

            if (
                current_section == "preferred"
                or contains_preferred_keyword
            ):
                target = preferred
            else:
                target = required

            if skill not in target:
                target[skill] = []

            if line not in target[skill]:
                target[skill].append(
                    line
                )

    for skill in list(preferred):
        if skill in required:
            del preferred[skill]

    return {
        "required": required,
        "preferred": preferred
    }


def detect_experience(
    text: str
):
    patterns = [
        r"(\d+)\s*\+\s*(?:years?|yrs?|yıl)",
        r"(\d+)\s*(?:years?|yrs?|yıl)",
        r"(\d+)\s*[-–]\s*(\d+)\s*(?:years?|yrs?|yıl)"
    ]

    matches = []

    for pattern in patterns:
        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE
        ):
            values = [
                int(value)
                for value in match.groups()
                if value
            ]

            if values:
                matches.append(
                    {
                        "text": match.group(0),
                        "minimum_years": min(
                            values
                        )
                    }
                )

    if not matches:
        return {
            "minimum_years": None,
            "evidence": []
        }

    minimum_years = max(
        item["minimum_years"]
        for item in matches
    )

    return {
        "minimum_years": minimum_years,
        "evidence": [
            item["text"]
            for item in matches[:5]
        ]
    }


def detect_education(
    text: str
):
    keywords = {
        "bachelor",
        "bachelor's",
        "degree",
        "university",
        "computer science",
        "software engineering",
        "computer engineering",
        "related field",
        "lisans",
        "üniversite",
        "bilgisayar mühendisliği",
        "yazılım mühendisliği",
        "ilgili bölüm"
    }

    results = []

    for line in clean_lines(text):
        lower_line = line.lower()

        if any(
            keyword in lower_line
            for keyword in keywords
        ):
            results.append(line)

    return results[:5]


def detect_responsibilities(
    text: str
):
    action_words = {
        "develop",
        "build",
        "design",
        "implement",
        "maintain",
        "collaborate",
        "create",
        "optimize",
        "integrate",
        "test",
        "deliver",
        "geliştir",
        "tasarla",
        "uygula",
        "oluştur",
        "bakım",
        "iş birliği",
        "entegre",
        "test"
    }

    results = []

    for line in clean_lines(text):
        lower_line = line.lower()

        if not (
            20 <= len(line) <= 300
        ):
            continue

        if any(
            word in lower_line
            for word in action_words
        ):
            results.append(line)

    return results[:8]


def analyze_job_description(
    text: str
):
    cleaned_text = text.strip()

    if len(cleaned_text) < 40:
        raise ValueError(
            "Job description is too short to analyze."
        )

    skills = detect_skills(
        cleaned_text
    )

    experience = detect_experience(
        cleaned_text
    )

    return {
        "job_title": detect_job_title(
            cleaned_text
        ),

        "required_skills": list(
            skills["required"].keys()
        ),

        "preferred_skills": list(
            skills["preferred"].keys()
        ),

        "skill_evidence": {
            "required":
                skills["required"],

            "preferred":
                skills["preferred"]
        },

        "experience": experience,

        "education": detect_education(
            cleaned_text
        ),

        "responsibilities":
            detect_responsibilities(
                cleaned_text
            ),

        "text_length": len(
            cleaned_text
        )
    }


def normalize_profile_skills(
    profile: dict
):
    return {
        skill.get("name")
        for skill in profile.get(
            "skills",
            []
        )
        if skill.get("name")
    }


def find_partial_match(
    required_skill: str,
    profile_skills: set
):
    related = RELATED_SKILLS.get(
        required_skill,
        set()
    )

    found = sorted(
        related.intersection(
            profile_skills
        )
    )

    return found


def build_project_recommendations(
    missing_skills: list[str],
    known_skills: set
):
    ideas = []

    missing = set(
        missing_skills
    )

    if (
        "TypeScript" in missing
        or "React" in missing
    ):
        ideas.append(
            {
                "title":
                    "Typed Product Dashboard",

                "description": (
                    "Build a production-style dashboard "
                    "with typed API responses, reusable "
                    "components and form validation."
                ),

                "targets": [
                    skill
                    for skill in [
                        "React",
                        "TypeScript"
                    ]
                    if skill in missing
                ],

                "technologies": [
                    "React",
                    "TypeScript",
                    "REST API"
                ]
            }
        )

    if (
        "PostgreSQL" in missing
        or "SQL" in missing
    ):
        ideas.append(
            {
                "title":
                    "Data-Driven SaaS API",

                "description": (
                    "Build an application with relational "
                    "data, authentication and a REST API."
                ),

                "targets": [
                    skill
                    for skill in [
                        "SQL",
                        "PostgreSQL"
                    ]
                    if skill in missing
                ],

                "technologies": [
                    "FastAPI",
                    "PostgreSQL",
                    "SQLAlchemy"
                ]
            }
        )

    if (
        "Docker" in missing
        or "CI/CD" in missing
        or "GitHub Actions" in missing
    ):
        ideas.append(
            {
                "title":
                    "Production Deployment Pipeline",

                "description": (
                    "Containerize an existing full-stack "
                    "project and create an automated "
                    "build and test pipeline."
                ),

                "targets": [
                    skill
                    for skill in [
                        "Docker",
                        "CI/CD",
                        "GitHub Actions"
                    ]
                    if skill in missing
                ],

                "technologies": [
                    "Docker",
                    "GitHub Actions",
                    "CI/CD"
                ]
            }
        )

    if (
        "Testing" in missing
        or "Jest" in missing
        or "Vitest" in missing
        or "Pytest" in missing
    ):
        ideas.append(
            {
                "title":
                    "Test-Driven Feature Lab",

                "description": (
                    "Take an existing project and add "
                    "unit, integration and API tests."
                ),

                "targets": [
                    skill
                    for skill in [
                        "Testing",
                        "Jest",
                        "Vitest",
                        "Pytest"
                    ]
                    if skill in missing
                ],

                "technologies": [
                    "Testing",
                    "GitHub Actions"
                ]
            }
        )

    if not ideas and missing_skills:
        ideas.append(
            {
                "title":
                    "Target Skill Portfolio Project",

                "description": (
                    "Build a focused portfolio project "
                    "that demonstrates the highest-priority "
                    "skills missing from the target role."
                ),

                "targets":
                    missing_skills[:4],

                "technologies":
                    missing_skills[:4]
            }
        )

    return ideas[:3]


def compare_profile_with_job(
    profile: dict,
    job_analysis: dict
):
    profile_skills = (
        normalize_profile_skills(
            profile
        )
    )

    required_skills = (
        job_analysis.get(
            "required_skills",
            []
        )
    )

    preferred_skills = (
        job_analysis.get(
            "preferred_skills",
            []
        )
    )

    matched_required = []
    partial_required = []
    missing_required = []

    for skill in required_skills:
        if skill in profile_skills:
            matched_required.append(
                skill
            )

            continue

        related_matches = (
            find_partial_match(
                skill,
                profile_skills
            )
        )

        if related_matches:
            partial_required.append(
                {
                    "skill": skill,
                    "related_evidence":
                        related_matches
                }
            )
        else:
            missing_required.append(
                skill
            )

    matched_preferred = [
        skill
        for skill in preferred_skills
        if skill in profile_skills
    ]

    missing_preferred = [
        skill
        for skill in preferred_skills
        if skill not in profile_skills
    ]

    required_total = len(
        required_skills
    )

    coverage_score = 0

    if required_total:
        coverage_score = round(
            (
                len(matched_required)
                + (
                    len(
                        partial_required
                    ) * 0.5
                )
            )
            / required_total
            * 100
        )

    learning_priorities = (
        missing_required
        + [
            item["skill"]
            for item in partial_required
        ]
        + missing_preferred
    )

    unique_priorities = list(
        dict.fromkeys(
            learning_priorities
        )
    )

    return {
        "job_title": job_analysis.get(
            "job_title",
            "Unknown Role"
        ),

        "required_skill_coverage":
            coverage_score,

        "matched_required":
            matched_required,

        "partial_required":
            partial_required,

        "missing_required":
            missing_required,

        "matched_preferred":
            matched_preferred,

        "missing_preferred":
            missing_preferred,

        "learning_priorities":
            unique_priorities[:8],

        "project_recommendations":
            build_project_recommendations(
                missing_required,
                profile_skills
            )
    }