import json
import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-terra"
)


AI_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string"
        },

        "strengths": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "explanation": {
                        "type": "string"
                    },
                    "evidence": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "title",
                    "explanation",
                    "evidence"
                ],
                "additionalProperties": False
            }
        },

        "improvements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "priority": {
                        "type": "string",
                        "enum": [
                            "high",
                            "medium",
                            "low"
                        ]
                    },
                    "explanation": {
                        "type": "string"
                    },
                    "recommendation": {
                        "type": "string"
                    },
                    "evidence": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "title",
                    "priority",
                    "explanation",
                    "recommendation",
                    "evidence"
                ],
                "additionalProperties": False
            }
        },

        "next_steps": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "project_ideas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "why": {
                        "type": "string"
                    },
                    "technologies": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "title",
                    "description",
                    "why",
                    "technologies"
                ],
                "additionalProperties": False
            }
        }
    },

    "required": [
        "summary",
        "strengths",
        "improvements",
        "next_steps",
        "project_ideas"
    ],

    "additionalProperties": False
}


def get_openai_client():
    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(
        api_key=api_key
    )


def build_repository_prompt(
    analysis: dict
):
    repository = analysis.get(
        "repository",
        {}
    )

    technologies = analysis.get(
        "technologies",
        {}
    )

    insights = analysis.get(
        "insights",
        {}
    )

    code_analysis = analysis.get(
        "code_analysis",
        {}
    )

    safe_analysis = {
        "repository": {
            "name": repository.get(
                "name"
            ),
            "description": repository.get(
                "description"
            ),
            "main_language": repository.get(
                "language"
            ),
            "default_branch": repository.get(
                "default_branch"
            )
        },

        "languages": technologies.get(
            "languages",
            []
        ),

        "technologies": technologies.get(
            "technologies",
            []
        ),

        "repository_signals": insights.get(
            "signals",
            []
        ),

        "code_analysis": {
            "analyzed_file_count":
                code_analysis.get(
                    "analyzed_file_count",
                    0
                ),

            "issue_count":
                code_analysis.get(
                    "issue_count",
                    0
                ),

            "summary":
                code_analysis.get(
                    "summary",
                    {}
                ),

            "issues":
                code_analysis.get(
                    "issues",
                    []
                )[:30]
        }
    }

    return json.dumps(
        safe_analysis,
        ensure_ascii=False,
        indent=2
    )


def generate_mock_repository_ai_analysis(
    analysis: dict
):
    technologies = (
        analysis
        .get("technologies", {})
        .get("technologies", [])
    )

    technology_names = [
        technology.get("name")
        for technology in technologies
        if technology.get("name")
    ]

    insights = (
        analysis
        .get("insights", {})
        .get("signals", [])
    )

    code_analysis = analysis.get(
        "code_analysis",
        {}
    )

    issue_count = code_analysis.get(
        "issue_count",
        0
    )

    warning_signals = [
        signal
        for signal in insights
        if signal.get("status") == "warning"
    ]

    strengths = []

    if technology_names:
        strengths.append(
            {
                "title": "Detected technology stack",
                "explanation": (
                    "RepoLens detected multiple technologies "
                    "with repository evidence."
                ),
                "evidence": technology_names[:5]
            }
        )

    if issue_count == 0:
        strengths.append(
            {
                "title": "Clean static analysis result",
                "explanation": (
                    "No supported code issues were detected "
                    "in the analyzed source files."
                ),
                "evidence": [
                    "Code analysis returned 0 issues"
                ]
            }
        )

    improvements = []

    for signal in warning_signals[:3]:
        improvements.append(
            {
                "title": signal.get(
                    "title",
                    "Repository improvement"
                ),
                "priority": "medium",
                "explanation": signal.get(
                    "message",
                    "An improvement opportunity was detected."
                ),
                "recommendation": (
                    "Review this area and improve the repository "
                    "using common software engineering practices."
                ),
                "evidence": signal.get(
                    "evidence",
                    []
                )
            }
        )

    if not improvements:
        improvements.append(
            {
                "title": "Add automated tests",
                "priority": "medium",
                "explanation": (
                    "Automated tests improve reliability "
                    "and make future changes safer."
                ),
                "recommendation": (
                    "Add unit and integration tests "
                    "for the most important application flows."
                ),
                "evidence": []
            }
        )

    return {
        "summary": (
            "This is a mock AI analysis generated locally "
            "from RepoLens repository signals. "
            "It is intended for development and UI testing."
        ),

        "strengths": strengths or [
            {
                "title": "Repository analysis completed",
                "explanation": (
                    "RepoLens successfully analyzed the "
                    "repository structure and source signals."
                ),
                "evidence": []
            }
        ],

        "improvements": improvements,

        "next_steps": [
            "Review repository warnings.",
            "Add or improve automated tests.",
            "Document setup and development instructions.",
            "Add CI/CD if the project does not already include it."
        ],

        "project_ideas": [
            {
                "title": "Production Readiness Upgrade",
                "description": (
                    "Improve the current project with testing, "
                    "CI/CD, containerization and stronger documentation."
                ),
                "why": (
                    "This project builds practical software "
                    "engineering skills around the existing codebase."
                ),
                "technologies": [
                    "GitHub Actions",
                    "Docker",
                    "Testing"
                ]
            },

            {
                "title": "Full Stack Analytics Dashboard",
                "description": (
                    "Build a dashboard using a modern frontend "
                    "and a REST API backend."
                ),
                "why": (
                    "This demonstrates frontend, backend, API "
                    "and deployment skills in one project."
                ),
                "technologies": [
                    "React",
                    "FastAPI",
                    "PostgreSQL"
                ]
            }
        ]
    }


def generate_repository_ai_analysis(analysis: dict):
    use_mock_ai = os.getenv(
        "USE_MOCK_AI",
        "false"
    ).lower() == "true"

    if use_mock_ai:
        return generate_mock_repository_ai_analysis(analysis)

    client = get_openai_client()
    repository_context = build_repository_prompt(analysis)

    prompt_messages = [
        {
            "role": "system",
            "content": (
                "You are RepoLens AI, an evidence-based software repository reviewer. "
                "Analyze only the repository information provided by the application. "
                "Do not invent files, technologies, security issues, architecture decisions, "
                "or developer experience that are not supported by the data. "
                "Treat static-analysis findings as heuristic signals rather than confirmed vulnerabilities. "
                "Give practical recommendations appropriate for a developer improving the repository."
            )
        },
        {
            "role": "user",
            "content": (
                "Analyze the following repository report.\n\n"
                f"{repository_context}"
            )
        }
    ]

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=prompt_messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "repository_ai_analysis",
                    "strict": True,
                    "schema": AI_ANALYSIS_SCHEMA
                }
            },
            temperature=0.2
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("The AI model returned an empty response.")
        return json.loads(content)
    except Exception:
        # Fallback: json_schema desteği olmayan modeller için standart json_object modu
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=prompt_messages + [
                {
                    "role": "system",
                    "content": f"Output must conform strictly to this JSON schema: {json.dumps(AI_ANALYSIS_SCHEMA)}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("The AI model returned an empty response.")
        return json.loads(content)