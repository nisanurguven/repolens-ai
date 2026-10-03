function CodeHealth({ analysis }) {
  if (!analysis) {
    return null;
  }

  return (
    <section className="code-health-section">
      <div className="code-health-header">
        <div>
          <span className="section-label">
            Static Code Analysis
          </span>

          <h3>Code Health</h3>
        </div>

        <span className="analyzed-files-badge">
          {analysis.analyzed_file_count} files analyzed
        </span>
      </div>

      <div className="code-health-summary">
        <article className="health-summary-card health-critical">
          <span>Critical</span>
          <strong>{analysis.summary.critical}</strong>
        </article>

        <article className="health-summary-card health-warning">
          <span>Warnings</span>
          <strong>{analysis.summary.warnings}</strong>
        </article>

        <article className="health-summary-card health-info">
          <span>Info</span>
          <strong>{analysis.summary.info}</strong>
        </article>

        <article className="health-summary-card">
          <span>Total Issues</span>
          <strong>{analysis.issue_count}</strong>
        </article>
      </div>

      {analysis.issues.length === 0 ? (
        <div className="no-code-issues">
          <div className="no-code-issues-icon">
            ✓
          </div>

          <div>
            <h4>No issues detected</h4>

            <p>
              RepoLens did not detect any supported code issues in the analyzed
              source files.
            </p>
          </div>
        </div>
      ) : (
        <div className="code-issues-list">
          {analysis.issues.map((issue, index) => (
            <article
              className={`code-issue code-issue-${issue.severity}`}
              key={`${issue.file}-${issue.line}-${issue.type}-${index}`}
            >
              <div className="code-issue-icon">
                {getIssueIcon(issue.severity)}
              </div>

              <div className="code-issue-content">
                <div className="code-issue-top">
                  <div>
                    <h4>{issue.title}</h4>

                    <span
                      className={`severity-badge severity-${issue.severity}`}
                    >
                      {issue.severity}
                    </span>
                  </div>

                  <span className="issue-type">
                    {formatIssueType(issue.type)}
                  </span>
                </div>

                <p>{issue.message}</p>

                <div className="issue-location">
                  <code>{issue.file}</code>

                  {issue.line && (
                    <span>
                      Line {issue.line}
                    </span>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}

      <div className="code-health-footer">
        <p>
          Static analysis findings are heuristic signals and should be reviewed
          before making code changes.
        </p>
      </div>
    </section>
  );
}

function getIssueIcon(severity) {
  if (severity === "critical") {
    return "!";
  }

  if (severity === "warning") {
    return "!";
  }

  return "i";
}

function formatIssueType(type) {
  return type
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() +
        word.slice(1)
    )
    .join(" ");
}

export default CodeHealth;