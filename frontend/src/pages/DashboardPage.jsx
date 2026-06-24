import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import "./Dashboard.css"
import api from "../api/axios"

export default function DashboardPage() {
  const navigate = useNavigate()

  const [tasks, setTasks] = useState([])
  const [briefing, setBriefing] = useState("")
  const [loading, setLoading] = useState(true)

  const user = JSON.parse(localStorage.getItem("user") || "{}")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [tasksRes, briefingRes] = await Promise.all([
          api.get("/tasks/"),
          api.get("/briefing/")
        ])

        setTasks(tasksRes.data || [])

        // support multiple possible API shapes
        setBriefing(
          briefingRes.data?.briefing ||
          briefingRes.data?.message ||
          ""
        )

      } catch (err) {
        console.error("Dashboard Error:", err)
        setBriefing("Unable to load AI briefing at the moment.")
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  const completedTasks = tasks.filter(
    (task) => task.status === "allowed"
  ).length

  const pendingTasks = tasks.length - completedTasks

  const progress =
    tasks.length > 0
      ? Math.round((completedTasks / tasks.length) * 100)
      : 0

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
          <div className="hero-top">

            <div>
              <h1 className="hero-title">
                Welcome back,{" "}
                {user?.first_name ||
                  user?.username ||
                  "User"} 👋
              </h1>

              <p className="hero-sub">
                Here is your daily productivity overview.
              </p>
            </div>

            <button
              className="profile-btn"
              onClick={() => navigate("/profile")}
            >
              👤 Profile
            </button>

          </div>
        </div>

        {/* STATS */}
        <div className="wellness-grid">

          <div className="wellness-card">
            <div className="wellness-label">
              Total Tasks
            </div>
            <div className="wellness-value">
              {tasks.length}
            </div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">
              Completed
            </div>
            <div className="wellness-value">
              {completedTasks}
            </div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">
              Pending
            </div>
            <div className="wellness-value">
              {pendingTasks}
            </div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">
              Progress
            </div>
            <div className="wellness-value">
              {progress}%
            </div>
          </div>

        </div>

        {/* PROGRESS BAR */}
        <div className="overview-card">

          <h2 className="section-title">
            Productivity Progress
          </h2>

          <div className="progress-container">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>

            <p className="progress-text">
              {completedTasks} of {tasks.length} tasks completed
            </p>
          </div>

        </div>

        {/* AI BRIEFING */}
        <div className="ai-card">

          <div className="ai-header">
            🧠 AI Daily Briefing
          </div>

          <p className="ai-text">
            {briefing || "No briefing available."}
          </p>

        </div>

        {/* TASKS */}
        <div className="today-plan">

          <div className="section-head">
            <h2 className="section-title">
              Today's Tasks
            </h2>

            <span className="badge-green">
              {tasks.length}
            </span>
          </div>

          {tasks.length === 0 ? (
            <p className="dash-sub">
              No tasks available.
            </p>
          ) : (
            tasks.slice(0, 5).map((task) => {
              const isDone = task.status === "allowed"

              return (
                <div
                  key={task.id}
                  className="task-row"
                >
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
                    }[task.priority] ||
                      task.priority}
                  </span>
                </div>
              )
            })
          )}

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