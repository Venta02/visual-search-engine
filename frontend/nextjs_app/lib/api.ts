const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type SearchResult = {
  id: string;
  score: number;
  payload: {
    filename?: string;
    filepath?: string;
    size_bytes?: number;
  };
};

export type SearchResponse = {
  query_type: string;
  latency_ms: number;
  total_results: number;
  results: SearchResult[];
};

export type HealthResponse = {
  status: string;
  version: string;
  qdrant_reachable: boolean;
  redis_reachable: boolean;
  indexed_count: number;
};

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function searchByText(
  query: string,
  limit = 10,
  scoreThreshold?: number
): Promise<SearchResponse> {
  const res = await fetch(`${API_URL}/search/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      limit,
      score_threshold: scoreThreshold ?? null,
    }),
  });
  if (!res.ok) throw new Error(`Search failed: ${res.status}`);
  return res.json();
}

export async function searchByImage(
  file: File,
  limit = 10
): Promise<SearchResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/search/image?limit=${limit}`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(`Search failed: ${res.status}`);
  return res.json();
}

export function getImageUrl(pointId: string): string {
  return `${API_URL}/images/${pointId}`;
}
