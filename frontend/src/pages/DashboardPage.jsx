import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import "./Dashboard.css"
import api from "../api/axios"

function ScoreCircle({ score }) {
  const r = 35
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ

  return (
    <div className="relative mx-auto mb-3" style={{ width: 90, height: 90 }}>
      <svg
        viewBox="0 0 90 90"
        width="90"
        height="90"
        style={{ transform: "rotate(-90deg)" }}
      >
        <circle
          cx="45"
          cy="45"
          r={r}
          fill="none"
          stroke="var(--cream3)"
          strokeWidth="8"
        />
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

  const [score, setScore] = useState(0)
  const [logs, setLogs] = useState([])
  const [briefing, setBriefing] = useState("")
  const [loadMessage, setLoadMessage] = useState("")
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)

  const user = JSON.parse(localStorage.getItem("user") || "{}")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [tasksRes] = await Promise.all([
          api.get("/tasks/")
        ])

        setTasks(tasksRes.data || [])

        // بيانات مؤقتة لحد ما تربط APIs الخاصة بالـ cognitive score
        setScore(78)
        setLogs([
          { score: 72 },
          { score: 80 },
          { score: 76 },
          { score: 84 },
          { score: 69 },
          { score: 90 },
          { score: 78 },
        ])

        setBriefing(
          "Your productivity is improving this week. Focus on high-priority tasks during peak concentration hours."
        )

        setLoadMessage(
          "You are performing well today. Keep your focus on important tasks."
        )
      } catch (err) {
        console.error("Dashboard Error:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  const weekScores = logs
    .slice(0, 7)
    .reverse()
    .map((log) => log.final_score || log.score || 0)

  const maxScore = Math.max(...weekScores, 100)

  const WEEK_DAYS = ["M", "T", "W", "T", "F", "S", "S"]

  const avgScore =
    logs.length > 0
      ? Math.round(
          logs.reduce(
            (sum, log) => sum + (log.final_score || log.score || 0),
            0
          ) / logs.length
        )
      : 0

  const streak = logs.length

  const scoreLabel =
    score >= 80
      ? "Excellent Focus"
      : score >= 60
      ? "Good Focus"
      : score >= 30
      ? "Moderate Focus"
      : "Low Focus"

  const toggle = (id) =>
    setTasks((prev) =>
      prev.map((t) =>
        t.id === id
          ? {
              ...t,
              status:
                t.status === "allowed"
                  ? "pending"
                  : "allowed",
            }
          : t
      )
    )

  if (loading) {
    return (
      <div className="dash-root">
        <div className="dash-wrap">Loading...</div>
      </div>
    )
  }

  return (
    <div className="dash-root">
      <div className="dash-wrap">

        {/* HERO */}
        <div className="hero-card">
          <h1 className="hero-title">
            Welcome back,{" "}
            {user?.first_name || user?.username || "User"} 👋
          </h1>

          <p className="hero-sub">
            Your current cognitive score is {score}.
            Focus on the most important tasks first.
          </p>
        </div>

        {/* QUICK STATS */}
        <div className="wellness-grid">
          <div className="wellness-card">
            <div className="wellness-label">Score</div>
            <div className="wellness-value">{score}</div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">Streak 🔥</div>
            <div className="wellness-value">{streak}</div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">Tasks</div>
            <div className="wellness-value">{tasks.length}</div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">Average</div>
            <div className="wellness-value">{avgScore}</div>
          </div>
        </div>

        {/* SCORE */}
        <div className="score-card">
          <div>
            <ScoreCircle score={score} />

            <div className="score-status">
              <span className="score-status-pill">
                {scoreLabel}
              </span>
            </div>

            <p
              style={{
                textAlign: "center",
                marginTop: "12px",
              }}
              className="dash-sub"
            >
              {loadMessage}
            </p>
          </div>
        </div>

        {/* WEEKLY TREND */}
        <div className="mini-chart">
          <div className="mini-chart-label">
            Weekly Trend
          </div>

          <div className="bars">
            {weekScores.map((s, i) => (
              <div key={i} className="bar-col">
                <div
                  className="bar"
                  style={{
                    height: `${(s / maxScore) * 70}px`,
                  }}
                />

                <span className="bar-day">
                  {WEEK_DAYS[i]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* AI INSIGHT */}
        <div className="ai-summary-card">
          <h2 className="ai-summary-title">
            🧠 AI Insight
          </h2>

          <p className="ai-summary-text">
            {briefing || "No cognitive briefing available."}
          </p>
        </div>

        {/* TODAY TASKS */}
        <div className="today-plan">
          <div className="section-head">
            <h2 className="section-title">
              Today's Tasks
            </h2>

            <span className="badge-green">
              {tasks.length}
            </span>
          </div>

          {tasks.slice(0, 5).map((task) => {
            const isDone = task.status === "allowed"

            return (
              <div key={task.id} className="task-row">
                <button
                  className={`task-checkbox ${
                    isDone ? "done" : ""
                  }`}
                  onClick={() => toggle(task.id)}
                >
                  {isDone && "✓"}
                </button>

                <span
                  className={`task-text ${
                    isDone ? "done" : ""
                  }`}
                >
                  {task.name}
                </span>

                <span
                  className={
                    task.priority === "medium"
                      ? "cost-med"
                      : `cost-${task.priority}`
                  }
                >
                  {{
                    low: "Low",
                    medium: "Medium",
                    high: "High",
                  }[task.priority]}
                </span>
              </div>
            )
          })}
        </div>

        {/* CTA */}
        <div className="dash-cta">
          <button
            className="btn-dash-cta"
            onClick={() => navigate("/tasks")}
          >
            View Full Task Board →
          </button>
        </div>

      </div>
    </div>
  )
}