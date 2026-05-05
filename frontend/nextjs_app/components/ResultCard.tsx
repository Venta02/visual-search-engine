"use client";

import Image from "next/image";
import { getImageUrl, SearchResult } from "@/lib/api";

type Props = {
  hit: SearchResult;
  rank: number;
};

export default function ResultCard({ hit, rank }: Props) {
  const isPositive = hit.score >= 0;
  const scoreColor = isPositive ? "text-emerald-400" : "text-zinc-500";
  const scoreLabel = isPositive ? `+${hit.score.toFixed(3)}` : hit.score.toFixed(3);

  return (
    <div className="group relative overflow-hidden rounded-xl bg-zinc-900 ring-1 ring-zinc-800 transition-all duration-300 hover:ring-zinc-700 hover:shadow-2xl hover:shadow-emerald-500/5 hover:-translate-y-1">
      <div className="absolute top-3 left-3 z-10 flex h-7 w-7 items-center justify-center rounded-full bg-black/70 backdrop-blur text-xs font-mono font-medium text-white">
        {rank}
      </div>

      <div className={`absolute top-3 right-3 z-10 rounded-md bg-black/70 backdrop-blur px-2 py-1 font-mono text-xs ${scoreColor}`}>
        {scoreLabel}
      </div>

      <div className="aspect-square relative overflow-hidden bg-zinc-950">
        <Image
          src={getImageUrl(hit.id)}
          alt={hit.payload.filename || hit.id}
          fill
          sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
          className="object-cover transition-transform duration-500 group-hover:scale-105"
          unoptimized
        />
      </div>

      <div className="px-3 py-2.5 text-xs text-zinc-500 truncate">
        {hit.payload.filename || hit.id}
      </div>
    </div>
  );
}
