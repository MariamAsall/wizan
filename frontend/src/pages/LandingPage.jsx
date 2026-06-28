import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"
import { Brain } from "lucide-react"
import "./LandingPage.css"

export default function LandingPage() {
  const navigate = useNavigate()
  const { t: tRaw } = useTranslation()
  const t = (key) => tRaw(`landing.${key}`)

  const isAuthed = !!localStorage.getItem("access_token")

  // ── balance beam ──────────────────────────────────────────────
  const [score, setScore] = useState(62)
  const tasks = Math.max(1, Math.round(2 + (score / 100) * 6))
  const taskWord = tasks === 1 ? t("quiz.taskSingular") : t("quiz.taskPlural")
  const tilt = ((score - 50) / 50) * 12

  // ── mini quiz ─────────────────────────────────────────────────
  const totalSteps = 3
  const [quizStep, setQuizStep]       = useState(1)
  const [quizTotal, setQuizTotal]     = useState(0)
  const [quizAnswered, setQuizAnswered] = useState(0)
  const [quizPts, setQuizPts]         = useState(3)

  const quizQuestions = [
    { key: "quiz.q1", opts: ["quiz.q1_opt1", "quiz.q1_opt2", "quiz.q1_opt3"], pts: [5, 3, 1] },
    { key: "quiz.q2", opts: ["quiz.q2_opt1", "quiz.q2_opt2", "quiz.q2_opt3"], pts: [5, 3, 1] },
    { key: "quiz.q3", opts: ["quiz.q3_opt1", "quiz.q3_opt2", "quiz.q3_opt3"], pts: [5, 3, 1] },
  ]

  const quizResultScore = Math.round((quizTotal / 15) * 100)
  let verdictKey = "quiz.verdict_mid"
  if (quizResultScore < 40) verdictKey = "quiz.verdict_low"
  else if (quizResultScore >= 70) verdictKey = "quiz.verdict_high"

  function answerQuiz(pts) {
    const newTotal    = quizTotal + pts
    const newAnswered = quizAnswered + 1
    setQuizTotal(newTotal)
    setQuizAnswered(newAnswered)
    setQuizPts(pts)
    if (newAnswered < totalSteps) {
      setQuizStep(newAnswered + 1)
    } else {
      setQuizStep("done")
      setScore(Math.round((newTotal / 15) * 100))
    }
  }

  function retakeQuiz() {
    setQuizTotal(0)
    setQuizAnswered(0)
    setQuizPts(3)
    setQuizStep(1)
  }

  function faceMouthPath(pts) {
    if (pts <= 1) return "M90 158q30 -10 60 0"
    if (pts <= 3) return "M90 152q30 4 60 0"
    return "M90 150q30 18 60 0"
  }
  function faceEyeR(pts) {
    if (pts <= 1) return 5
    if (pts <= 3) return 6
    return 7
  }

  return (
    <div className="landing-root">

      {/* ── Hero ─────────────────────────────────────────────── */}
      <header className="landing-hero">
        <div className="landing-hero-grid">
          <div>
            <div className="landing-eyebrow">{t("hero.eyebrow")}</div>
            <h1 className="landing-h1" dangerouslySetInnerHTML={{ __html: t("hero.title") }} />
            <p className="landing-hero-sub">{t("hero.sub")}</p>
            <div className="landing-hero-actions">
              {isAuthed ? (
                <button className="landing-btn-primary" onClick={() => navigate("/quiz")}>
                  {t("hero.ctaPrimary")}
                </button>
              ) : (
                <>
                  <Link className="landing-btn-primary" to="/register">
                    {t("hero.ctaPrimary")}
                  </Link>
                  <Link className="landing-btn-ghost" to="/login">
                    {t("hero.ctaGhost")}
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* balance beam */}
          <div className="landing-scale-wrap">
            <div className="landing-scale-readout">
              <span>{t("hero.scoreLabel")} <b>{score}</b>/100</span>
              <span>{t("hero.loadLabel")} <b>{tasks} {taskWord}</b></span>
            </div>
            <svg className="w-full h-auto" viewBox="0 0 420 220">
              <line x1="210" y1="80" x2="210" y2="200" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
              <circle cx="210" cy="80" r="5" fill="currentColor" />
              <g style={{ transform: `rotate(${-tilt}deg)`, transformOrigin: "210px 80px", transition: "transform 0.35s ease" }}>
                <line x1="90" y1="80" x2="330" y2="80" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                <line x1="90" y1="80" x2="90" y2="120" stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
                <line x1="330" y1="80" x2="330" y2="120" stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
                <g>
                  <path d="M65 120 Q90 150 115 120" fill="none" stroke="var(--primary)" strokeWidth="3" strokeLinecap="round" />
                  <text x="90" y="143" textAnchor="middle" fontFamily="monospace" fontSize="11" fill="var(--primary)" fontWeight="600">SCORE</text>
                </g>
                <g>
                  <path d="M305 120 Q330 150 355 120" fill="none" stroke="var(--accent)" strokeWidth="3" strokeLinecap="round" />
                  <text x="330" y="143" textAnchor="middle" fontFamily="monospace" fontSize="11" fill="var(--accent)" fontWeight="600">TASKS</text>
                </g>
              </g>
              <polygon points="210,200 195,215 225,215" fill="currentColor" />
            </svg>
            <div className="landing-slider-row">
              <span className="landing-slider-label">{t("hero.sliderLow")}</span>
              <input
                type="range" min="0" max="100" value={score}
                className="flex-1"
                onChange={(e) => setScore(parseInt(e.target.value, 10))}
              />
              <span className="landing-slider-label">{t("hero.sliderHigh")}</span>
            </div>
          </div>
        </div>
      </header>

      {/* ── Ticker strip ─────────────────────────────────────── */}
      <div className="landing-strip">
        <div className="landing-strip-inner">
          {["MORNING QUIZ", "COGNITIVE SCORE 0–100", "ADAPTIVE TASK REGULATOR", "PLANNING AGENT", "RAG STUDY ASSISTANT", "VOICE INPUT", "PROMPT INJECTION GUARDED",
            "MORNING QUIZ", "COGNITIVE SCORE 0–100", "ADAPTIVE TASK REGULATOR", "PLANNING AGENT", "RAG STUDY ASSISTANT", "VOICE INPUT", "PROMPT INJECTION GUARDED"]
            .map((label, i) => <span key={i}>{label}</span>)}
        </div>
      </div>

      {/* ── How it works ─────────────────────────────────────── */}
      <section id="how" className="landing-section">
        <div className="landing-section-head">
          <div className="landing-section-eyebrow">{t("how.eyebrow")}</div>
          <h2>{t("how.title")}</h2>
          <p>{t("how.sub")}</p>
        </div>
        <div className="landing-states">
          <div className="landing-state-card">
            <div className="landing-state-score">
              <span className="landing-dot landing-dot-low" />
              <span>{t("how.score1")}</span>
            </div>
            <h3>{t("how.card1.title")}</h3>
            <p>{t("how.card1.body")}</p>
            <div className="landing-state-bar"><i style={{ width: "28%", background: "var(--destructive)" }} /></div>
          </div>
          <div className="landing-state-card">
            <div className="landing-state-score">
              <span className="landing-dot landing-dot-mid" />
              <span>{t("how.score2")}</span>
            </div>
            <h3>{t("how.card2.title")}</h3>
            <p>{t("how.card2.body")}</p>
            <div className="landing-state-bar"><i style={{ width: "58%", background: "var(--accent)" }} /></div>
          </div>
          <div className="landing-state-card">
            <div className="landing-state-score">
              <span className="landing-dot landing-dot-high" />
              <span>{t("how.score3")}</span>
            </div>
            <h3>{t("how.card3.title")}</h3>
            <p>{t("how.card3.body")}</p>
            <div className="landing-state-bar"><i style={{ width: "91%", background: "var(--primary)" }} /></div>
          </div>
        </div>
      </section>

      {/* ── Moments ──────────────────────────────────────────── */}
      <section id="moments" className="landing-section">
        <div className="landing-section-head">
          <div className="landing-section-eyebrow">{t("moments.eyebrow")}</div>
          <h2>{t("moments.title")}</h2>
          <p>{t("moments.sub")}</p>
        </div>
        <div className="landing-moment-grid">
          {[
            {
              title: t("moments.card1.title"), body: t("moments.card1.body"),
              svg: (
                <svg viewBox="0 0 200 160"><rect width="200" height="160" rx="14" fill="var(--muted)" />
                  <circle cx="100" cy="62" r="26" fill="var(--primary)" opacity="0.9" />
                  <path d="M70 110q30-22 60 0" stroke="currentColor" strokeWidth="3" fill="none" strokeLinecap="round" />
                  <circle cx="89" cy="58" r="3.5" fill="var(--primary-foreground)" />
                  <circle cx="111" cy="58" r="3.5" fill="var(--primary-foreground)" />
                  <rect x="40" y="124" width="120" height="6" rx="3" fill="currentColor" opacity="0.15" />
                </svg>
              )
            },
            {
              title: t("moments.card2.title"), body: t("moments.card2.body"),
              svg: (
                <svg viewBox="0 0 200 160"><rect width="200" height="160" rx="14" fill="var(--muted)" />
                  <rect x="46" y="40" width="108" height="80" rx="8" fill="var(--card)" stroke="currentColor" strokeWidth="2" />
                  <rect x="58" y="56" width="60" height="8" rx="4" fill="var(--accent)" />
                  <rect x="58" y="74" width="84" height="6" rx="3" fill="currentColor" opacity="0.25" />
                  <rect x="58" y="88" width="70" height="6" rx="3" fill="currentColor" opacity="0.25" />
                  <rect x="58" y="102" width="50" height="6" rx="3" fill="currentColor" opacity="0.25" />
                </svg>
              )
            },
            {
              title: t("moments.card3.title"), body: t("moments.card3.body"),
              svg: (
                <svg viewBox="0 0 200 160"><rect width="200" height="160" rx="14" fill="var(--muted)" />
                  <circle cx="100" cy="80" r="34" fill="none" stroke="var(--primary)" strokeWidth="3" />
                  <path d="M86 80l10 10 20-22" stroke="var(--primary)" strokeWidth="4" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )
            },
            {
              title: t("moments.card4.title"), body: t("moments.card4.body"),
              svg: (
                <svg viewBox="0 0 200 160"><rect width="200" height="160" rx="14" fill="var(--muted)" />
                  <rect x="92" y="46" width="16" height="46" rx="8" fill="var(--primary)" />
                  <path d="M76 78a24 24 0 0 0 48 0" stroke="currentColor" strokeWidth="3" fill="none" strokeLinecap="round" />
                  <line x1="100" y1="102" x2="100" y2="114" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                  <line x1="84" y1="114" x2="116" y2="114" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                </svg>
              )
            },
          ].map((card, i) => (
            <div key={i} className="landing-moment-card">
              <div className="landing-moment-art">{card.svg}</div>
              <h4>{card.title}</h4>
              <p>{card.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Arabic band ───────────────────────────────────────── */}
      <div className="landing-arabic-band">
        <span className="arabic">الاسم <b>ميزان</b> مش صدفة — التطبيق بيوزن طاقتك الذهنية كل يوم، وبيرتب مهامك على وزنها</span>
        <p className="translation">"Wizan" means balance — the app weighs your mental energy every morning and arranges your tasks accordingly.</p>
      </div>

      {/* ── Mini quiz ─────────────────────────────────────────── */}
      <section id="quiz" className="landing-section">
        <div className="landing-section-head">
          <div className="landing-section-eyebrow">{t("quiz.eyebrow")}</div>
          <h2>{t("quiz.title")}</h2>
          <p>{t("quiz.sub")}</p>
        </div>
        <div className="landing-quiz-grid">
          <div className="landing-quiz-panel">
            {quizStep !== "done" ? (
              <>
                <p className="landing-quiz-q">{t(quizQuestions[quizStep - 1].key)}</p>
                <div className="landing-quiz-opts">
                  {quizQuestions[quizStep - 1].opts.map((optKey, i) => (
                    <button
                      key={optKey}
                      className="landing-quiz-opt"
                      onClick={() => answerQuiz(quizQuestions[quizStep - 1].pts[i])}
                    >
                      {t(optKey)}
                    </button>
                  ))}
                </div>
              </>
            ) : (
              <div>
                <p className="landing-quiz-q">
                  {t("quiz.resultLabelPrefix")}<b>{quizResultScore}</b>{t("quiz.resultLabelSuffix")}
                </p>
                <p className="landing-quiz-verdict">{t(verdictKey)}</p>
                <button className="landing-btn-primary mt-5" onClick={retakeQuiz}>
                  {t("quiz.retake")}
                </button>
              </div>
            )}
            <div className="landing-quiz-progress">
              <i style={{ width: `${(quizAnswered / totalSteps) * 100}%` }} />
            </div>
          </div>

          <div className="landing-quiz-visual">
            <svg viewBox="0 0 240 240">
              <circle cx="120" cy="120" r="108" fill="var(--muted)" />
              <circle cx="92" cy="108" r="6" fill="currentColor" />
              <circle cx="148" cy="108" r={faceEyeR(quizPts)} fill="currentColor" />
              <path d={faceMouthPath(quizPts)} stroke="currentColor" strokeWidth="4" fill="none" strokeLinecap="round" />
            </svg>
            <p className="landing-quiz-visual-label">{t("quiz.visualLabel")}</p>
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────────── */}
      <section className="px-6 md:px-12">
        <div className="landing-cta">
          <h2 dangerouslySetInnerHTML={{ __html: t("cta.title") }} />
          <p>{t("cta.sub")}</p>
          <Link className="landing-btn-primary" to={isAuthed ? "/quiz" : "/register"}>
            {t("cta.button")}
          </Link>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────── */}
      <footer className="landing-footer">
        <div className="flex items-center gap-2 font-bold text-foreground">
          <Brain size={18} className="text-primary" />
          {t("footer.logo")}
        </div>
        <div className="meta">{t("footer.meta")}</div>
      </footer>

    </div>
  )
}