function AIAnalysis({ analysis }) {
  if (!analysis) {
    return null;
  }

  return (
    <section className="ai-analysis-section">
      <div className="ai-analysis-header">
        <div>
          <span className="section-label">
            AI Repository Review
          </span>

          <h3>
            RepoLens AI Analysis
          </h3>
        </div>

        <span className="ai-badge">
          AI Generated
        </span>
      </div>

      <div className="ai-summary">
        <h4>Summary</h4>

        <p>
          {analysis.summary}
        </p>
      </div>

      <div className="ai-analysis-grid">
        <div className="ai-analysis-column">
          <h4>Strengths</h4>

          {analysis.strengths.map(
            (strength, index) => (
              <article
                className="ai-card ai-strength"
                key={`${strength.title}-${index}`}
              >
                <h5>
                  {strength.title}
                </h5>

                <p>
                  {strength.explanation}
                </p>

                {strength.evidence.length > 0 && (
                  <div className="ai-evidence">
                    <span>Evidence</span>

                    {strength.evidence.map(
                      (evidence) => (
                        <code key={evidence}>
                          {evidence}
                        </code>
                      )
                    )}
                  </div>
                )}
              </article>
            )
          )}
        </div>

        <div className="ai-analysis-column">
          <h4>
            Priority Improvements
          </h4>

          {analysis.improvements.map(
            (improvement, index) => (
              <article
                className="ai-card ai-improvement"
                key={`${improvement.title}-${index}`}
              >
                <div className="ai-card-title">
                  <h5>
                    {improvement.title}
                  </h5>

                  <span
                    className={`priority priority-${improvement.priority}`}
                  >
                    {improvement.priority}
                  </span>
                </div>

                <p>
                  {improvement.explanation}
                </p>

                <strong>
                  Recommendation
                </strong>

                <p>
                  {improvement.recommendation}
                </p>

                {improvement.evidence.length > 0 && (
                  <div className="ai-evidence">
                    <span>Evidence</span>

                    {improvement.evidence.map(
                      (evidence) => (
                        <code key={evidence}>
                          {evidence}
                        </code>
                      )
                    )}
                  </div>
                )}
              </article>
            )
          )}
        </div>
      </div>

      <div className="ai-next-steps">
        <h4>
          Recommended Next Steps
        </h4>

        <ol>
          {analysis.next_steps.map(
            (step, index) => (
              <li key={`${step}-${index}`}>
                <span>
                  {index + 1}
                </span>

                <p>
                  {step}
                </p>
              </li>
            )
          )}
        </ol>
      </div>

      <div className="ai-projects">
        <h4>
          Recommended Projects
        </h4>

        <div className="ai-project-grid">
          {analysis.project_ideas.map(
            (project, index) => (
              <article
                className="ai-project-card"
                key={`${project.title}-${index}`}
              >
                <h5>
                  {project.title}
                </h5>

                <p>
                  {project.description}
                </p>

                <div className="project-reason">
                  <span>Why this project?</span>

                  <p>
                    {project.why}
                  </p>
                </div>

                <div className="project-technologies">
                  {project.technologies.map(
                    (technology) => (
                      <span key={technology}>
                        {technology}
                      </span>
                    )
                  )}
                </div>
              </article>
            )
          )}
        </div>
      </div>

      <div className="ai-disclaimer">
        AI recommendations are based on the repository signals
        detected by RepoLens and should be reviewed before making
        engineering decisions.
      </div>
    </section>
  );
}

export default AIAnalysis;