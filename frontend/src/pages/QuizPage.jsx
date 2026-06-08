import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"
import "./Quiz.css"

const MOODS = [
  { em: "😴", lb: "Exhausted" },
  { em: "😐", lb: "Okay"      },
  { em: "🙂", lb: "Good"      },
  { em: "⚡", lb: "Energised" },
]

const SLEEP_OPTIONS = [
  "Less than 5 hours — rough night",
  "5–6 hours — a bit short",
  "7–8 hours — solid sleep",
  "8+ hours — fully rested",
]

export default function QuizPage() {
  const navigate      = useNavigate()
  const { t }         = useTranslation()
  const [step, setStep]   = useState(1)
  const [mood, setMood]   = useState(null)
  const [sleep, setSleep] = useState(2)
  const [focus, setFocus] = useState(7)

  const pct = Math.round((step / 3) * 100)
  const sliderBg = `linear-gradient(to right, var(--primary) ${((focus - 1) / 9) * 100}%, var(--muted) ${((focus - 1) / 9) * 100}%)`
  return (
    <div className="quiz-root">
      <div className="quiz-wrap">
        {/* Progress */}
        <div className="quiz-progress-bg">
          <div className="quiz-progress-fill" style={{ width: `${pct}%` }} />
        </div>

        {/* ── Step 1: Mood ─────────────────────────────── */}
        {step === 1 && (
          <div className="quiz-panel">
            <p className="quiz-step-label">Question 1 of 3</p>
            <h2 className="quiz-question">
              How are you feeling this <em>morning?</em>
            </h2>
            <p className="quiz-hint">Be honest — Wizan adjusts your day based on this.</p>

            <div className="quiz-emoji-row">
              {MOODS.map(({ em, lb }) => (
                <button
                  key={lb}
                  className={`quiz-emoji-btn ${mood === lb ? "selected" : ""}`}
                  onClick={() => setMood(lb)}
                >
                  <span className="em">{em}</span>
                  <span className="lb">{lb}</span>
                </button>
              ))}
            </div>

            <div className="quiz-nav">
              <div />
              <button className="btn-next" onClick={() => setStep(2)}>Next →</button>
            </div>
          </div>
        )}

        {/* ── Step 2: Sleep ────────────────────────────── */}
        {step === 2 && (
          <div className="quiz-panel">
            <p className="quiz-step-label">Question 2 of 3</p>
            <h2 className="quiz-question">
              How was your <em>sleep</em> last night?
            </h2>
            <p className="quiz-hint">Hours and quality both matter.</p>

            <div className="quiz-options">
              {SLEEP_OPTIONS.map((opt, i) => (
                <button
                  key={opt}
                  className={`quiz-opt ${sleep === i ? "selected" : ""}`}
                  onClick={() => setSleep(i)}
                >
                  <span className="quiz-opt-dot">
                    {sleep === i && <span className="quiz-opt-dot-inner" />}
                  </span>
                  <span className="quiz-opt-label">{opt}</span>
                </button>
              ))}
            </div>

            <div className="quiz-nav">
              <button className="btn-back" onClick={() => setStep(1)}>← Back</button>
              <button className="btn-next" onClick={() => setStep(3)}>Next →</button>
            </div>
          </div>
        )}

        {/* ── Step 3: Focus ────────────────────────────── */}
        {step === 3 && (
          <div className="quiz-panel">
            <p className="quiz-step-label">Question 3 of 3</p>
            <h2 className="quiz-question">
              Rate your <em>focus</em> right now
            </h2>
            <p className="quiz-hint">1 = scattered, 10 = laser sharp</p>

            <div className="mb-8">
              <div className="quiz-slider-val">{focus}</div>
              <input
                type="range"
                min="1"
                max="10"
                value={focus}
                onChange={(e) => setFocus(Number(e.target.value))}
                className="quiz-slider"
                style={{ background: sliderBg }}
              />
              <div className="quiz-slider-labels">
                <span>1 — scattered</span>
                <span>10 — laser sharp</span>
              </div>
            </div>

            <div className="quiz-nav">
              <button className="btn-back" onClick={() => setStep(2)}>← Back</button>
              <button className="btn-next" onClick={() => navigate("/dashboard")}>
                See my score →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
