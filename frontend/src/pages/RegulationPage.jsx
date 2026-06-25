import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"
import api from "../api/axios"
import { Button } from "../components/ui/button"
import { Alert, AlertDescription } from "../components/ui/alert"
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "../components/ui/alert-dialog"
import "./Regulation.css"

const PRIORITY_STYLES = {
  low: "bg-emerald-100 text-emerald-700",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-red-100 text-red-600",
}

export default function RegulationPage() {
  const { t, i18n } = useTranslation()
  const isAr = i18n.language === "ar"
  const navigate = useNavigate()
  const { state } = useLocation()

  const [allowed, setAllowed] = useState(state?.allowed_tasks ?? [])
  const [postponed, setPostponed] = useState(state?.postponed_tasks ?? [])
  const [error, setError] = useState(null)
  const [overridingId, setOverridingId] = useState(null)

  const [stepsMap, setStepsMap] = useState({})

  if (!state) return (
    <div className="reg-root" dir={isAr ? "rtl" : "ltr"}>
      <div className="reg-wrap flex flex-col justify-center items-center">
        <Alert variant="destructive"><AlertDescription>{t("common.error")}</AlertDescription></Alert>
        <Button className="mt-4 w-fit" onClick={() => navigate("/tasks")}>
          {isAr ? "→" : "←"} {t("tasks.title")}
        </Button>
      </div>
    </div>
  )

  //  steps 
  const toggleSteps = async (taskId) => {
    const current = stepsMap[taskId]

    // already fetched — just toggle expanded
    if (current && current !== "loading") {
      setStepsMap((prev) => ({
        ...prev,
        [taskId]: { ...current, expanded: !current.expanded },
      }))
      return
    }

    // already loading — do nothing
    if (current === "loading") return

    // fetch
    setStepsMap((prev) => ({ ...prev, [taskId]: "loading" }))
    try {
      const res = await api.post(`/tasks/${taskId}/decompose/`)
      setStepsMap((prev) => ({
        ...prev,
        [taskId]: { expanded: true, steps: res.data.steps },
      }))
    } catch {
      setError(t("regulation.decompose_error"))
      setStepsMap((prev) => { const s = { ...prev }; delete s[taskId]; return s })
    }
  }

  const isExpanded = (taskId) =>
    stepsMap[taskId] && stepsMap[taskId] !== "loading" && stepsMap[taskId].expanded

  // override 
  const confirmOverride = async () => {
    try {
      await api.post("/tasks/override/", { task_id: overridingId, reason: "User decided to proceed" })
      const task = postponed.find((t) => t.id === overridingId)
      setPostponed((prev) => prev.filter((t) => t.id !== overridingId))
      setAllowed((prev) => [...prev, { ...task, status: "overridden" }])
      setOverridingId(null)
    } catch (err) {
      setError(err.response?.data?.error || t("common.error"))
      setOverridingId(null)
    }
  }

  return (
    <div className="reg-root" dir={isAr ? "rtl" : "ltr"}>
      <div className="reg-wrap">

        <Button variant="ghost" className="mb-6" onClick={() => navigate("/tasks")}>
          {isAr ? "→" : "←"} {t("tasks.title")}
        </Button>

        <h1 className="reg-title">{t("regulation.title")}</h1>

        {error && (
          <Alert variant="destructive" className="my-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {state.reply && (
          <div className="reg-reply">{state.reply}</div>
        )}

        {/*  allowed  */}
        <div className="reg-divider mb-3">
          <span>✅ {t("regulation.allowed")}</span>
        </div>

        {allowed.length === 0 && (
          <p className="text-sm text-muted-foreground mb-4">{t("tasks.no_tasks")}</p>
        )}

        {allowed.map((task) => (
          <div key={task.id} className="reg-card">
            <div className="reg-card-top">
              <span className="reg-card-title">{task.name}</span>
              <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${PRIORITY_STYLES[task.priority]}`}>
                {t(`tasks.priority.${task.priority}`)}
              </span>
              <Button size="sm" variant="secondary" onClick={() => toggleSteps(task.id)}>
                {stepsMap[task.id] === "loading"
                  ? t("common.loading")
                  : isExpanded(task.id)
                    ? t("regulation.steps_hide")
                    : t("regulation.steps_btn")}
              </Button>
            </div>

            {task.deadline && <div className="reg-deadline">📅 {task.deadline}</div>}
            {task.reason && <p className="reg-reason">💡 {task.reason}</p>}

            {isExpanded(task.id) && (
              <div className="reg-steps">
                {stepsMap[task.id].steps.map((step, i) => (
                  <div key={i} className="reg-step cursor-pointer select-none"
                    onClick={() => setStepsMap((prev) => {
                      const steps = prev[task.id].steps.map((s, j) =>
                        j === i ? { ...s, is_completed: !s.is_completed } : s
                      )
                      return { ...prev, [task.id]: { ...prev[task.id], steps } }
                    })}>
                    <span className={`reg-dot ${step.is_completed ? "done" : ""}`} />
                    <span className={step.is_completed ? "line-through opacity-50" : ""}>
                      {step.description ?? step.name ?? step}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {/*  postponed  */}
        {postponed.length > 0 && (
          <>
            <div className="reg-divider mt-6 mb-3">
              <span>⏳ {t("regulation.postponed")}</span>
            </div>

            {postponed.map((task) => (
              <div key={task.id} className="reg-card postponed">
                <div className="reg-card-top">
                  <span className="reg-card-title">{task.name}</span>
                  <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${PRIORITY_STYLES[task.priority]}`}>
                    {t(`tasks.priority.${task.priority}`)}
                  </span>
                  <Button size="sm" variant="destructive" onClick={() => setOverridingId(task.id)}>
                    {t("regulation.override")}
                  </Button>
                </div>
                {task.deadline && <div className="reg-deadline">📅 {task.deadline}</div>}
                {task.reason && <p className="reg-reason">⚠️ {task.reason}</p>}
              </div>
            ))}
          </>
        )}

        {postponed.length === 0 && (
          <p className="text-sm text-muted-foreground mt-2">{t("regulation.no_postponed")}</p>
        )}

      </div>

      <AlertDialog open={!!overridingId} onOpenChange={(open) => !open && setOverridingId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t("regulation.override_confirm_title")}</AlertDialogTitle>
            <p className="text-sm text-muted-foreground mt-1">{t("regulation.override_confirm_desc")}</p>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t("tasks.cancel")}</AlertDialogCancel>
            <AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={confirmOverride}>
              {t("regulation.override")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

    </div>
  )
}