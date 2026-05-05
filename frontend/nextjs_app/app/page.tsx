"use client";

import { useState, useEffect } from "react";
import SearchBar from "@/components/SearchBar";
import ResultGrid from "@/components/ResultGrid";
import {
  searchByText,
  searchByImage,
  checkHealth,
  SearchResponse,
  HealthResponse,
} from "@/lib/api";

export default function Home() {
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  const handleTextSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchByText(query, 12);
      setResults(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSearch = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchByImage(file, 12);
      setResults(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-white">
      <div className="border-b border-zinc-900 bg-zinc-950/80 backdrop-blur sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${health?.status === "ok" ? "bg-emerald-500" : "bg-red-500"} animate-pulse`} />
            <span className="text-zinc-400 font-mono">
              {health ? (
                <>
                  API <span className="text-zinc-300">v{health.version}</span> · {health.indexed_count.toLocaleString()} images indexed
                </>
              ) : (
                "API offline"
              )}
            </span>
          </div>
          <div className="text-zinc-600 font-mono">SigLIP · Qdrant</div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="mb-12">
          <h1 className="text-5xl font-bold tracking-tight mb-3 bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
            Visual Search Engine
          </h1>
          <p className="text-lg text-zinc-500">
            Multi-modal retrieval powered by SigLIP embeddings
          </p>
        </div>

        <div className="mb-10">
          <SearchBar
            onTextSearch={handleTextSearch}
            onImageSearch={handleImageSearch}
            loading={loading}
          />
        </div>

        {results && !loading && (
          <div className="flex items-baseline justify-between mb-6 pb-4 border-b border-zinc-900">
            <h2 className="text-sm font-medium text-zinc-400">
              {results.total_results} results
            </h2>
            <div className="text-xs font-mono text-zinc-600">
              {results.latency_ms.toFixed(1)}ms · {results.query_type}
            </div>
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-lg bg-red-950/50 ring-1 ring-red-900/50 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        <ResultGrid results={results?.results ?? []} loading={loading} />
      </div>
    </main>
  );
}
