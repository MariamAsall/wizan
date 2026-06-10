import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"
import api from "@/api/axios"
import "./Quiz.css"

const QUESTIONS_UI = [
  {
    type: "slider",
    labels: ["< 4 hrs 😴", "4–5 hrs", "5–6 hrs", "6–7 hrs", "8+ hrs 🌟"],
    labels_ar: ["أقل من 4 ساعات 😴", "4-5 ساعات", "5-6 ساعات", "6-7 ساعات", "8+ ساعات 🌟"],
  },
  {
    type: "cards",
    options: [
      { value: 1, emoji: "😩", label: "Terrible", label_ar: "سيء جداً" },
      { value: 2, emoji: "😕", label: "Poor", label_ar: "ضعيف" },
      { value: 3, emoji: "😐", label: "Average", label_ar: "متوسط" },
      { value: 4, emoji: "😊", label: "Good", label_ar: "جيد" },
      { value: 5, emoji: "✨", label: "Excellent", label_ar: "ممتاز" },
    ],
  },
  {
    type: "cards",
    options: [
      { value: 1, emoji: "🧘", label: "Calm", label_ar: "هادئ" },
      { value: 2, emoji: "😌", label: "Slight", label_ar: "قليل" },
      { value: 3, emoji: "😤", label: "Moderate", label_ar: "متوسط" },
      { value: 4, emoji: "😰", label: "Very stressed", label_ar: "متوتر جداً" },
      { value: 5, emoji: "🔥", label: "Overwhelmed", label_ar: "مرهق" },
    ],
  },
  {
    type: "cards",
    options: [
      { value: 1, emoji: "🪫", label: "Exhausted", label_ar: "منهك" },
      { value: 2, emoji: "😓", label: "Low", label_ar: "منخفض" },
      { value: 3, emoji: "🙂", label: "Moderate", label_ar: "متوسط" },
      { value: 4, emoji: "💪", label: "Good", label_ar: "جيد" },
      { value: 5, emoji: "⚡", label: "Energized", label_ar: "نشيط" },
    ],
  },
  {
    type: "slider",
    labels: ["🌀 Scattered", "Hard", "Some effort", "Focused", "🎯 Laser"],
    labels_ar: ["🌀 مشتت", "صعب", "بعض الجهد", "مركز", "🎯 تركيز تام"],
  },
  {
    type: "cards",
    options: [
      { value: 1, emoji: "😞", label: "Very low", label_ar: "منخفض جداً" },
      { value: 2, emoji: "😕", label: "Not great", label_ar: "ليس جيداً" },
      { value: 3, emoji: "😐", label: "Neutral", label_ar: "محايد" },
      { value: 4, emoji: "😊", label: "Pretty good", label_ar: "جيد نسبياً" },
      { value: 5, emoji: "🌈", label: "Excellent", label_ar: "ممتاز" },
    ],
  },
]

export default function QuizPage() {
  const navigate = useNavigate()
  const { t, i18n } = useTranslation()
  const isAr = i18n.language === "ar"
  const [questions, setQuestions] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState([])

  useEffect(() => {
    api.get("/quiz/questions/")
      .then((res) => {
        const merged = res.data.map((q, i) => ({ ...q, ...QUESTIONS_UI[i] }))
        setQuestions(merged)
      })
      .catch((err) => {
        setError(t("quiz.error_load"))
      })
      .finally(() => setLoading(false))
  }, [])

  const total = questions.length
  const current = questions[step]
  const currentVal = answers.find((a) => a.question_id === current?.id)?.answer ?? null
  const pct = total ? Math.round(((step + 1) / total) * 100) : 0
  const questionText = current
    ? (isAr ? current.question_text_ar : current.question_text_en)
    : ""
  const canProceed = current?.type === "slider" || currentVal !== null
  const sliderLabels = isAr ? current?.labels_ar : current?.labels

  const handleAnswer = (value) => {
    setError(null)
    setAnswers((prev) => {
      const exists = prev.find((a) => a.question_id === current.id)
      if (exists) return prev.map((a) =>
        a.question_id === current.id ? { ...a, answer: value } : a
      )
      return [...prev, { question_id: current.id, answer: value }]
    })
  }

  const handleNext = async () => {
    if (step < total - 1) {
      setStep((s) => s + 1)
      setError(null)
    } else {
      setSubmitting(true)
      setError(null)
      try {
        const { data } = await api.post("/submit-quiz/", { answers })
        localStorage.setItem("cognitive_score", data.score)
        navigate("/result")
      } catch (e) {
        const serverMessage = e.response?.data?.error
        if (e.response?.status === 400 && serverMessage?.includes("already")) {
          setError(t("quiz.already_done"))
        } else {
          setError(serverMessage || t("quiz.error_generic"))
        }
      } finally {
        setSubmitting(false)
      }
    }
  }

  if (loading) return (
    <div className="quiz-loading">
      <div className="quiz-spinner" />
      <p>{t("quiz.loading")}</p>
    </div>
  )

  return (
    <div className="quiz-root" dir={isAr ? "rtl" : "ltr"}>
      <div className="quiz-wrap">
        <h1 className="quiz-title">{t("quiz.title")}</h1>

        {error && (
          <div className="quiz-error-msg">{error}</div>
        )}

        {/* Progress */}
        <p className="quiz-step-label">
          {t("quiz.step")} {step + 1} {t("quiz.of")} {total}
        </p>
        <div className="quiz-progress-bg">
          <div className="quiz-progress-fill" style={{ width: `${pct}%` }} />
        </div>

        {/* Card */}
        <div className="quiz-panel">
          <h2 className="quiz-question">{questionText}</h2>
          <p className="quiz-hint">
            {current?.type === "slider" ? t("quiz.drag") : t("quiz.tap")}
          </p>

          {/* Emoji cards */}
          {current?.type === "cards" && (
            <div className="quiz-emoji-row">
              {current.options.map((opt) => (
                <button
                  key={opt.value}
                  className={`quiz-emoji-btn ${currentVal === opt.value ? "selected" : ""}`}
                  onClick={() => handleAnswer(opt.value)}
                >
                  <span className="em">{opt.emoji}</span>
                  <span className="lb">{isAr ? opt.label_ar : opt.label}</span>
                </button>
              ))}
            </div>
          )}

          {/* Slider */}
          {current?.type === "slider" && (
            <div className="quiz-slider-wrap" dir="ltr">
              <div className="quiz-slider-val">{currentVal ?? 3}</div>
              <input
                type="range"
                min="1"
                max="5"
                value={currentVal ?? 3}
                onChange={(e) => handleAnswer(Number(e.target.value))}
                className="quiz-slider"
                style={{
                  background: `linear-gradient(to right, var(--color-primary) ${(((currentVal ?? 3) - 1) / 4) * 100}%, var(--color-muted) ${(((currentVal ?? 3) - 1) / 4) * 100}%)`
                }}
              />
              <div className="quiz-slider-labels">
                {sliderLabels?.map((l, i) => <span key={i}>{l}</span>)}
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="quiz-nav">
            <button
              className="btn-back"
              onClick={() => setStep((s) => s - 1)}
              disabled={step === 0}
            >
              {t("quiz.back")}
            </button>
            <button
              className="btn-next"
              onClick={handleNext}
              disabled={!canProceed || submitting}
            >
              {submitting
                ? t("quiz.submitting")
                : step === total - 1
                  ? t("quiz.submit")
                  : t("quiz.next")}
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}