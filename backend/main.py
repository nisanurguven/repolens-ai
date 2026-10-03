from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse, quote
from pathlib import PurePosixPath
from pydantic import BaseModel
from typing import Any

from services.ai_service import (generate_repository_ai_analysis,)

from services.job_service import (
    extract_pdf_text,
    analyze_job_description,
    compare_profile_with_job,
)

import base64
import json
import re
import httpx
import asyncio
import openai
import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

app = FastAPI(
    title="RepoLens AI API",
    description="Backend API for analyzing GitHub repositories.",
    version="0.2.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_github_repository_url(url: str):
    parsed_url = urlparse(url)

    if parsed_url.scheme not in ["http", "https"]:
        raise HTTPException(
            status_code=400,
            detail="Repository URL must start with http:// or https://."
        )

    if parsed_url.netloc not in ["github.com", "www.github.com"]:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid GitHub repository URL."
        )

    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) < 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL."
        )

    owner = path_parts[0]
    repository_name = path_parts[1].replace(".git", "")

    if not owner or not repository_name:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL."
        )

    return owner, repository_name

async def github_request(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "RepoLens-AI"
    }
    
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=15.0
        ) as client:
            response = await client.get(
                url,
                headers=headers
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="GitHub API request timed out."
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="GitHub service is currently unavailable."
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Repository resource not found."
        )

    if response.status_code == 403:
        raise HTTPException(
            status_code=403,
            detail="GitHub API rate limit exceeded. Please try again later."
        )

    if not response.is_success:
        raise HTTPException(
            status_code=response.status_code,
            detail="GitHub API request failed."
        )

    return response.json()


def build_file_tree(items, repository_name: str):
    root = {
        "name": repository_name,
        "type": "directory",
        "path": "",
        "children": {}
    }

    for item in items:
        if item.get("type") != "blob":
            continue

        file_path = item.get("path")

        if not file_path:
            continue

        parts = file_path.split("/")
        current_node = root
        current_path = []

        for index, part in enumerate(parts):
            current_path.append(part)

            is_file = index == len(parts) - 1

            if is_file:
                current_node["children"][part] = {
                    "name": part,
                    "type": "file",
                    "path": file_path,
                    "size": item.get("size")
                }

            else:
                if part not in current_node["children"]:
                    current_node["children"][part] = {
                        "name": part,
                        "type": "directory",
                        "path": "/".join(current_path),
                        "children": {}
                    }

                current_node = current_node["children"][part]

    def convert_children(node):
        if node["type"] != "directory":
            return node

        converted_children = [
            convert_children(child)
            for child in node["children"].values()
        ]

        converted_children.sort(
            key=lambda child: (
                child["type"] != "directory",
                child["name"].lower()
            )
        )

        node["children"] = converted_children

        return node

    return convert_children(root)


LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".cs": "C#",
    ".c": "C",
    ".cpp": "C++",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sql": "SQL",
    ".swift": "Swift",
    ".rb": "Ruby"
}


JAVASCRIPT_TECHNOLOGIES = {
    "react": ("React", "frontend"),
    "react-dom": ("React", "frontend"),
    "vite": ("Vite", "build-tool"),
    "typescript": ("TypeScript", "language"),
    "next": ("Next.js", "framework"),
    "vue": ("Vue", "frontend"),
    "@angular/core": ("Angular", "frontend"),
    "express": ("Express", "backend"),
    "tailwindcss": ("Tailwind CSS", "styling"),
    "react-router-dom": ("React Router", "frontend"),
    "@tanstack/react-query": ("TanStack Query", "state-data"),
    "zustand": ("Zustand", "state-management"),
    "redux": ("Redux", "state-management"),
    "@reduxjs/toolkit": ("Redux Toolkit", "state-management"),
    "axios": ("Axios", "http-client"),
    "eslint": ("ESLint", "code-quality"),
    "jest": ("Jest", "testing"),
    "vitest": ("Vitest", "testing")
}


PYTHON_TECHNOLOGIES = {
    "fastapi": ("FastAPI", "backend"),
    "django": ("Django", "backend"),
    "flask": ("Flask", "backend"),
    "sqlalchemy": ("SQLAlchemy", "database"),
    "pydantic": ("Pydantic", "backend"),
    "uvicorn": ("Uvicorn", "server"),
    "psycopg": ("PostgreSQL", "database"),
    "psycopg2": ("PostgreSQL", "database"),
    "psycopg2-binary": ("PostgreSQL", "database"),
    "asyncpg": ("PostgreSQL", "database"),
    "pymongo": ("MongoDB", "database"),
    "redis": ("Redis", "database"),
    "pandas": ("Pandas", "data"),
    "numpy": ("NumPy", "data"),
    "scikit-learn": ("Scikit-learn", "machine-learning"),
    "torch": ("PyTorch", "machine-learning"),
    "tensorflow": ("TensorFlow", "machine-learning"),
    "openai": ("OpenAI API", "ai"),
    "langchain": ("LangChain", "ai"),
    "pytest": ("Pytest", "testing")
}

ANALYZABLE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".kt",
    ".go",
    ".php",
    ".cs",
    ".c",
    ".cpp"
}


EXCLUDED_PATH_PARTS = {
    "node_modules",
    "dist",
    "build",
    ".next",
    "coverage",
    "vendor",
    "__pycache__"
}


SECRET_NAME_PATTERN = re.compile(
    r"(?i)\b("
    r"api[_-]?key|"
    r"secret|"
    r"token|"
    r"password|"
    r"passwd|"
    r"access[_-]?key|"
    r"private[_-]?key"
    r")\b"
)


STRING_ASSIGNMENT_PATTERN = re.compile(
    r"""(?ix)
    \b
    (?P<name>
        api[_-]?key|
        secret|
        token|
        password|
        passwd|
        access[_-]?key|
        private[_-]?key
    )
    \b
    \s*
    [:=]
    \s*
    ["']
    (?P<value>[^"']{8,})
    ["']
    """
)


SAFE_SECRET_VALUES = {
    "your_api_key",
    "your-api-key",
    "your_token",
    "your-token",
    "your_password",
    "your-password",
    "changeme",
    "change_me",
    "example",
    "placeholder"
}


def should_analyze_file(path: str, size: int):
    suffix = PurePosixPath(path).suffix.lower()

    if suffix not in ANALYZABLE_EXTENSIONS:
        return False

    if size > 200 * 1024:
        return False

    path_parts = {
        part.lower()
        for part in PurePosixPath(path).parts
    }

    if path_parts.intersection(EXCLUDED_PATH_PARTS):
        return False

    file_name = PurePosixPath(path).name.lower()

    if (
        file_name.endswith(".min.js")
        or file_name.endswith(".min.css")
    ):
        return False

    return True


def create_code_issue(
    issue_type: str,
    severity: str,
    title: str,
    message: str,
    file_path: str,
    line: int | None = None
):
    return {
        "type": issue_type,
        "severity": severity,
        "title": title,
        "message": message,
        "file": file_path,
        "line": line
    }


def is_safe_secret_value(value: str):
    normalized_value = value.strip().lower()

    if normalized_value in SAFE_SECRET_VALUES:
        return True

    if normalized_value.startswith("${"):
        return True

    if normalized_value.startswith("process.env"):
        return True

    if normalized_value.startswith("os.getenv"):
        return True

    if normalized_value.startswith("env."):
        return True

    return False


def analyze_source_content(
    file_path: str,
    content: str
):
    issues = []

    lines = content.splitlines()

    if len(lines) > 400:
        issues.append(
            create_code_issue(
                issue_type="large_file",
                severity="warning",
                title="Large source file",
                message=(
                    f"This file contains {len(lines)} lines "
                    "and may benefit from being split into smaller modules."
                ),
                file_path=file_path
            )
        )

    suffix = PurePosixPath(
        file_path
    ).suffix.lower()

    for line_number, line in enumerate(
        lines,
        start=1
    ):
        stripped_line = line.strip()

        upper_line = line.upper()

        if "TODO" in upper_line:
            issues.append(
                create_code_issue(
                    issue_type="todo",
                    severity="info",
                    title="TODO comment",
                    message=(
                        "A TODO comment was found "
                        "and may represent unfinished work."
                    ),
                    file_path=file_path,
                    line=line_number
                )
            )

        if "FIXME" in upper_line:
            issues.append(
                create_code_issue(
                    issue_type="fixme",
                    severity="warning",
                    title="FIXME comment",
                    message=(
                        "A FIXME comment was found "
                        "and may indicate a known problem."
                    ),
                    file_path=file_path,
                    line=line_number
                )
            )

        if suffix in {
            ".js",
            ".jsx",
            ".ts",
            ".tsx"
        }:
            if re.search(
                r"\bconsole\.(log|debug)\s*\(",
                line
            ):
                issues.append(
                    create_code_issue(
                        issue_type="debug_output",
                        severity="info",
                        title="Console debug output",
                        message=(
                            "A console.log or console.debug "
                            "statement was detected."
                        ),
                        file_path=file_path,
                        line=line_number
                    )
                )

            if re.search(
                r"\bdebugger\s*;",
                line
            ):
                issues.append(
                    create_code_issue(
                        issue_type="debugger",
                        severity="warning",
                        title="Debugger statement",
                        message=(
                            "A JavaScript debugger statement "
                            "was detected."
                        ),
                        file_path=file_path,
                        line=line_number
                    )
                )

        if suffix == ".py":
            if re.search(
                r"^\s*print\s*\(",
                line
            ):
                issues.append(
                    create_code_issue(
                        issue_type="debug_output",
                        severity="info",
                        title="Python print statement",
                        message=(
                            "A print statement was detected. "
                            "Consider structured logging "
                            "for production code."
                        ),
                        file_path=file_path,
                        line=line_number
                    )
                )

        secret_match = (
            STRING_ASSIGNMENT_PATTERN.search(
                stripped_line
            )
        )

        if secret_match:
            secret_value = secret_match.group(
                "value"
            )

            if not is_safe_secret_value(
                secret_value
            ):
                issues.append(
                    create_code_issue(
                        issue_type="possible_secret",
                        severity="critical",
                        title="Possible hard-coded secret",
                        message=(
                            "A value that looks like a "
                            "hard-coded credential was detected. "
                            "The credential value is not exposed "
                            "by RepoLens."
                        ),
                        file_path=file_path,
                        line=line_number
                    )
                )

    return issues


async def analyze_repository_code(
    owner: str,
    repository_name: str,
    branch: str,
    raw_items
):
    candidate_files = []

    for item in raw_items:
        if item.get("type") != "blob":
            continue

        file_path = item.get(
            "path",
            ""
        )

        file_size = item.get(
            "size"
        ) or 0

        if should_analyze_file(
            file_path,
            file_size
        ):
            candidate_files.append(
                {
                    "path": file_path,
                    "size": file_size
                }
            )

    candidate_files.sort(
        key=lambda item: item["size"]
    )

    candidate_files = candidate_files[:30]

    semaphore = asyncio.Semaphore(5)

    async def analyze_file(file_item):
        async with semaphore:
            content = (
                await get_repository_file_content(
                    owner,
                    repository_name,
                    file_item["path"],
                    branch
                )
            )

        if content is None:
            return []

        return analyze_source_content(
            file_item["path"],
            content
        )

    results = await asyncio.gather(
        *[
            analyze_file(file_item)
            for file_item in candidate_files
        ]
    )

    issues = [
        issue
        for file_issues in results
        for issue in file_issues
    ]

    severity_order = {
        "critical": 0,
        "warning": 1,
        "info": 2
    }

    issues.sort(
        key=lambda issue: (
            severity_order.get(
                issue["severity"],
                99
            ),
            issue["file"],
            issue["line"] or 0
        )
    )

    summary = {
        "critical": sum(
            1
            for issue in issues
            if issue["severity"] == "critical"
        ),
        "warnings": sum(
            1
            for issue in issues
            if issue["severity"] == "warning"
        ),
        "info": sum(
            1
            for issue in issues
            if issue["severity"] == "info"
        )
    }

    return {
        "analyzed_file_count": len(
            candidate_files
        ),
        "issue_count": len(
            issues
        ),
        "summary": summary,
        "issues": issues
    }


def add_technology(
    technologies: dict,
    name: str,
    category: str,
    evidence: str
):
    if name not in technologies:
        technologies[name] = {
            "name": name,
            "category": category,
            "evidence": []
        }

    if evidence not in technologies[name]["evidence"]:
        technologies[name]["evidence"].append(evidence)


async def get_repository_file_content(
    owner: str,
    repository_name: str,
    file_path: str,
    branch: str
):
    encoded_path = quote(
        file_path,
        safe="/"
    )

    encoded_branch = quote(
        branch,
        safe=""
    )

    file_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}/contents/"
        f"{encoded_path}?ref={encoded_branch}"
    )

    file_data = await github_request(file_url)

    if not isinstance(file_data, dict):
        return None

    if file_data.get("encoding") != "base64":
        return None

    encoded_content = file_data.get("content")

    if not encoded_content:
        return None

    try:
        decoded_content = base64.b64decode(
            encoded_content
        ).decode(
            "utf-8",
            errors="replace"
        )

        return decoded_content

    except (ValueError, TypeError):
        return None


def detect_languages(raw_items):
    language_counts = {}

    for item in raw_items:
        if item.get("type") != "blob":
            continue

        file_path = item.get("path", "")

        suffix = PurePosixPath(
            file_path
        ).suffix.lower()

        language = LANGUAGE_EXTENSIONS.get(
            suffix
        )

        if not language:
            continue

        language_counts[language] = (
            language_counts.get(language, 0) + 1
        )

    languages = [
        {
            "name": language,
            "files": count
        }
        for language, count
        in language_counts.items()
    ]

    languages.sort(
        key=lambda language: language["files"],
        reverse=True
    )

    return languages


def parse_python_package_name(line: str):
    cleaned_line = line.strip()

    if not cleaned_line:
        return None

    if cleaned_line.startswith("#"):
        return None

    package_name = re.split(
        r"[<>=!~\[\s]",
        cleaned_line
    )[0]

    return package_name.lower()


async def analyze_manifest_files(
    owner: str,
    repository_name: str,
    branch: str,
    raw_items
):
    technologies = {}
    analyzed_files = []

    file_paths = [
        item.get("path")
        for item in raw_items
        if item.get("type") == "blob"
        and item.get("path")
    ]

    for file_path in file_paths:
        file_name = PurePosixPath(
            file_path
        ).name.lower()

        normalized_path = file_path.lower()

        if file_name == "dockerfile":
            add_technology(
                technologies,
                "Docker",
                "devops",
                file_path
            )

        if file_name in [
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml"
        ]:
            add_technology(
                technologies,
                "Docker Compose",
                "devops",
                file_path
            )

        if normalized_path.startswith(
            ".github/workflows/"
        ):
            add_technology(
                technologies,
                "GitHub Actions",
                "ci-cd",
                file_path
            )

        if file_name == "tsconfig.json":
            add_technology(
                technologies,
                "TypeScript",
                "language",
                file_path
            )

        if file_name.startswith("vite.config"):
            add_technology(
                technologies,
                "Vite",
                "build-tool",
                file_path
            )

        if file_name.startswith("tailwind.config"):
            add_technology(
                technologies,
                "Tailwind CSS",
                "styling",
                file_path
            )

        if file_name.startswith("next.config"):
            add_technology(
                technologies,
                "Next.js",
                "framework",
                file_path
            )

        if file_name == "package-lock.json":
            add_technology(
                technologies,
                "npm",
                "package-manager",
                file_path
            )

        if file_name == "yarn.lock":
            add_technology(
                technologies,
                "Yarn",
                "package-manager",
                file_path
            )

        if file_name == "pnpm-lock.yaml":
            add_technology(
                technologies,
                "pnpm",
                "package-manager",
                file_path
            )

    package_json_files = [
        path
        for path in file_paths
        if PurePosixPath(path).name.lower()
        == "package.json"
    ]

    requirements_files = [
        path
        for path in file_paths
        if PurePosixPath(path).name.lower()
        == "requirements.txt"
    ]

    for package_path in package_json_files[:10]:
        content = await get_repository_file_content(
            owner,
            repository_name,
            package_path,
            branch
        )

        if not content:
            continue

        analyzed_files.append(package_path)

        try:
            package_data = json.loads(content)
        except json.JSONDecodeError:
            continue

        dependencies = {
            **package_data.get(
                "dependencies",
                {}
            ),
            **package_data.get(
                "devDependencies",
                {}
            )
        }

        for package_name in dependencies:
            technology = (
                JAVASCRIPT_TECHNOLOGIES.get(
                    package_name.lower()
                )
            )

            if not technology:
                continue

            technology_name, category = (
                technology
            )

            add_technology(
                technologies,
                technology_name,
                category,
                f"{package_path} → {package_name}"
            )

    for requirements_path in requirements_files[:10]:
        content = await get_repository_file_content(
            owner,
            repository_name,
            requirements_path,
            branch
        )

        if not content:
            continue

        analyzed_files.append(
            requirements_path
        )

        for line in content.splitlines():
            package_name = (
                parse_python_package_name(
                    line
                )
            )

            if not package_name:
                continue

            technology = (
                PYTHON_TECHNOLOGIES.get(
                    package_name
                )
            )

            if not technology:
                continue

            technology_name, category = (
                technology
            )

            add_technology(
                technologies,
                technology_name,
                category,
                (
                    f"{requirements_path}"
                    f" → {package_name}"
                )
            )

    technology_list = list(
        technologies.values()
    )

    technology_list.sort(
        key=lambda technology: (
            technology["category"],
            technology["name"]
        )
    )

    return {
        "technologies": technology_list,
        "analyzed_manifest_files": analyzed_files
    }

async def get_repository_context(url: str):
    owner, repository_name = parse_github_repository_url(url)

    repository_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}"
    )

    repository_data = await github_request(
        repository_url
    )

    default_branch = repository_data.get(
        "default_branch"
    )

    if not default_branch:
        raise HTTPException(
            status_code=500,
            detail="Could not determine the repository default branch."
        )

    encoded_branch = quote(
        default_branch,
        safe=""
    )

    tree_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}/git/trees/"
        f"{encoded_branch}?recursive=1"
    )

    tree_data = await github_request(
        tree_url
    )

    raw_items = tree_data.get(
        "tree",
        []
    )

    return {
        "owner": owner,
        "repository_name": repository_name,
        "repository_data": repository_data,
        "default_branch": default_branch,
        "tree_data": tree_data,
        "raw_items": raw_items
    }

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".kt",
    ".go",
    ".rs",
    ".php",
    ".cs",
    ".c",
    ".cpp",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".swift",
    ".rb"
}


def create_signal(
    key: str,
    title: str,
    status: str,
    message: str,
    evidence=None
):
    return {
        "key": key,
        "title": title,
        "status": status,
        "message": message,
        "evidence": evidence or []
    }


def analyze_repository_signals(raw_items):
    file_items = [
        item
        for item in raw_items
        if item.get("type") == "blob"
    ]

    directory_items = [
        item
        for item in raw_items
        if item.get("type") == "tree"
    ]

    file_paths = [
        item.get("path", "")
        for item in file_items
    ]

    directory_paths = [
        item.get("path", "")
        for item in directory_items
    ]

    normalized_files = [
        path.lower()
        for path in file_paths
    ]

    normalized_directories = [
        path.lower()
        for path in directory_paths
    ]

    signals = []

    readme_files = [
        path
        for path in file_paths
        if PurePosixPath(path).name.lower().startswith("readme")
    ]

    if readme_files:
        signals.append(
            create_signal(
                "readme",
                "README documentation",
                "success",
                "Repository documentation was detected.",
                readme_files
            )
        )
    else:
        signals.append(
            create_signal(
                "readme",
                "README documentation",
                "warning",
                "No README file was detected."
            )
        )

    gitignore_files = [
        path
        for path in file_paths
        if PurePosixPath(path).name.lower() == ".gitignore"
    ]

    if gitignore_files:
        signals.append(
            create_signal(
                "gitignore",
                ".gitignore configuration",
                "success",
                "A .gitignore file is present.",
                gitignore_files
            )
        )
    else:
        signals.append(
            create_signal(
                "gitignore",
                ".gitignore configuration",
                "warning",
                "No .gitignore file was detected."
            )
        )

    license_files = [
        path
        for path in file_paths
        if PurePosixPath(path).name.lower()
        in {
            "license",
            "license.md",
            "license.txt",
            "copying"
        }
    ]

    if license_files:
        signals.append(
            create_signal(
                "license",
                "License",
                "success",
                "A repository license was detected.",
                license_files
            )
        )
    else:
        signals.append(
            create_signal(
                "license",
                "License",
                "info",
                "No license file was detected."
            )
        )

    test_files = []

    for path in file_paths:
        lower_path = path.lower()
        file_name = PurePosixPath(path).name.lower()

        if (
            "/tests/" in f"/{lower_path}/"
            or "/test/" in f"/{lower_path}/"
            or "/__tests__/" in f"/{lower_path}/"
            or file_name.startswith("test_")
            or ".test." in file_name
            or ".spec." in file_name
        ):
            test_files.append(path)

    if test_files:
        signals.append(
            create_signal(
                "tests",
                "Automated tests",
                "success",
                "Test files were detected in the repository.",
                test_files[:10]
            )
        )
    else:
        signals.append(
            create_signal(
                "tests",
                "Automated tests",
                "warning",
                "No automated test files were detected."
            )
        )

    exposed_environment_files = []

    safe_environment_files = {
        ".env.example",
        ".env.sample",
        ".env.template"
    }

    for path in file_paths:
        file_name = PurePosixPath(path).name.lower()

        if (
            file_name == ".env"
            or (
                file_name.startswith(".env.")
                and file_name not in safe_environment_files
            )
        ):
            exposed_environment_files.append(path)

    if exposed_environment_files:
        signals.append(
            create_signal(
                "environment",
                "Environment files",
                "warning",
                "Potential environment files are committed to the repository.",
                exposed_environment_files
            )
        )
    else:
        signals.append(
            create_signal(
                "environment",
                "Environment files",
                "success",
                "No exposed environment files were detected."
            )
        )

    docker_files = [
        path
        for path in file_paths
        if (
            PurePosixPath(path).name.lower() == "dockerfile"
            or PurePosixPath(path).name.lower()
            in {
                "docker-compose.yml",
                "docker-compose.yaml",
                "compose.yml",
                "compose.yaml"
            }
        )
    ]

    if docker_files:
        signals.append(
            create_signal(
                "docker",
                "Containerization",
                "success",
                "Docker configuration was detected.",
                docker_files
            )
        )
    else:
        signals.append(
            create_signal(
                "docker",
                "Containerization",
                "info",
                "Docker configuration was not detected."
            )
        )

    workflow_files = [
        path
        for path in file_paths
        if path.lower().startswith(".github/workflows/")
    ]

    if workflow_files:
        signals.append(
            create_signal(
                "ci_cd",
                "CI/CD",
                "success",
                "GitHub Actions workflows were detected.",
                workflow_files
            )
        )
    else:
        signals.append(
            create_signal(
                "ci_cd",
                "CI/CD",
                "info",
                "No GitHub Actions workflows were detected."
            )
        )

    large_source_files = []

    for item in file_items:
        path = item.get("path", "")
        size = item.get("size") or 0

        suffix = PurePosixPath(
            path
        ).suffix.lower()

        if (
            suffix in SOURCE_EXTENSIONS
            and size > 100 * 1024
        ):
            large_source_files.append(
                {
                    "path": path,
                    "size": size
                }
            )

    if large_source_files:
        signals.append(
            create_signal(
                "large_files",
                "Large source files",
                "warning",
                "Large source files were detected and may benefit from refactoring.",
                [
                    item["path"]
                    for item in large_source_files[:10]
                ]
            )
        )
    else:
        signals.append(
            create_signal(
                "large_files",
                "Large source files",
                "success",
                "No unusually large source files were detected."
            )
        )

    source_file_count = sum(
        1
        for path in file_paths
        if PurePosixPath(path).suffix.lower()
        in SOURCE_EXTENSIONS
    )

    has_frontend = any(
        path == "frontend"
        or path.startswith("frontend/")
        for path in normalized_directories
    )

    has_backend = any(
        path == "backend"
        or path.startswith("backend/")
        for path in normalized_directories
    )

    if has_frontend and has_backend:
        signals.append(
            create_signal(
                "architecture",
                "Project structure",
                "success",
                "Separate frontend and backend directories were detected.",
                [
                    "frontend/",
                    "backend/"
                ]
            )
        )
    else:
        signals.append(
            create_signal(
                "architecture",
                "Project structure",
                "info",
                "A separate frontend/backend directory structure was not detected."
            )
        )

    success_count = sum(
        1
        for signal in signals
        if signal["status"] == "success"
    )

    warning_count = sum(
        1
        for signal in signals
        if signal["status"] == "warning"
    )

    info_count = sum(
        1
        for signal in signals
        if signal["status"] == "info"
    )

    return {
        "source_file_count": source_file_count,
        "success_count": success_count,
        "warning_count": warning_count,
        "info_count": info_count,
        "large_source_files": large_source_files,
        "signals": signals
    }

class RepositoryAnalysisRequest(BaseModel):
    url: str

class RepositoryAIAnalysisRequest(BaseModel):
    analysis: dict[str, Any]
    
class DeveloperProfileRequest(BaseModel):
    analysis: dict[str, Any]
    
class CareerGapRequest(BaseModel):
    profile: dict[str, Any]
    job_analysis: dict[str, Any]


def build_developer_profile(
    analysis: dict
):
    repository = analysis.get(
        "repository",
        {}
    )

    technology_analysis = analysis.get(
        "technologies",
        {}
    )

    repository_insights = analysis.get(
        "insights",
        {}
    )

    skills = {}

    languages = technology_analysis.get(
        "languages",
        []
    )

    for language in languages:
        name = language.get("name")
        file_count = language.get(
            "files",
            0
        )

        if not name:
            continue

        skills[name] = {
            "name": name,
            "category": "language",
            "evidence_type": "repository",
            "evidence": [
                (
                    f"{file_count} source "
                    f"{'file' if file_count == 1 else 'files'} detected"
                )
            ]
        }

    technologies = technology_analysis.get(
        "technologies",
        []
    )

    for technology in technologies:
        name = technology.get("name")

        if not name:
            continue

        category = technology.get(
            "category",
            "technology"
        )

        evidence = technology.get(
            "evidence",
            []
        )

        if name in skills:
            existing_evidence = skills[
                name
            ]["evidence"]

            for item in evidence:
                if item not in existing_evidence:
                    existing_evidence.append(
                        item
                    )

            continue

        skills[name] = {
            "name": name,
            "category": category,
            "evidence_type": "repository",
            "evidence": evidence
        }

    signals = repository_insights.get(
        "signals",
        []
    )

    for signal in signals:
        if signal.get("status") != "success":
            continue

        signal_key = signal.get("key")

        if signal_key == "tests":
            skills[
                "Automated Testing"
            ] = {
                "name": "Automated Testing",
                "category": "engineering-practice",
                "evidence_type": "repository",
                "evidence": signal.get(
                    "evidence",
                    []
                )
            }

        elif signal_key == "docker":
            if "Docker" not in skills:
                skills["Docker"] = {
                    "name": "Docker",
                    "category": "devops",
                    "evidence_type": "repository",
                    "evidence": signal.get(
                        "evidence",
                        []
                    )
                }

        elif signal_key == "ci_cd":
            if "GitHub Actions" not in skills:
                skills[
                    "GitHub Actions"
                ] = {
                    "name": "GitHub Actions",
                    "category": "ci-cd",
                    "evidence_type": "repository",
                    "evidence": signal.get(
                        "evidence",
                        []
                    )
                }

    skill_list = list(
        skills.values()
    )

    skill_list.sort(
        key=lambda skill: (
            skill["category"],
            skill["name"].lower()
        )
    )

    categories = {}

    for skill in skill_list:
        category = skill["category"]

        categories[category] = (
            categories.get(
                category,
                0
            ) + 1
        )

    return {
        "repository": repository.get(
            "full_name"
        ),

        "total_skills": len(
            skill_list
        ),

        "language_count": sum(
            1
            for skill in skill_list
            if skill["category"]
            == "language"
        ),

        "technology_count": len(
            technologies
        ),

        "categories": categories,

        "skills": skill_list
    }


@app.get("/")
def home():
    return {
        "message": "RepoLens AI API is running."
    }


@app.get("/api/repository")
async def get_repository(url: str):
    owner, repository_name = parse_github_repository_url(url)

    github_api_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}"
    )

    data = await github_request(github_api_url)

    return {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "owner": data.get("owner", {}).get("login"),
        "owner_avatar": data.get("owner", {}).get("avatar_url"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "watchers": data.get("subscribers_count"),
        "size": data.get("size"),
        "visibility": data.get("visibility"),
        "default_branch": data.get("default_branch"),
        "github_url": data.get("html_url"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at")
    }


@app.get("/api/repository/tree")
async def get_repository_tree(url: str):
    owner, repository_name = parse_github_repository_url(url)

    repository_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}"
    )

    repository_data = await github_request(repository_url)

    default_branch = repository_data.get("default_branch")

    if not default_branch:
        raise HTTPException(
            status_code=500,
            detail="Could not determine the repository default branch."
        )

    encoded_branch = quote(
        default_branch,
        safe=""
    )

    tree_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}/git/trees/"
        f"{encoded_branch}?recursive=1"
    )

    tree_data = await github_request(tree_url)

    raw_items = tree_data.get("tree", [])

    file_count = sum(
        1
        for item in raw_items
        if item.get("type") == "blob"
    )

    directory_count = sum(
        1
        for item in raw_items
        if item.get("type") == "tree"
    )

    file_tree = build_file_tree(
        raw_items,
        repository_name
    )

    return {
        "repository": repository_data.get("full_name"),
        "default_branch": default_branch,
        "file_count": file_count,
        "directory_count": directory_count,
        "truncated": tree_data.get("truncated", False),
        "tree": file_tree
    }
    

@app.get("/api/repository/technologies")
async def get_repository_technologies(
    url: str
):
    owner, repository_name = (
        parse_github_repository_url(url)
    )

    repository_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}"
    )

    repository_data = await github_request(
        repository_url
    )

    default_branch = repository_data.get(
        "default_branch"
    )

    if not default_branch:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not determine the "
                "repository default branch."
            )
        )

    encoded_branch = quote(
        default_branch,
        safe=""
    )

    tree_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}/git/trees/"
        f"{encoded_branch}?recursive=1"
    )

    tree_data = await github_request(
        tree_url
    )

    raw_items = tree_data.get(
        "tree",
        []
    )

    languages = detect_languages(
        raw_items
    )

    manifest_analysis = (
        await analyze_manifest_files(
            owner,
            repository_name,
            default_branch,
            raw_items
        )
    )

    return {
        "repository": repository_data.get(
            "full_name"
        ),
        "default_branch": default_branch,
        "languages": languages,
        "technologies": manifest_analysis[
            "technologies"
        ],
        "analyzed_manifest_files":
            manifest_analysis[
                "analyzed_manifest_files"
            ],
        "technology_count": len(
            manifest_analysis[
                "technologies"
            ]
        )
    }
    
    
@app.get("/api/repository/insights")
async def get_repository_insights(url: str):
    owner, repository_name = (
        parse_github_repository_url(url)
    )

    repository_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}"
    )

    repository_data = await github_request(
        repository_url
    )

    default_branch = repository_data.get(
        "default_branch"
    )

    if not default_branch:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not determine the "
                "repository default branch."
            )
        )

    encoded_branch = quote(
        default_branch,
        safe=""
    )

    tree_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}/git/trees/"
        f"{encoded_branch}?recursive=1"
    )

    tree_data = await github_request(
        tree_url
    )

    raw_items = tree_data.get(
        "tree",
        []
    )

    analysis = analyze_repository_signals(
        raw_items
    )

    return {
        "repository": repository_data.get(
            "full_name"
        ),
        "default_branch": default_branch,
        "source_file_count": analysis[
            "source_file_count"
        ],
        "summary": {
            "success": analysis[
                "success_count"
            ],
            "warnings": analysis[
                "warning_count"
            ],
            "info": analysis[
                "info_count"
            ]
        },
        "large_source_files": analysis[
            "large_source_files"
        ],
        "signals": analysis[
            "signals"
        ]
    }
    
    
@app.get("/api/repository/code-analysis")
async def get_repository_code_analysis(
    url: str
):
    owner, repository_name = (
        parse_github_repository_url(url)
    )

    repository_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}"
    )

    repository_data = await github_request(
        repository_url
    )

    default_branch = repository_data.get(
        "default_branch"
    )

    if not default_branch:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not determine the "
                "repository default branch."
            )
        )

    encoded_branch = quote(
        default_branch,
        safe=""
    )

    tree_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository_name}/git/trees/"
        f"{encoded_branch}?recursive=1"
    )

    tree_data = await github_request(
        tree_url
    )

    raw_items = tree_data.get(
        "tree",
        []
    )

    analysis = await analyze_repository_code(
        owner,
        repository_name,
        default_branch,
        raw_items
    )

    return {
        "repository": repository_data.get(
            "full_name"
        ),
        "default_branch": default_branch,
        "analyzed_file_count": analysis[
            "analyzed_file_count"
        ],
        "issue_count": analysis[
            "issue_count"
        ],
        "summary": analysis[
            "summary"
        ],
        "issues": analysis[
            "issues"
        ]
    }
    
@app.post("/api/analyze")
async def analyze_repository(
    request: RepositoryAnalysisRequest
):
    context = await get_repository_context(
        request.url
    )

    owner = context["owner"]
    repository_name = context[
        "repository_name"
    ]

    repository_data = context[
        "repository_data"
    ]

    default_branch = context[
        "default_branch"
    ]

    tree_data = context[
        "tree_data"
    ]

    raw_items = context[
        "raw_items"
    ]

    file_count = sum(
        1
        for item in raw_items
        if item.get("type") == "blob"
    )

    directory_count = sum(
        1
        for item in raw_items
        if item.get("type") == "tree"
    )

    file_tree = build_file_tree(
        raw_items,
        repository_name
    )

    languages = detect_languages(
        raw_items
    )

    manifest_analysis = (
        await analyze_manifest_files(
            owner,
            repository_name,
            default_branch,
            raw_items
        )
    )

    repository_insights = (
        analyze_repository_signals(
            raw_items
        )
    )

    code_analysis = (
        await analyze_repository_code(
            owner,
            repository_name,
            default_branch,
            raw_items
        )
    )

    return {
        "repository": {
            "name": repository_data.get(
                "name"
            ),
            "full_name": repository_data.get(
                "full_name"
            ),
            "description": repository_data.get(
                "description"
            ),
            "owner": repository_data.get(
                "owner",
                {}
            ).get(
                "login"
            ),
            "owner_avatar": repository_data.get(
                "owner",
                {}
            ).get(
                "avatar_url"
            ),
            "language": repository_data.get(
                "language"
            ),
            "stars": repository_data.get(
                "stargazers_count"
            ),
            "forks": repository_data.get(
                "forks_count"
            ),
            "open_issues": repository_data.get(
                "open_issues_count"
            ),
            "watchers": repository_data.get(
                "subscribers_count"
            ),
            "size": repository_data.get(
                "size"
            ),
            "visibility": repository_data.get(
                "visibility"
            ),
            "default_branch": default_branch,
            "github_url": repository_data.get(
                "html_url"
            ),
            "created_at": repository_data.get(
                "created_at"
            ),
            "updated_at": repository_data.get(
                "updated_at"
            )
        },

        "tree": {
            "repository": repository_data.get(
                "full_name"
            ),
            "default_branch": default_branch,
            "file_count": file_count,
            "directory_count": directory_count,
            "truncated": tree_data.get(
                "truncated",
                False
            ),
            "tree": file_tree
        },

        "technologies": {
            "repository": repository_data.get(
                "full_name"
            ),
            "default_branch": default_branch,
            "languages": languages,
            "technologies": manifest_analysis[
                "technologies"
            ],
            "analyzed_manifest_files":
                manifest_analysis[
                    "analyzed_manifest_files"
                ],
            "technology_count": len(
                manifest_analysis[
                    "technologies"
                ]
            )
        },

        "insights": {
            "repository": repository_data.get(
                "full_name"
            ),
            "default_branch": default_branch,
            "source_file_count":
                repository_insights[
                    "source_file_count"
                ],
            "summary": {
                "success":
                    repository_insights[
                        "success_count"
                    ],
                "warnings":
                    repository_insights[
                        "warning_count"
                    ],
                "info":
                    repository_insights[
                        "info_count"
                    ]
            },
            "large_source_files":
                repository_insights[
                    "large_source_files"
                ],
            "signals":
                repository_insights[
                    "signals"
                ]
        },

        "code_analysis": {
            "repository": repository_data.get(
                "full_name"
            ),
            "default_branch": default_branch,
            "analyzed_file_count":
                code_analysis[
                    "analyzed_file_count"
                ],
            "issue_count":
                code_analysis[
                    "issue_count"
                ],
            "summary":
                code_analysis[
                    "summary"
                ],
            "issues":
                code_analysis[
                    "issues"
                ]
        }
    }
    
@app.post(
    "/api/repository/ai-analysis"
)
async def get_repository_ai_analysis(
    request: RepositoryAIAnalysisRequest
):
    try:
        ai_analysis = await asyncio.to_thread(
            generate_repository_ai_analysis,
            request.analysis
        )

        return ai_analysis

    except openai.AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail=(
                "OpenAI authentication failed. "
                "Please check your OPENAI_API_KEY."
            )
        )

    except openai.PermissionDeniedError:
        raise HTTPException(
            status_code=403,
            detail=(
                "Your OpenAI API project does not have permission "
                "to use the requested model."
            )
        )

    except openai.RateLimitError as error:
        error_code = getattr(
            error,
            "code",
            None
        )

        if error_code == "credit_balance_exhausted":
            message = (
                "OpenAI API credit balance is exhausted. "
                "Please check your API billing."
            )
        elif error_code in {
            "project_spend_limit_exceeded",
            "organization_spend_limit_exceeded"
        }:
            message = (
                "The OpenAI API spending limit has been reached."
            )
        else:
            message = (
                "OpenAI API rate limit was reached. "
                "Please try again later."
            )

        raise HTTPException(
            status_code=429,
            detail=message
        )

    except openai.BadRequestError as error:
        print(
            "OpenAI BadRequestError:",
            error
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "OpenAI rejected the AI analysis request. "
                "Check the backend terminal for details."
            )
        )

    except openai.APIConnectionError as error:
        print(
            "OpenAI APIConnectionError:",
            error
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Could not connect to the OpenAI API."
            )
        )

    except RuntimeError as error:
        print(
            "AI RuntimeError:",
            error
        )

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception as error:
        print(
            "Unexpected AI error:",
            type(error).__name__,
            str(error)
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "AI analysis could not be generated. "
                "Check the backend terminal for the exact error."
            )
        )
        
        
@app.post(
    "/api/developer-profile"
)
async def get_developer_profile(
    request: DeveloperProfileRequest
):
    return build_developer_profile(
        request.analysis
    )
    
@app.post("/api/job-analysis")
async def get_job_analysis(
    text: str = Form(default=""),
    file: UploadFile | None = File(
        default=None
    ),
):
    combined_text = text.strip()

    if file is not None:
        filename = (
            file.filename or ""
        ).lower()

        if not filename.endswith(
            ".pdf"
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only PDF files are supported."
                )
            )

        file_bytes = await file.read()

        try:
            pdf_text = extract_pdf_text(
                file_bytes
            )

        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        if combined_text:
            combined_text += (
                "\n\n" + pdf_text
            )
        else:
            combined_text = pdf_text

    if not combined_text:
        raise HTTPException(
            status_code=400,
            detail=(
                "Please paste a job description "
                "or upload a PDF."
            )
        )

    try:
        return analyze_job_description(
            combined_text
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
        
@app.post("/api/career-gap")
async def get_career_gap(
    request: CareerGapRequest
):
    return compare_profile_with_job(
        request.profile,
        request.job_analysis
    )