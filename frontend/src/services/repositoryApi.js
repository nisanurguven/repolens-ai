const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

export async function analyzeRepository(
  repositoryUrl
) {
  const response = await fetch(
    `${API_BASE_URL}/api/analyze`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        url: repositoryUrl,
      }),
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The server returned an invalid response."
    );
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
        "Repository analysis failed."
    );
  }

  return data;
}

export async function generateAIAnalysis(
  analysis
) {
  const response = await fetch(
    `${API_BASE_URL}/api/repository/ai-analysis`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        analysis,
      }),
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The AI service returned an invalid response."
    );
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
        "AI analysis could not be generated."
    );
  }

  return data;
}

export async function buildDeveloperProfile(
  analysis
) {
  const response = await fetch(
    `${API_BASE_URL}/api/developer-profile`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        analysis,
      }),
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "The developer profile service returned an invalid response."
    );
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
        "Developer profile could not be generated."
    );
  }

  return data;
}