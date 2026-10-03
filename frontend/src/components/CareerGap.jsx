import { useState } from "react";

import {
  analyzeJobDescription,
  analyzeCareerGap,
} from "../services/careerApi";


function CareerGap({
  developerProfile,
}) {
  const [jobText, setJobText] =
    useState("");

  const [jobFile, setJobFile] =
    useState(null);

  const [jobAnalysis, setJobAnalysis] =
    useState(null);

  const [gapAnalysis, setGapAnalysis] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  async function handleSubmit(event) {
    event.preventDefault();

    if (
      !jobText.trim() &&
      !jobFile
    ) {
      setError(
        "Paste a job description or upload a PDF."
      );

      return;
    }

    try {
      setLoading(true);
      setError("");

      setJobAnalysis(null);
      setGapAnalysis(null);

      const analyzedJob =
        await analyzeJobDescription(
          jobText,
          jobFile
        );

      const gap =
        await analyzeCareerGap(
          developerProfile,
          analyzedJob
        );

      setJobAnalysis(
        analyzedJob
      );

      setGapAnalysis(
        gap
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Career gap analysis failed."
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <section className="career-gap-section">
      <div className="career-gap-header">
        <div>
          <span className="section-label">
            Career Intelligence
          </span>

          <h3>
            Career Gap Analysis
          </h3>

          <p>
            Compare your evidence-based
            developer profile with a target
            job description.
          </p>
        </div>
      </div>


      <form
        className="job-analysis-form"
        onSubmit={handleSubmit}
      >
        <div className="job-text-field">
          <label
            htmlFor="job-description"
          >
            Job Description
          </label>

          <textarea
            id="job-description"
            value={jobText}
            onChange={(event) =>
              setJobText(
                event.target.value
              )
            }
            placeholder="Paste the job description here..."
          />
        </div>


        <div className="job-file-field">
          <div>
            <span>
              Or upload the job posting
            </span>

            <p>
              PDF files up to 5 MB
            </p>
          </div>

          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={(event) =>
              setJobFile(
                event.target.files?.[0]
                  || null
              )
            }
          />

          {jobFile && (
            <span className="selected-job-file">
              {jobFile.name}
            </span>
          )}
        </div>


        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Analyzing Career Gap..."
            : "Analyze Career Gap"}
        </button>


        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </form>


      {jobAnalysis && (
        <div className="job-analysis-result">
          <div className="job-analysis-title">
            <div>
              <span>
                Target Role
              </span>

              <h4>
                {jobAnalysis.job_title}
              </h4>
            </div>

            {jobAnalysis.experience
              .minimum_years !== null && (
              <div className="experience-badge">
                {
                  jobAnalysis.experience
                    .minimum_years
                }
                + years
              </div>
            )}
          </div>


          <SkillGroup
            title="Required Skills"
            skills={
              jobAnalysis.required_skills
            }
          />

          <SkillGroup
            title="Preferred Skills"
            skills={
              jobAnalysis.preferred_skills
            }
          />
        </div>
      )}


      {gapAnalysis && (
        <div className="career-gap-result">
          <div className="coverage-card">
            <span>
              Required Skill Coverage
            </span>

            <strong>
              {
                gapAnalysis.required_skill_coverage
              }
              %
            </strong>

            <p>
              Based only on repository
              evidence currently available
              to RepoLens.
            </p>
          </div>


          <div className="gap-columns">
            <GapColumn
              title="Matched"
              type="matched"
              skills={
                gapAnalysis.matched_required
              }
            />

            <GapColumn
              title="Missing"
              type="missing"
              skills={
                gapAnalysis.missing_required
              }
            />
          </div>


          {gapAnalysis.partial_required
            .length > 0 && (
            <div className="partial-skills">
              <h4>
                Partial Evidence
              </h4>

              {gapAnalysis.partial_required.map(
                (item) => (
                  <article
                    key={item.skill}
                  >
                    <strong>
                      {item.skill}
                    </strong>

                    <span>
                      Related repository
                      evidence:
                    </span>

                    <div>
                      {item.related_evidence.map(
                        (evidence) => (
                          <code
                            key={
                              evidence
                            }
                          >
                            {evidence}
                          </code>
                        )
                      )}
                    </div>
                  </article>
                )
              )}
            </div>
          )}


          <div className="learning-priorities">
            <h4>
              Learning Priorities
            </h4>

            <div>
              {gapAnalysis
                .learning_priorities
                .map(
                  (
                    priority,
                    index
                  ) => (
                    <span
                      key={priority}
                    >
                      {index + 1}.{" "}
                      {priority}
                    </span>
                  )
                )}
            </div>
          </div>


          {gapAnalysis
            .project_recommendations
            .length > 0 && (
            <div className="career-projects">
              <h4>
                Projects to Close the Gap
              </h4>

              <div className="career-project-grid">
                {gapAnalysis
                  .project_recommendations
                  .map((project) => (
                    <article
                      key={
                        project.title
                      }
                    >
                      <h5>
                        {project.title}
                      </h5>

                      <p>
                        {
                          project.description
                        }
                      </p>

                      <span>
                        Targets
                      </span>

                      <div className="career-tags">
                        {project.targets.map(
                          (target) => (
                            <code
                              key={
                                target
                              }
                            >
                              {target}
                            </code>
                          )
                        )}
                      </div>

                      <span>
                        Technologies
                      </span>

                      <div className="career-tags">
                        {project
                          .technologies
                          .map(
                            (
                              technology
                            ) => (
                              <code
                                key={
                                  technology
                                }
                              >
                                {
                                  technology
                                }
                              </code>
                            )
                          )}
                      </div>
                    </article>
                  ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}


function SkillGroup({
  title,
  skills,
}) {
  return (
    <div className="job-skill-group">
      <h5>{title}</h5>

      {skills.length === 0 ? (
        <p>
          No supported skills were detected.
        </p>
      ) : (
        <div>
          {skills.map((skill) => (
            <span key={skill}>
              {skill}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}


function GapColumn({
  title,
  skills,
  type,
}) {
  return (
    <div
      className={`gap-column gap-${type}`}
    >
      <h4>{title}</h4>

      {skills.length === 0 ? (
        <p>
          No skills in this category.
        </p>
      ) : (
        skills.map((skill) => (
          <div
            className="gap-skill"
            key={skill}
          >
            <span>
              {type === "matched"
                ? "✓"
                : "×"}
            </span>

            {skill}
          </div>
        ))
      )}
    </div>
  );
}


export default CareerGap;