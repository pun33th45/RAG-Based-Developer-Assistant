import { Bot, ChevronDown, ChevronUp, Loader2, Send, User } from "lucide-react";
import { useState } from "react";
import { askQuestion } from "../api";

const starterQuestions = ["Explain the architecture", "Find potential bugs", "What are the main entry points?"];

export default function Chat({ indexedSummary }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Upload a project, then ask me to explain it, trace behavior, or look for bugs.",
      sources: [],
    },
  ]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [showContext, setShowContext] = useState(false);

  async function submitQuestion(value = question) {
    const trimmed = value.trim();
    if (!trimmed || loading) return;

    setQuestion("");
    setLoading(true);
    setMessages((current) => [...current, { role: "user", content: trimmed, sources: [] }]);

    try {
      const result = await askQuestion(trimmed);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: result.answer, sources: result.sources || [] },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: error.response?.data?.detail || "I could not answer that yet. Upload files and try again.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitQuestion();
    }
  }

  return (
    <main className="mx-auto grid max-w-6xl grid-rows-[1fr_auto] gap-4 px-5 py-6">
      <div className="min-h-[58vh] overflow-hidden rounded-md border border-line bg-panel">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <div>
            <h2 className="text-sm font-semibold text-white">Assistant</h2>
            <p className="text-xs text-slate-400">
              {indexedSummary
                ? `${indexedSummary.documents} files indexed, ${indexedSummary.chunks} chunks ready`
                : "RAG answers grounded in your uploaded files"}
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowContext((value) => !value)}
            className="inline-flex items-center gap-2 rounded-md border border-line px-3 py-2 text-xs text-slate-200 transition hover:bg-white/5"
          >
            {showContext ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            Context
          </button>
        </div>

        <div className="max-h-[62vh] space-y-4 overflow-y-auto px-4 py-5">
          {messages.map((message, index) => (
            <article key={`${message.role}-${index}`} className="flex gap-3">
              <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-line bg-ink">
                {message.role === "user" ? (
                  <User className="h-4 w-4 text-slate-200" />
                ) : (
                  <Bot className="h-4 w-4 text-accent" />
                )}
              </div>
              <div className="min-w-0 flex-1">
                <div className="whitespace-pre-wrap text-sm leading-6 text-slate-100">{message.content}</div>
                {showContext && message.sources?.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {message.sources.map((source, sourceIndex) => (
                      <details key={`${source.source}-${sourceIndex}`} className="rounded-md border border-line bg-ink p-3">
                        <summary className="cursor-pointer text-xs font-medium text-slate-300">{source.source}</summary>
                        <pre className="mt-2 max-h-56 overflow-auto whitespace-pre-wrap text-xs leading-5 text-slate-400">
                          {source.content}
                        </pre>
                      </details>
                    ))}
                  </div>
                )}
              </div>
            </article>
          ))}
          {loading && (
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Loader2 className="h-4 w-4 animate-spin" />
              Thinking through the retrieved context...
            </div>
          )}
        </div>
      </div>

      <div className="rounded-md border border-line bg-panel p-4">
        <div className="mb-3 flex flex-wrap gap-2">
          {starterQuestions.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => submitQuestion(item)}
              className="rounded-md border border-line px-3 py-1.5 text-xs text-slate-300 transition hover:bg-white/5"
            >
              {item}
            </button>
          ))}
        </div>
        <div className="flex gap-3">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={handleKeyDown}
            rows={2}
            placeholder="Ask about architecture, bugs, or a specific function..."
            className="min-h-12 flex-1 resize-none rounded-md border border-line bg-ink px-3 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-accent"
          />
          <button
            type="button"
            onClick={() => submitQuestion()}
            disabled={loading || !question.trim()}
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-md bg-accent text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            aria-label="Send question"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>
    </main>
  );
}
