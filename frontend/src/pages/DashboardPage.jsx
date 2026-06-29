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


const dashboardTasks = tasks.filter(
  task =>
    task.status === "allowed" ||
    task.status === "completed"
);


const completedTasks = dashboardTasks.filter(
  task => task.status === "completed"
).length;

const pendingTasks = dashboardTasks.filter(
  task => task.status === "allowed"
).length;

const progress =
  dashboardTasks.length > 0
    ? Math.round((completedTasks / dashboardTasks.length) * 100)
    : 0;





const toggleTask = async (id) => {
  try {
    const res = await api.patch(`/tasks/${id}/toggle-complete/`);

    setTasks(prev =>
      prev.map(task =>
        task.id === id
          ? { ...task, status: res.data.status }
          : task
      )
    );
  } catch (err) {
    console.error(err);
  }
};

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
              {dashboardTasks.length}
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
  total: dashboardTasks.length,
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
              {dashboardTasks.length}
            </span>
          </div>

          {dashboardTasks.length === 0 ? (
            <p className="dash-sub">
              {t("dashboard.no_tasks")}
            </p>
          ) : (
            dashboardTasks.map((task) => {
              const isDone = task.status === "completed"

              return (
                <div
                  key={task.id}
                  className="task-row"
                >
                  <button
                    className={`task-checkbox ${isDone ? "done" : ""}`}
                    onClick={() => toggleTask(task.id)}
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