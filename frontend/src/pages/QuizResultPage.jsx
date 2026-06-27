import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"
import api from "@/api/axios"
import "./QuizResult.css"

function getScoreState(score) {
  if (score >= 60) return { color: "#22c55e" }
  if (score >= 30) return { color: "var(--primary)" }
  return { color: "var(--destructive)" }
}

const LOAD_EMOJIS = {
  LOW: "🌟",
  MEDIUM: "✦",
  HIGH: "⚡",
}

export default function QuizResultPage() {
  const navigate = useNavigate()
  const { t, i18n } = useTranslation("")

  const [data, setData] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api
      .get("/allowed-tasks/")
      .then((res) => setData(res.data))
      .catch(() => setError(t("error")))
      .finally(() => setLoading(false))
  }, [t])

  if (loading) {
    return (
      <div className="result-loading">
        <div className="result-spinner" />
        <p>{t("result.loading")}</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="result-loading">
        <p className="result-error">{error}</p>
      </div>
    )
  }

  const { score = 0, cognitive_load = "medium", allowed_tasks = [] } = data

  const { color } = getScoreState(score)

  const loadInfo = {
    emoji: LOAD_EMOJIS[cognitive_load] || "✦",
    title: t(`result.load.${cognitive_load}.title`),
    desc: t(`result.load.${cognitive_load}.desc`),
  }

  const postponedCount = 3 - allowed_tasks.length

  return (
    <div
      className="result-root"
      dir={i18n.language === "ar" ? "rtl" : "ltr"}
    >
      <div className="result-wrap">

        <div className="result-score-card">
          <div className="score">
            <span
              className="result-score-number"
              style={{ color }}
            >
              {score}
            </span>

            <span className="result-score-max">/100</span>
          </div>

          <div className="result-state">
            <h2 className="result-state-title">
              {loadInfo.title} {loadInfo.emoji}
            </h2>

            <p className="result-state-desc">
              {loadInfo.desc}
            </p>
          </div>
        </div>

        <div className="result-info-card">
          <div>
            <span className="result-info-emoji">✅</span>
            <span className="result-info-title">
              {t("result.allowedToday")}
            </span>
          </div>

          <div>
            <p className="result-info-desc">
              {allowed_tasks.length}{" "}
              {allowed_tasks.length === 1
                ? t("result.taskType")
                : t("result.taskTypes")}
              {" — "}
              {allowed_tasks
                .map((task) => t(`result.tasks.${task}`))
                .join(", ")}
            </p>
          </div>
        </div>

        {postponedCount > 0 && (
          <div className="result-info-card">
            <div>
              <span className="result-info-emoji">⏳</span>
            <span className="result-info-title">
                {t("result.postponed")}
              </span>
            </div>
            <div>
              <p className="result-info-desc">
                {t("result.postponedDesc", {
                  count: postponedCount,
                  label:
                    postponedCount === 1
                      ? t("result.taskType")
                      : t("result.taskTypes"),
                })}
              </p>
            </div>
          </div>
        )}

        <div className="result-info-card">
          <div>
            <span className="result-info-emoji">💡</span>

            <span className="result-info-title">
              {t("result.wizanTip")}
            </span>
          </div>

          <div>
            <p className="result-info-desc">
              {t(`result.tips.${cognitive_load}`)}
            </p>
          </div>
        </div>

        <button
          className="result-btn"
          onClick={() => navigate("/dashboard")}
        >
          {t("result.goDashboard")}
        </button>

      </div>
    </div>
  )
}
