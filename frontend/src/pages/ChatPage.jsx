import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";
import { Send, Sparkles, ThumbsUp, ThumbsDown } from "lucide-react";
import api from "../api/axios";


async function getReply(question) {
  const { data } = await api.post("/chat/study/", { query: question });
  return { answer: data.answer, sources: data.sources };
}

function Avatar({ role }) {
  if (role === "user") {
    return (
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-medium text-background">
        {JSON.parse(localStorage.getItem("user"))?.first_name?.charAt(0).toUpperCase() || "U"}
      </div>
    );
  }
  return (
    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-primary/50 to-primary text-background">
      <Sparkles size={14} />
    </div>
  );
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 p-1">
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary/50 [animation-delay:-0.3s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary/50 [animation-delay:-0.15s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary/50" />
    </div>
  );
}

export default function ChatPage() {
  const { t, i18n } = useTranslation();
  const dir = i18n.dir();

  const [messages, setMessages] = useState(() => {
  const saved = sessionStorage.getItem("chat_messages");
  return saved ? JSON.parse(saved) : [{ role: "assistant", text: t("chat.welcomeMessage"), sources: [] }];
});
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { role: "user", text: input }]);
    setInput("");
    setLoading(true);

    const reply = await getReply(input);
    setMessages((prev) => [...prev, { role: "assistant", text: reply.answer, sources: reply.sources }]);
    setLoading(false);
  };

  const sendFeedback = async (message, rating) => {
  try {
    await api.post("/chat/feedback/", {
      question: messages[messages.length - 2]?.text || "",
      answer: message.text,
      rating,
    });
  } catch (err) {
    console.error(err);
  }
};

  useEffect(() => {
  sessionStorage.setItem("chat_messages", JSON.stringify(messages));
}, [messages]);


  return (
    <div dir={dir} className="flex h-full flex-col">
      <header className="flex items-center gap-3 border-b border-border px-6 py-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-primary/50 to-primary text-background">
          <Sparkles size={16} />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-foreground">{t("chat.title")}</h1>
          <p className="text-xs text-foreground/60">{t("chat.subtitle")}</p>
        </div>
      </header>

      <div className="flex-1 space-y-4 overflow-y-auto p-6">
        {messages.map((msg, i) => {
          const isUser = msg.role === "user";
          const avatar = <Avatar role={msg.role} />;
          const bubble = (
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-[15px] leading-relaxed shadow-sm ${isUser ? "bg-linear-to-br from-primary to-destructive text-background" : "border border-border bg-card text-card-foreground"
                }`}
            >
              <div className="[&_p]:mb-2 [&_p:last-child]:mb-0 [&_strong]:font-semibold [&_ul]:my-2 [&_ul]:ms-4 [&_ul]:list-disc [&_li]:mb-1">
                <ReactMarkdown>{msg.text}</ReactMarkdown>
                {!isUser && (
  <>
    {msg.sources?.length > 0 && (
      <div className="mt-2 flex flex-wrap gap-1.5">
        {msg.sources.map((s, i) => (
          <span
            key={i}
            className="rounded-full border border-border bg-background px-2 py-0.5 text-xs text-foreground/60"
          >
            {s.source} • p.{s.page}
          </span>
        ))}
      </div>
    )}

    <div className="mt-3 flex items-center gap-2">
      <button
        onClick={() => sendFeedback(msg, 1)}
        className="rounded-full p-2 hover:bg-green-100 transition"
      >
        <ThumbsUp size={16} />
      </button>

      <button
        onClick={() => sendFeedback(msg, -1)}
        className="rounded-full p-2 hover:bg-red-100 transition"
      >
        <ThumbsDown size={16} />
      </button>
    </div>
  </>
)}
              </div>
            </div>
          );
          return (
            <div key={i} className={`flex items-end gap-2 ${isUser ? "justify-end" : "justify-start"}`}>
              {isUser ? (
                <>
                  {bubble}
                  {avatar}
                </>
              ) : (
                <>
                  {avatar}
                  {bubble}
                  
                </>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex items-end gap-2 justify-start">
            <Avatar role="assistant" />
            <div className="rounded-2xl border border-border bg-card text-card-foreground px-3 shadow-sm">
              <TypingDots />
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSend} className="border-t border-border px-6 py-4">
        <div className="flex items-center gap-2 rounded-full border border-border bg-card text-card-foreground px-3 py-1.5 transition focus-within:border-primary focus-within:bg-card">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t("chat.placeholder")}
            className="flex-1 bg-transparent px-2 py-1.5 text-[15px] text-foreground placeholder:text-foreground/50 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full cursor-pointer bg-primary text-background transition hover:bg-primary/80 disabled:bg-secondary/70 disabled:text-foreground/50 disabled:cursor-not-allowed"
          >
            <Send size={16} />
          </button>
        </div>
      </form>
    </div>
  );
}