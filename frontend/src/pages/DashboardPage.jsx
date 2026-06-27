import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"


import "./Dashboard.css"
import api from "../api/axios"

export default function DashboardPage() {
  const navigate = useNavigate()
const { t, i18n } = useTranslation()
  const isAr = i18n.language === "ar"

  const [tasks, setTasks] = useState([])
  const [briefing, setBriefing] = useState("")
  const [loading, setLoading] = useState(true)

  const user = JSON.parse(localStorage.getItem("user") || "{}")
useEffect(() => {
  const fetchDashboard = async () => {
    try {
      // 1. tasks (لازم تشتغل حتى لو briefing فشل)
      const tasksRes = await api.get("/tasks/")
      setTasks(tasksRes.data || [])

      // 2. briefing (لو فشل ما يكسرش الصفحة)
      try {
        const briefingRes = await api.get("/briefing/")

        setBriefing(
          briefingRes.data?.briefing ||
          briefingRes.data?.message ||
          ""
        )

      } catch (err) {
        if (err.response?.status === 404) {
          setBriefing(t("dashboard.quiz_first"))
        } else {
          setBriefing(t("dashboard.ai_error"))
        }
      }

    } catch (err) {
      console.error("Dashboard Error:", err)
      setBriefing(t("dashboard.dashboard_error"))
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
    <div className="tasks-loading">
      <div className="tasks-spinner" />
      <p>{t("dashboard.loading")}</p>
    </div>
  )
}

  return (
    <div className="dash-root" dir={isAr ? "rtl" : "ltr"}>
      <div className="dash-wrap">

        {/* HERO */}
        <div className="hero-card">
          <div className="hero-top">

            <div>
            <h1 className="hero-title">
  {t("dashboard.welcome")}{" "}
  {user?.first_name || user?.username || t("dashboard.user")} 👋
    </h1>

              <p className="hero-sub">
                {t("dashboard.subtitle")}
              </p>
            </div>

            <button
              className="profile-btn"
              onClick={() => navigate("/profile")}
            >
              👤 {t("dashboard.profile")}
            </button>

          </div>
        </div>

        {/* STATS */}
        <div className="wellness-grid">

          <div className="wellness-card">
            <div className="wellness-label">
              {t("dashboard.total_tasks")}
            </div>
            <div className="wellness-value">
              {tasks.length}
            </div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">
              {t("dashboard.completed")}
            </div>
            <div className="wellness-value">
              {completedTasks}
            </div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">
              {t("dashboard.pending")}
            </div>
            <div className="wellness-value">
              {pendingTasks}
            </div>
          </div>

          <div className="wellness-card">
            <div className="wellness-label">
              {t("dashboard.progress")}
            </div>
            <div className="wellness-value">
              {progress}%
            </div>
          </div>

        </div>

        {/* PROGRESS BAR */}
        <div className="overview-card">

          <h2 className="section-title">
              {t("dashboard.productivity_progress")}
          </h2>

          <div className="progress-container">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>

            <p className="progress-text">
            {t("dashboard.progress_text", {
  completed: completedTasks,
  total: tasks.length,
})}
            </p>
          </div>

        </div>

        {/* AI BRIEFING */}
        <div className="ai-card">

          <div className="ai-header">
            🧠 {t("dashboard.ai_briefing")}
          </div>

          <p className="ai-text">
             {briefing || t("dashboard.no_briefing")}
          </p>

        </div>

        {/* TASKS */}
        <div className="today-plan">

          <div className="section-head">
            <h2 className="section-title">
              {t("dashboard.today_tasks")}
            </h2>

            <span className="badge-green">
              {tasks.length}
            </span>
          </div>

          {tasks.length === 0 ? (
            <p className="dash-sub">
              {t("dashboard.no_tasks")}
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
                    {t(`tasks.priority.${task.priority}`)}
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
            {t("dashboard.view_tasks")}
          </button>
        </div>

      </div>
    </div>
  )
}