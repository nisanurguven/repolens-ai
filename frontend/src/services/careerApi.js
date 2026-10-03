const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


export async function analyzeJobDescription(
  text,
  file
) {
  const formData = new FormData();

  if (text.trim()) {
    formData.append(
      "text",
      text.trim()
    );
  }

  if (file) {
    formData.append(
      "file",
      file
    );
  }

  const response = await fetch(
    `${API_BASE_URL}/api/job-analysis`,
    {
      method: "POST",
      body: formData,
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The job analysis service returned an invalid response."
    );
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
        "Job description could not be analyzed."
    );
  }

  return data;
}


export async function analyzeCareerGap(
  profile,
  jobAnalysis
) {
  const response = await fetch(
    `${API_BASE_URL}/api/career-gap`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        profile,
        job_analysis: jobAnalysis,
      }),
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The career gap service returned an invalid response."
    );
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
        "Career gap analysis failed."
    );
  }

  return data;
}