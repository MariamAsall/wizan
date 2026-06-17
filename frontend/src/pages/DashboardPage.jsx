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

  // قائمة المهام الأولية (قمنا بتحديث الحقول لتطابق الـ Model الحقيقي)
  const [tasks, setTasks] = useState([
    { id: 1, name: "Morning quiz", priority: "low", status: "allowed" },
    { id: 2, name: "Review lecture notes for Chapter 4", priority: "medium", status: "pending" },
    { id: 3, name: "Submit database assignment", priority: "high", status: "pending" },
  ])

  const [voiceStatus, setVoiceStatus] = useState("Use voice to instantly add a new task")

  // دالة عمل toggle للحالة بناءً على الـ status الخاص بموديلك
  const toggle = (id) =>
    setTasks((prev) =>
      prev.map((t) => 
        t.id === id 
          ? { ...t, status: t.status === "allowed" ? "pending" : "allowed" } 
          : t
      )
    )

  // 🔥 استقبال المهمة الحقيقية المفرغة من الـ DB وحقنها في الـ State فوراً
  const handleNewVoiceTask = (taskFromServer) => {
    // إضافة المهمة الحقيقية بكامل الـ Keys الخاصة بها في أعلى القائمة
    setTasks((prevTasks) => [taskFromServer, ...prevTasks])
    
    // تحديث رسالة النجاح بالنص المفرغ المأخوذ من حقل name الحقيقي
    setVoiceStatus(`✅ Added successfully: "${taskFromServer.name}"`)
  }

  return (
    <div className="dash-root">
      <div className="dash-wrap">
        
        {/* ... الكود العلوي (Greeting, Chart, Stats) يبقى كما هو ... */}

        {/* 🧠 SECTION VOICE ASSISTANT */}
        <div className="today-plan mb-6">
          <div className="section-head">
            <h2 className="section-title">Add Task by Voice</h2>
            <span className="badge-green">AUDIO</span>
          </div>

          {/* ربط الـ Recorder بدالة الاستقبال والحقن الجديدة */}
          <VoiceRecorder onPlanReceived={handleNewVoiceTask} />

          {/* صندوق يعرض حالة المعالجة أو نجاح العملية للمستخدم */}
          <div className="mt-2 p-3 bg-gray-50 border border-gray-100 rounded-lg text-xs text-gray-500">
            {voiceStatus}
          </div>
        </div>

        {/* قائمة المهام (Today's plan) - محدثة لتطابق حقول الـ Model الحقيقي */}
        <div className="today-plan">
          <div className="section-head">
            <h2 className="section-title">Today's plan</h2>
            <span className="badge-green">{tasks.length} tasks</span>
          </div>

          {tasks.map((task) => {
            const isDone = task.status === "allowed"; // افترضنا هنا أن الـ allowed يعني تمت الموافقة/الإنجاز
            
            return (
              <div key={task.id} className="task-row">
                <button
                  className={`task-checkbox ${isDone ? "done" : ""}`}
                  onClick={() => toggle(task.id)}
                >
                  {isDone && (
                    <span className="text-white text-xs font-bold">✓</span>
                  )}
                </button>

                {/* تدوير البيانات بناءً على حقل name الحقيقي في قاعدة البيانات */}
                <span className={`task-text ${isDone ? "done" : ""}`}>
                  {task.name}
                </span>

                {/* تدوير البيانات بناءً على حقل priority الحقيقي في قاعدة البيانات */}
                <span className={`cost-${task.priority}`}>
                  {{ low: "Low", medium: "Medium", high: "High" }[task.priority]}
                </span>
              </div>
            )
          })}
        </div>

        {/* CTA */}
        <div className="dash-cta">
          <button className="btn-dash-cta" onClick={() => navigate("/tasks")}>
            View full task board →
          </button>
        </div>

      </div>
    </div>
  )
}