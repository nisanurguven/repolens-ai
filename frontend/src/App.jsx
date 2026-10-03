import { useState } from "react";

import "./App.css";

import RepositoryTree from "./components/RepositoryTree";
import TechnologyStack from "./components/TechnologyStack";
import RepositoryInsights from "./components/RepositoryInsights";
import CodeHealth from "./components/CodeHealth";
import AIAnalysis from "./components/AIAnalysis";
import DeveloperProfile from "./components/DeveloperProfile";
import CareerGap from "./components/CareerGap";

import {
  analyzeRepository,
  generateAIAnalysis,
  buildDeveloperProfile,
} from "./services/repositoryApi";

function App() {
  const [repositoryUrl, setRepositoryUrl] = useState("");

  const [repository, setRepository] = useState(null);
  const [repositoryTree, setRepositoryTree] = useState(null);
  const [technologyAnalysis, setTechnologyAnalysis] = useState(null);
  const [repositoryInsights, setRepositoryInsights] = useState(null);
  const [codeAnalysis, setCodeAnalysis] = useState(null);

  const [fullAnalysis, setFullAnalysis] = useState(null);

  const [aiAnalysis, setAIAnalysis] = useState(null);
  const [aiLoading, setAILoading] = useState(false);
  const [aiError, setAIError] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [developerProfile, setDeveloperProfile] = useState(null);

  async function handleAnalyze(event) {
    event.preventDefault();

    const trimmedUrl = repositoryUrl.trim();

    if (!trimmedUrl) {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      resetAnalysis();

      const analysis = await analyzeRepository(trimmedUrl);

      const profile = await buildDeveloperProfile(analysis);

      setFullAnalysis(analysis);

      setRepository(
        analysis.repository
      );

      setRepositoryTree(
        analysis.tree
      );

      setTechnologyAnalysis(
        analysis.technologies
      );

      setRepositoryInsights(
        analysis.insights
      );

      setCodeAnalysis(
        analysis.code_analysis
      );

      setDeveloperProfile(
        profile
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "An unexpected error occurred."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateAIAnalysis() {
    if (!fullAnalysis) {
      return;
    }

    try {
      setAILoading(true);
      setAIError("");

      const result = await generateAIAnalysis(
        fullAnalysis
      );

      setAIAnalysis(result);
    } catch (requestError) {
      setAIError(
        requestError instanceof Error
          ? requestError.message
          : "AI analysis failed."
      );
    } finally {
      setAILoading(false);
    }
  }

  function resetAnalysis() {
    setRepository(null);
    setRepositoryTree(null);
    setTechnologyAnalysis(null);
    setRepositoryInsights(null);
    setCodeAnalysis(null);

    setDeveloperProfile(null);

    setFullAnalysis(null);

    setAIAnalysis(null);
    setAIError("");
  }

  function formatNumber(value) {
    if (
      value === null ||
      value === undefined
    ) {
      return "N/A";
    }

    return new Intl.NumberFormat(
      "en-US"
    ).format(value);
  }

  return (
    <main className="app">
      <div className="background-glow background-glow-one" />
      <div className="background-glow background-glow-two" />

      <section className="hero">
        <div className="brand">
          <div className="brand-icon">
            R
          </div>

          <div>
            <h2>
              RepoLens AI
            </h2>

            <span>
              Repository Intelligence
            </span>
          </div>
        </div>

        <div className="hero-badge">
          <span className="badge-dot" />

          AI-Powered Repository Analysis
        </div>

        <h1>
          Understand your codebase

          <span>
            {" "}
            before AI even reads it.
          </span>
        </h1>

        <p className="hero-description">
          Analyze repository structure,
          technologies, project quality
          and source code signals from
          a public GitHub repository.
        </p>

        <form
          className="search-container"
          onSubmit={handleAnalyze}
        >
          <div className="search-input-wrapper">
            <span className="github-symbol">
              ⌘
            </span>

            <input
              type="text"
              value={repositoryUrl}
              onChange={(event) =>
                setRepositoryUrl(
                  event.target.value
                )
              }
              placeholder="https://github.com/facebook/react"
              aria-label="GitHub repository URL"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Analyzing..."
              : "Analyze Repository"}
          </button>
        </form>

        <div className="search-help">
          <span>
            No login required
          </span>

          <span>•</span>

          <span>
            Public repositories only
          </span>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </section>

      {loading && (
        <section className="loading-card">
          <div className="loader" />

          <div>
            <h3>
              Analyzing repository
            </h3>

            <p>
              RepoLens is scanning the
              repository structure,
              technologies and source
              code...
            </p>
          </div>
        </section>
      )}

      {repository && !loading && (
        <section className="repository-section">
          <div className="repository-card">
            <div className="repository-top">
              <div className="owner-information">
                <img
                  src={repository.owner_avatar}
                  alt={`${repository.owner} avatar`}
                  className="owner-avatar"
                />

                <div>
                  <span className="owner-name">
                    {repository.owner}
                  </span>

                  <h2>
                    {repository.name}
                  </h2>
                </div>
              </div>

              <div className="repository-tags">
                <span className="visibility-tag">
                  {repository.visibility ||
                    "public"}
                </span>

                {repository.language && (
                  <span className="language-tag">
                    {repository.language}
                  </span>
                )}
              </div>
            </div>

            <p className="repository-description">
              {repository.description ||
                "No repository description available."}
            </p>

            <div className="repository-stats">
              <article className="stat-card">
                <span>
                  Stars
                </span>

                <strong>
                  {formatNumber(
                    repository.stars
                  )}
                </strong>
              </article>

              <article className="stat-card">
                <span>
                  Forks
                </span>

                <strong>
                  {formatNumber(
                    repository.forks
                  )}
                </strong>
              </article>

              <article className="stat-card">
                <span>
                  Open Issues
                </span>

                <strong>
                  {formatNumber(
                    repository.open_issues
                  )}
                </strong>
              </article>

              <article className="stat-card">
                <span>
                  Repository Size
                </span>

                <strong>
                  {repository.size
                    ? `${formatNumber(
                      repository.size
                    )} KB`
                    : "N/A"}
                </strong>
              </article>
            </div>

            <div className="repository-details">
              <div className="detail-row">
                <span>
                  Full name
                </span>

                <strong>
                  {repository.full_name}
                </strong>
              </div>

              <div className="detail-row">
                <span>
                  Default branch
                </span>

                <strong>
                  {repository.default_branch ||
                    "Unknown"}
                </strong>
              </div>

              <div className="detail-row">
                <span>
                  Main language
                </span>

                <strong>
                  {repository.language ||
                    "Unknown"}
                </strong>
              </div>

              <div className="detail-row">
                <span>
                  Visibility
                </span>

                <strong>
                  {repository.visibility ||
                    "Public"}
                </strong>
              </div>
            </div>

            <div className="repository-footer">
              <div>
                <span>
                  RepoLens Analysis
                </span>

                <p>
                  Structure, technologies,
                  project signals and code
                  health are shown below.
                </p>
              </div>

              <a
                href={repository.github_url}
                target="_blank"
                rel="noreferrer"
              >
                View on GitHub

                <span>
                  →
                </span>
              </a>
            </div>

            {repositoryTree && (
              <section className="repository-tree-section">
                <div className="tree-header">
                  <div>
                    <span>
                      Repository Structure
                    </span>

                    <h3>
                      File Explorer
                    </h3>
                  </div>

                  <div className="tree-summary">
                    <span>
                      {repositoryTree.file_count} files
                    </span>

                    <span>
                      {repositoryTree.directory_count} folders
                    </span>
                  </div>
                </div>

                {repositoryTree.truncated && (
                  <div className="tree-warning">
                    GitHub returned a
                    truncated repository
                    tree because the
                    repository is very
                    large.
                  </div>
                )}

                <div className="tree-container">
                  <RepositoryTree
                    node={
                      repositoryTree.tree
                    }
                  />
                </div>
              </section>
            )}

            {technologyAnalysis && (
              <TechnologyStack
                analysis={
                  technologyAnalysis
                }
              />
            )}

            {developerProfile && (
              <DeveloperProfile
                profile={
                  developerProfile
                }
              />
            )}

            {developerProfile && (
              <CareerGap
                developerProfile={
                  developerProfile
                }
              />
            )}

            {repositoryInsights && (
              <RepositoryInsights
                analysis={
                  repositoryInsights
                }
              />
            )}

            {codeAnalysis && (
              <CodeHealth
                analysis={
                  codeAnalysis
                }
              />
            )}

            {fullAnalysis && !aiAnalysis && (
              <section className="generate-ai-section">
                <div>
                  <span className="section-label">
                    AI Layer
                  </span>

                  <h3>
                    Get an intelligent repository review
                  </h3>

                  <p>
                    RepoLens will use the
                    verified repository data
                    above to generate
                    evidence-based strengths,
                    improvements and
                    recommended next steps.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={
                    handleGenerateAIAnalysis
                  }
                  disabled={aiLoading}
                >
                  {aiLoading
                    ? "Generating AI Analysis..."
                    : "Generate AI Analysis"}
                </button>

                {aiError && (
                  <div className="error-message">
                    {aiError}
                  </div>
                )}
              </section>
            )}

            {aiAnalysis && (
              <AIAnalysis
                analysis={
                  aiAnalysis
                }
              />
            )}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;