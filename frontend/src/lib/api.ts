import { AnalysisResponse } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeOffer(
  files: File[] = [],
  text: string = "",
  language: string = "bn"
): Promise<AnalysisResponse> {
  const formData = new FormData();

  for (const file of files) {
    formData.append("files", file);
  }

  if (text.trim()) {
    formData.append("text", text.trim());
  }

  formData.append("language", language);

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(
      errorBody.detail || `Request failed with status ${response.status}`
    );
  }

  return response.json();
}

export async function checkHealth(): Promise<{ status: string; env: string }> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json();
}
