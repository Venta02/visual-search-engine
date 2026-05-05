"use client";

import { useState, useRef, ChangeEvent } from "react";

type Props = {
  onTextSearch: (query: string) => void;
  onImageSearch: (file: File) => void;
  loading: boolean;
};

export default function SearchBar({ onTextSearch, onImageSearch, loading }: Props) {
  const [mode, setMode] = useState<"text" | "image">("text");
  const [query, setQuery] = useState("");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleTextSubmit = () => {
    if (query.trim() && !loading) onTextSearch(query.trim());
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPreviewUrl(URL.createObjectURL(file));
    onImageSearch(file);
  };

  return (
    <div className="w-full">
      <div className="inline-flex rounded-lg bg-zinc-900 p-1 ring-1 ring-zinc-800 mb-4">
        <button
          onClick={() => setMode("text")}
          className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
            mode === "text"
              ? "bg-zinc-800 text-white"
              : "text-zinc-500 hover:text-zinc-300"
          }`}
        >
          Text
        </button>
        <button
          onClick={() => setMode("image")}
          className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
            mode === "image"
              ? "bg-zinc-800 text-white"
              : "text-zinc-500 hover:text-zinc-300"
          }`}
        >
          Image
        </button>
      </div>

      {mode === "text" ? (
        <div className="flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleTextSubmit()}
              placeholder="Describe what you are looking for..."
              className="w-full rounded-xl bg-zinc-900 ring-1 ring-zinc-800 px-5 py-4 text-white placeholder-zinc-600 outline-none transition-all focus:ring-2 focus:ring-emerald-500/50"
              disabled={loading}
            />
          </div>
          <button
            onClick={handleTextSubmit}
            disabled={loading || !query.trim()}
            className="rounded-xl bg-emerald-500 px-6 py-4 font-medium text-black transition-all hover:bg-emerald-400 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      ) : (
        <div className="flex gap-4 items-start">
          <div
            onClick={() => fileInputRef.current?.click()}
            className="flex-1 rounded-xl border-2 border-dashed border-zinc-800 bg-zinc-900/50 px-6 py-10 text-center cursor-pointer transition-all hover:border-emerald-500/50 hover:bg-zinc-900"
          >
            {previewUrl ? (
              <div className="flex items-center justify-center gap-4">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={previewUrl} alt="Query" className="h-20 w-20 rounded-lg object-cover" />
                <div className="text-left">
                  <p className="text-sm text-white">Click to change image</p>
                  <p className="text-xs text-zinc-500 mt-1">Or drag and drop</p>
                </div>
              </div>
            ) : (
              <div>
                <p className="text-sm text-zinc-400">Click to upload an image</p>
                <p className="text-xs text-zinc-600 mt-1">PNG, JPG, WEBP up to 10MB</p>
              </div>
            )}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>
      )}
    </div>
  );
}
