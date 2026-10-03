function TechnologyStack({ analysis }) {
  if (!analysis) {
    return null;
  }

  return (
    <section className="technology-section">
      <div className="technology-header">
        <div>
          <span className="section-label">
            Technology Detection
          </span>

          <h3>Detected Stack</h3>
        </div>

        <span className="technology-count">
          {analysis.technology_count} technologies
        </span>
      </div>

      <div className="language-section">
        <h4>Languages</h4>

        <div className="language-grid">
          {analysis.languages.map((language) => (
            <article
              className="language-card"
              key={language.name}
            >
              <span>{language.name}</span>

              <strong>
                {language.files}
              </strong>

              <small>
                {language.files === 1 ? "file" : "files"}
              </small>
            </article>
          ))}
        </div>
      </div>

      <div className="detected-technologies">
        <h4>Technologies</h4>

        {analysis.technologies.length === 0 ? (
          <p className="no-technologies">
            No supported technologies were detected from manifest files.
          </p>
        ) : (
          <div className="technology-grid">
            {analysis.technologies.map((technology) => (
              <article
                className="technology-card"
                key={technology.name}
              >
                <div className="technology-card-header">
                  <div>
                    <h5>{technology.name}</h5>

                    <span className="technology-category">
                      {technology.category}
                    </span>
                  </div>

                  <span className="verified-badge">
                    Evidence found
                  </span>
                </div>

                <div className="technology-evidence">
                  <span>Evidence</span>

                  {technology.evidence.map((item) => (
                    <code key={item}>
                      {item}
                    </code>
                  ))}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>

      {analysis.analyzed_manifest_files.length > 0 && (
        <div className="manifest-information">
          <span>Analyzed manifest files:</span>

          <div>
            {analysis.analyzed_manifest_files.map((file) => (
              <code key={file}>
                {file}
              </code>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

export default TechnologyStack;