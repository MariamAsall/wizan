import { useState } from "react"
import "./Tasks.css"

const INITIAL_ALLOWED = [
  {
    id: 1, title: "Review lecture notes — Chapter 4", cost: "med",
    steps: [
      { text: "Re-read slides 1–15",           done: true  },
      { text: "Highlight key formulas",         done: true  },
      { text: "Write a 1-page summary",         done: false },
      { text: "Test yourself with 5 questions", done: false },
    ],
  },
  {
    id: 2, title: "Submit database assignment", cost: "high",
    steps: [
      { text: "Finish ERD diagram",          done: true  },
      { text: "Write SQL migration files",   done: false },
      { text: "Upload to submission portal", done: false },
    ],
  },
  { id: 3, title: "Reply to team messages", cost: "low", steps: [] },
]

const INITIAL_POSTPONED = [
  {
    id: 4, title: "Write project report — 3000 words", cost: "high",
    reason: "Moved to tomorrow — cognitive cost too high for today's score",
  },
  {
    id: 5, title: "Prepare presentation slides", cost: "high",
    reason: "Moved to Saturday — deadline not urgent",
  },
]

const COST_LABEL = { low: "Low", med: "Medium", high: "High" }

export default function TasksPage() {
  const [input, setInput]         = useState("")
  const [allowed, setAllowed]     = useState(INITIAL_ALLOWED)
  const [postponed, setPostponed] = useState(INITIAL_POSTPONED)

  const addTask = () => {
    if (!input.trim()) return
    setAllowed((p) => [...p, { id: Date.now(), title: input.trim(), cost: "low", steps: [] }])
    setInput("")
  }

  return (
    <div className="tasks-root">
      <div className="tasks-wrap">

        {/* Header */}
        <div className="mb-7">
          <h1 className="tasks-title">Task board</h1>
          <p className="tasks-sub">
            Score today:{" "}
            <span className="score-pill">74 — Good 🌿</span>
          </p>
        </div>

        {/* Add task */}
        <div className="add-task-bar">
          <input
            type="text"
            className="add-task-input"
            placeholder="Add a new task…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addTask()}
          />
          <button className="btn-mic" title="Add by voice">🎙️</button>
          <button className="btn-add-task" onClick={addTask}>+ Add task</button>
        </div>

        {/* Allowed */}
        <div className="task-section-divider mb-3">
          <span>✅ Allowed today</span>
        </div>
        {allowed.map((task) => (
          <div key={task.id} className="task-card">
            <div className="task-card-top">
              <span className="task-card-title">{task.title}</span>
              <span className={`cost-${task.cost}`}>{COST_LABEL[task.cost]}</span>
            </div>
            {task.steps.length > 0 && (
              <div className="task-steps">
                {task.steps.map((s, i) => (
                  <div key={i} className="task-step">
                    <span className={`step-dot ${s.done ? "done" : ""}`} />
                    {s.text}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Postponed */}
        {postponed.length > 0 && (
          <>
            <div className="task-section-divider mt-6 mb-3">
              <span>⏳ Postponed (score too low)</span>
            </div>
            {postponed.map((task) => (
              <div key={task.id} className="task-card postponed">
                <div className="task-card-top">
                  <span className="task-card-title">{task.title}</span>
                  <span className={`cost-${task.cost}`}>{COST_LABEL[task.cost]}</span>
                  <button
                    className="btn-override"
                    onClick={() => setPostponed((p) => p.filter((t) => t.id !== task.id))}
                  >
                    Override
                  </button>
                </div>
                <p className="postpone-reason">{task.reason}</p>
              </div>
            ))}
          </>
        )}

      </div>
    </div>
  )
}
