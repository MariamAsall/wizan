import { useState, useRef, useEffect } from "react"
import "./Chat.css"

function Citation({ page }) {
  return <span className="citation">📄 {page}</span>
}

const INITIAL_MESSAGES = [
  {
    id: 1,
    role: "user",
    text: "What is the difference between HNSW and IVF index in pgvector?",
  },
  {
    id: 2,
    role: "ai",
    content: (
      <>
        <strong>HNSW (Hierarchical Navigable Small World)</strong> builds a multi-layer graph
        structure where each node connects to its nearest neighbours at different scales. It offers
        very fast approximate nearest-neighbour search with high recall, but consumes more memory
        during index build. <Citation page="p. 12" />
        <br /><br />
        <strong>IVF (Inverted File Index)</strong> clusters vectors into Voronoi cells during
        training and searches only the closest clusters at query time. It is more memory-efficient
        and faster to build, but requires a separate training step and recall depends on the number
        of probes. <Citation page="p. 15" />
        <br /><br />
        For your Wizan project, HNSW is the better choice since you need low-latency live search
        and your dataset fits in memory.
      </>
    ),
    sources: [
      "Database Systems — Ch. 5, p. 12",
      "Vector Search Guide — p. 15",
    ],
  },
  {
    id: 3,
    role: "user",
    text: "Can you give me a simple analogy for HNSW?",
  },
  {
    id: 4,
    role: "ai",
    content: (
      <>
        Think of it like a city with highways, main roads, and side streets. The top layer of HNSW
        is the highway — it lets you jump large distances quickly. Each lower layer adds more detail
        until you reach the exact neighbourhood you want. <Citation page="p. 13" />
      </>
    ),
    sources: ["Database Systems — Ch. 5, p. 13"],
  },
]

export default function ChatPage() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES)
  const [draft, setDraft]       = useState("")
  const bottomRef               = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const send = () => {
    if (!draft.trim()) return
    setMessages((p) => [
      ...p,
      { id: Date.now(), role: "user", text: draft.trim() },
    ])
    setDraft("")
  }

  return (
    <div className="chat-root">
      <div className="chat-wrap">

        {/* Header */}
        <div className="mb-6">
          <h1 className="chat-title">Study assistant</h1>
          <p className="chat-sub">
            Ask anything from your course materials — answers come with sources.
          </p>
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {messages.map((msg) =>
            msg.role === "user" ? (
              <p key={msg.id} className="msg-user">{msg.text}</p>
            ) : (
              <div key={msg.id} className="msg-ai-wrap">
                <div className="msg-ai">
                  <p className="msg-ai-name">Wizan · Study assistant</p>
                  {msg.content}
                </div>
                {msg.sources?.length > 0 && (
                  <div className="source-chips">
                    {msg.sources.map((s) => (
                      <button key={s} className="source-chip">
                        <span className="source-icon">PDF</span>
                        {s}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="chat-input-bar">
          <textarea
            className="chat-textarea"
            rows={1}
            placeholder="Ask a study question…"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send() }
            }}
          />
          <button className="btn-send" onClick={send}>Send</button>
        </div>

      </div>
    </div>
  )
}
