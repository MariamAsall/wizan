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
  const [cognitiveLoad, setCognitiveLoad] = useState("")
  const [loadMessage, setLoadMessage] = useState("")
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)

  const user = JSON.parse(localStorage.getItem("user") || "{}")

  const weekScores = logs
    .slice(0, 7)
    .reverse()
    .map((log) => log.final_score || log.score || 0)

  const maxScore = Math.max(...weekScores, 100)

  const WEEK_DAYS = ["M", "T", "W", "T", "F", "S", "S"]

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [scoreRes, logsRes, allowedRes, briefingRes, tasksRes] =
          await Promise.allSettled([
            
            api.get("/cognitive-score/"),
            api.get("/cognitive-log/"),
            api.get("/allowed-tasks/"),
            api.get("/briefing/"),
            api.get("/tasks/"),
          ])

        if (scoreRes.status === "fulfilled") {
          setScore(scoreRes.value.data.score)
        }

        if (logsRes.status === "fulfilled") {
          setLogs(logsRes.value.data)
        }

        if (allowedRes.status === "fulfilled") {
          setCognitiveLoad(allowedRes.value.data.cognitive_load)
          setLoadMessage(allowedRes.value.data.message)
        }

        if (briefingRes.status === "fulfilled") {
          const data = briefingRes.value.data
          setBriefing(
            typeof data === "string"
              ? data
              : data.briefing || data.message || JSON.stringify(data)
          )
        }

        if (tasksRes.status === "fulfilled") {
          setTasks(tasksRes.value.data)
        }
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  const toggle = (id) =>
    setTasks((prev) =>
      prev.map((t) =>
        t.id === id
          ? {
              ...t,
              status: t.status === "allowed" ? "pending" : "allowed",
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
            Here's your cognitive overview today.
          </p>
        </div>

        {/* STATS */}
        <div className="wellness-grid">
          <div className="wellness-card">
            <div className="wellness-label">Cognitive Score</div>
            <div className="wellness-value">{score}</div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">Cognitive Load</div>
            <div className="wellness-value">{cognitiveLoad}</div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">Tasks</div>
            <div className="wellness-value">{tasks.length}</div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">Logs</div>
            <div className="wellness-value">{logs.length}</div>
          </div>
        </div>

        {/* SCORE */}
        <div className="score-card">
          <ScoreCircle score={score} />
        </div>

        {/* WEEKLY TREND */}
        <div className="mini-chart">
          <div className="mini-chart-label">Weekly Trend</div>

          <div className="bars">
            {weekScores.map((s, i) => (
              <div key={i} className="bar-col">
                <div
                  className="bar"
                  style={{
                    height: `${(s / maxScore) * 70}px`,
                  }}
                />
                <span className="bar-day">{WEEK_DAYS[i]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* AI INSIGHT */}
        <div className="ai-summary-card">
          <h2 className="ai-summary-title">🧠 AI Daily Insight</h2>
          <p className="ai-summary-text">
            {briefing || "No cognitive briefing available."}
          </p>
        </div>

        {/* COGNITIVE STATUS */}
        <div className="today-plan">
          <div className="section-head">
            <h2 className="section-title">Cognitive Status</h2>
            <span className="badge-green">{cognitiveLoad}</span>
          </div>
          <p className="dash-sub">{loadMessage}</p>
        </div>

        {/* TASKS */}
        <div className="today-plan">
          <div className="section-head">
            <h2 className="section-title">Today's Tasks</h2>
            <span className="badge-green">{tasks.length}</span>
          </div>

          {tasks.map((task) => {
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

                <span className={`task-text ${isDone ? "done" : ""}`}>
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

        {/* LAST QUIZ */}
        <div className="today-plan">
          <div className="section-head">
            <h2 className="section-title">Last Quiz Answers</h2>
          </div>

          {logs[0]?.quiz_answers?.slice(0, 5)?.map((a, i) => (
            <div key={i} className="task-row">
              <span className="task-text">{a.question_en}</span>
              <span className="badge-green">{a.answer}</span>
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