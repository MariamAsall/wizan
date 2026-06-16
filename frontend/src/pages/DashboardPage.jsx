import { useState } from "react"
import { useNavigate } from "react-router-dom"
import "./Dashboard.css"

import VoiceRecorder from "../components/VoiceRecorder"
import VoicePlanControls from "../components/VoicePlanControls"

const WEEK_SCORES = [58, 72, 65, 80, 70, 74, 74]
const WEEK_DAYS   = ["M", "T", "W", "T", "F", "S", "S"]
const MAX_SCORE   = Math.max(...WEEK_SCORES)

const INITIAL_TASKS = [
  { id: 1, text: "Morning quiz ✓", cost: "low", done: true },
  { id: 2, text: "Review lecture notes for Chapter 4", cost: "med", done: false },
  { id: 3, text: "Submit database assignment", cost: "high", done: false },
  { id: 4, text: "Reply to team messages", cost: "low", done: false },
  { id: 5, text: "Plan weekend study session", cost: "low", done: false },
]

function ScoreCircle({ score }) {
  const r = 35
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ

  return (
    <div className="relative mx-auto mb-3" style={{ width: 90, height: 90 }}>
      <svg viewBox="0 0 90 90" width="90" height="90" style={{ transform: "rotate(-90deg)" }}>
        <circle cx="45" cy="45" r={r} fill="none" stroke="var(--cream3)" strokeWidth="8" />
        <circle
          cx="45"
          cy="45"
          r={r}
          fill="none"
          stroke="var(--sage)"
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
        />
      </svg>

      <span className="score-num-overlay">{score}</span>
    </div>
  )
}

export default function DashboardPage() {
  const navigate = useNavigate()

  const [tasks, setTasks] = useState(INITIAL_TASKS)

  // 🔥 NEW: Voice Plan state
  const [voicePlan, setVoicePlan] = useState("Click record to generate your AI daily plan")

  const toggle = (id) =>
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, done: !t.done } : t))
    )

  const today = new Date().toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  })

  return (
    <div className="dash-root">
      <div className="dash-wrap">

        {/* Greeting */}
        <div className="mb-8">
          <p className="dash-eyebrow">{today}</p>
          <h1 className="dash-hello">
            Good morning, <em>Mariam</em> 👋
          </h1>
          <p className="dash-sub">Your cognitive score is ready</p>
        </div>

        {/* Score + Chart */}
        <div className="dash-grid">
          <div className="score-card">
            <div className="score-card-bar" />
            <p className="score-card-label">Today's cognitive score</p>
            <ScoreCircle score={74} />
            <div className="score-status">
              <span className="score-status-pill">Good day 🌿</span>
            </div>
          </div>

          <div className="mini-chart">
            <p className="mini-chart-label">7-day trend</p>
            <div className="bars">
              {WEEK_SCORES.map((s, i) => (
                <div key={i} className="bar-col">
                  <div
                    className="bar"
                    style={{
                      height: Math.round((s / MAX_SCORE) * 60),
                      background: i === WEEK_SCORES.length - 1 ? "var(--sage)" : "var(--cream3)",
                    }}
                  />
                  <span className="bar-day">{WEEK_DAYS[i]}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="stat-row">
          {[
            { num: "5", lbl: "Tasks allowed" },
            { num: "2", lbl: "Postponed" },
            { num: "3 🔥", lbl: "Day streak" },
          ].map(({ num, lbl }) => (
            <div key={lbl} className="stat-card">
              <div className="stat-num">{num}</div>
              <div className="stat-lbl">{lbl}</div>
            </div>
          ))}
        </div>

        {/* 🧠 NEW VOICE SECTION (ADDED ONLY) */}
        <div className="today-plan">
          <div className="section-head">
            <h2 className="section-title">AI Voice Assistant</h2>
            <span className="badge-green">NEW</span>
          </div>

          {/* Recorder */}
          <VoiceRecorder onPlan={setVoicePlan} />

          {/* Plan Output */}
          <div className="mt-4 p-3 bg-muted rounded-lg text-sm">
            {voicePlan}
          </div>

          {/* Text-to-Speech */}
          <VoicePlanControls text={voicePlan} />
        </div>

        {/* Today's plan (EXISTING - unchanged) */}
        <div className="today-plan">
          <div className="section-head">
            <h2 className="section-title">Today's plan</h2>
            <span className="badge-green">5 tasks</span>
          </div>

          {tasks.map((task) => (
            <div key={task.id} className="task-row">
              <button
                className={`task-checkbox ${task.done ? "done" : ""}`}
                onClick={() => toggle(task.id)}
              >
                {task.done && (
                  <span className="text-white text-xs font-bold">✓</span>
                )}
              </button>

              <span className={`task-text ${task.done ? "done" : ""}`}>
                {task.text}
              </span>

              <span className={`cost-${task.cost}`}>
                {{ low: "Low", med: "Medium", high: "High" }[task.cost]}
              </span>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="dash-cta">
          <button
            className="btn-dash-cta"
            onClick={() => navigate("/tasks")}
          >
            View full task board →
          </button>
        </div>

      </div>
    </div>
  )
}