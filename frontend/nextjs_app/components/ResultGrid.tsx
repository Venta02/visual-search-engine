"use client";

import { SearchResult } from "@/lib/api";
import ResultCard from "./ResultCard";

type Props = {
  results: SearchResult[];
  loading?: boolean;
};

export default function ResultGrid({ results, loading }: Props) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="aspect-square rounded-xl bg-zinc-900 ring-1 ring-zinc-800 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-20 text-zinc-500">
        <p className="text-lg">No results yet</p>
        <p className="text-sm mt-1">Search for something to see matches</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {results.map((hit, i) => (
        <ResultCard key={hit.id} hit={hit} rank={i + 1} />
      ))}
    </div>
  );
}
