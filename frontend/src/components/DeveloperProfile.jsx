function DeveloperProfile({ profile }) {
  if (!profile) {
    return null;
  }

  return (
    <section className="developer-profile-section">
      <div className="developer-profile-header">
        <div>
          <span className="section-label">
            Evidence-Based Profile
          </span>

          <h3>
            Developer Profile
          </h3>

          <p>
            Skills detected from repository
            evidence. These are not manually
            declared skills.
          </p>
        </div>

        <div className="profile-total">
          <strong>
            {profile.total_skills}
          </strong>

          <span>
            detected skills
          </span>
        </div>
      </div>

      <div className="profile-summary-grid">
        <article>
          <span>
            Languages
          </span>

          <strong>
            {profile.language_count}
          </strong>
        </article>

        <article>
          <span>
            Technologies
          </span>

          <strong>
            {profile.technology_count}
          </strong>
        </article>

        <article>
          <span>
            Evidence Source
          </span>

          <strong>
            GitHub
          </strong>
        </article>
      </div>

      <div className="developer-skills">
        <div className="developer-skills-header">
          <h4>
            Verified Repository Skills
          </h4>

          <span>
            {profile.repository}
          </span>
        </div>

        <div className="developer-skills-grid">
          {profile.skills.map((skill) => (
            <article
              className="developer-skill-card"
              key={`${skill.category}-${skill.name}`}
            >
              <div className="developer-skill-top">
                <div>
                  <h5>
                    {skill.name}
                  </h5>

                  <span>
                    {formatCategory(
                      skill.category
                    )}
                  </span>
                </div>

                <div className="skill-evidence-badge">
                  Evidence found
                </div>
              </div>

              <div className="developer-skill-evidence">
                <span>
                  Evidence
                </span>

                {skill.evidence.length > 0 ? (
                  skill.evidence.map(
                    (evidence) => (
                      <code key={evidence}>
                        {evidence}
                      </code>
                    )
                  )
                ) : (
                  <code>
                    Repository signal detected
                  </code>
                )}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function formatCategory(category) {
  return category
    .split("-")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() +
        word.slice(1)
    )
    .join(" ");
}

export default DeveloperProfile;