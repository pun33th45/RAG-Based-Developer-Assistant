import { FileArchive, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";
import { uploadFile } from "../api";

export default function Upload({ onIndexed }) {
  const inputRef = useRef(null);
  const [fileName, setFileName] = useState("");
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setStatus("loading");
    setMessage("Indexing your upload...");

    try {
      const result = await uploadFile(file);
      setStatus("success");
      setMessage(`${result.documents} files indexed into ${result.chunks} chunks.`);
      onIndexed?.(result);
    } catch (error) {
      setStatus("error");
      setMessage(error.response?.data?.detail || "Upload failed.");
    } finally {
      event.target.value = "";
    }
  }

  const statusColor = {
    idle: "text-slate-400",
    loading: "text-amber-300",
    success: "text-emerald-300",
    error: "text-rose-300",
  }[status];

  return (
    <section className="border-b border-line bg-panel/70">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-5 py-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-md border border-line bg-ink">
            <FileArchive className="h-5 w-5 text-accent" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white">DevInsight AI</h1>
            <p className={`text-sm ${statusColor}`}>{message || "Upload a zip or source document to start."}</p>
          </div>
        </div>

        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".zip,.py,.js,.jsx,.ts,.tsx,.txt,.md"
          onChange={handleUpload}
        />
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={status === "loading"}
          className="inline-flex items-center justify-center gap-2 rounded-md bg-accent px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <UploadCloud className="h-4 w-4" aria-hidden="true" />
          {status === "loading" ? "Uploading" : fileName ? "Upload Another" : "Upload Codebase"}
        </button>
      </div>
    </section>
  );
}
