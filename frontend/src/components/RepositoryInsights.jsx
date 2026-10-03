function RepositoryInsights({ analysis }) {
  if (!analysis) {
    return null;
  }

  return (
    <section className="insights-section">
      <div className="insights-header">
        <div>
          <span className="section-label">
            Repository Intelligence
          </span>

          <h3>Project Insights</h3>
        </div>

        <div className="insights-summary">
          <span className="summary-success">
            {analysis.summary.success} passed
          </span>

          <span className="summary-warning">
            {analysis.summary.warnings} warnings
          </span>

          <span className="summary-info">
            {analysis.summary.info} info
          </span>
        </div>
      </div>

      <div className="insights-grid">
        {analysis.signals.map((signal) => (
          <article
            className={`insight-card insight-${signal.status}`}
            key={signal.key}
          >
            <div className="insight-card-top">
              <span className="insight-status-icon">
                {getStatusIcon(signal.status)}
              </span>

              <div>
                <h4>{signal.title}</h4>

                <span className="insight-status">
                  {signal.status}
                </span>
              </div>
            </div>

            <p>{signal.message}</p>

            {signal.evidence.length > 0 && (
              <div className="insight-evidence">
                <span>Evidence</span>

                {signal.evidence.map((item) => (
                  <code key={item}>
                    {item}
                  </code>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}

function getStatusIcon(status) {
  if (status === "success") {
    return "✓";
  }

  if (status === "warning") {
    return "!";
  }

  return "i";
}

export default RepositoryInsights;