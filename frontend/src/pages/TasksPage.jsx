import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"
import api from "../api/axios"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Alert, AlertDescription } from "../components/ui/alert"
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../components/ui/dialog"
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
}
  from "../components/ui/alert-dialog"
import "./Tasks.css"
import { AlertCircleIcon, Edit, Trash2 } from "lucide-react"
import VoiceRecorder from "../components/VoiceRecorder"

import { notify } from "../components/notifications"


const STATUS_STYLES = {
  allowed: "bg-emerald-100 text-emerald-700",
  pending: "bg-yellow-100 text-yellow-700",
  postponed: "bg-red-100 text-red-600",
  overridden: "bg-amber-100 text-amber-700",
}
const PRIORITY_STYLES = {
  low: "bg-emerald-100 text-emerald-700",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-red-100 text-red-600",
}

export default function TasksPage() {
  const { t, i18n } = useTranslation()
  const isAr = i18n.language === "ar"
  const navigate = useNavigate()

  const today = new Date().toISOString().split("T")[0]

  const [tasks, setTasks] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const [input, setInput] = useState("")
  const [priority, setPriority] = useState("")
  const [deadline, setDeadline] = useState("")

  const [editingTask, setEditingTask] = useState(null)
  const [editName, setEditName] = useState("")
  const [editPriority, setEditPriority] = useState("")
  const [editDeadline, setEditDeadline] = useState("")

  const [deletingId, setDeletingId] = useState(null)
  const [regulating, setRegulating] = useState(false)

  useEffect(() => { fetchTasks() }, [])

  const fetchTasks = async () => {
    setLoading(true)
    try {
      const res = await api.get("/tasks/")
      setTasks(res.data)
      setLoading(false)
    } catch {
      setError(t("tasks.error_load"))
      setLoading(false)                         
    }
  }

  const addTask = async () => {
    if (!input.trim()) {
      setError(t("tasks.error_empty"))
      return
    }
    if (deadline && deadline < today) {
      setError(t("tasks.deadline_past"))
      return
    }
    try {
      const res = await api.post("/tasks/", {
        name: input.trim(),
        priority: priority || "medium",
        deadline: deadline || null,
      })
      notify.success("task_create", {task: input.trim()})

      setTasks((prev) => [...prev, res.data])
      setInput("")
      setPriority("")
      setDeadline("")
      setError(null)
    } catch {
      notify.error("task_create")
      setError(t("tasks.error_add"))
    }
  }

  const confirmDelete = async () => {
    try {
      await api.delete(`/tasks/${deletingId}/`)
      setTasks((prev) => prev.filter((t) => t.id !== deletingId))
      setDeletingId(null)
      notify.success("task_delete")
      
    } catch {
      notify.error("task_delete")
      setError(t("common.error"))
    }
  }

  const updateTask = async () => {
    if (editDeadline && editDeadline < today) {
      setError(t("tasks.deadline_past"))
      return
    }
    try {
      await api.patch(`/tasks/${editingTask}/`, {
        name: editName,
        priority: editPriority || "medium",
        deadline: editDeadline || null,
      })
      notify.success("task_update")
      setEditingTask(null)
      setError(null)
      fetchTasks()
    } catch {
      notify.error("task_update")
      setError(t("common.error"))
    }
  }

const regulate = async () => {
  setRegulating(true)
  try {
    const [regulateRes, tasksRes] = await Promise.all([
      api.post("/tasks/regulate/"),
      api.get("/tasks/")
    ])
    console.log(regulateRes.data)
    console.log(tasksRes.data)

    navigate("/regulation", {
      state: {
        reply: regulateRes.data.reply,
        allowed_tasks: [...regulateRes.data.allowed_tasks, ...tasksRes.data.filter((t) => t.status === "overridden")],
        postponed_tasks: tasksRes.data.filter((t) => t.status === "postponed"),
      }
    })
  } catch {
    setError(t("common.error"))
  } finally {
    setRegulating(false)
  }
}

if (loading) return (
  <div className="tasks-loading">
    <div className="tasks-spinner" />
    <p>{t("tasks.loading")}</p>
  </div>
)

  return (
    <div className="tasks-root" dir={isAr ? "rtl" : "ltr"}>
      <div className="tasks-wrap">

        <div className="mb-7">
          <h1 className="tasks-title">{t("tasks.title")}</h1>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-5">
            <AlertCircleIcon />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* add bar */}
        <div className="add-task-bar flex-wrap">
          <Input
            className="add-task-input"
            placeholder={t("tasks.add_placeholder")}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addTask()}
          />

          <Select value={priority} onValueChange={setPriority}>
            <SelectTrigger className="w-[140px] rounded-[10px] border-[1.5px] text-sm">
              <SelectValue placeholder={t("tasks.priority.select")}/>
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
              <SelectItem value="low">{t("tasks.priority.low")}</SelectItem>
              <SelectItem value="medium">{t("tasks.priority.medium")}</SelectItem>
              <SelectItem value="high">{t("tasks.priority.high")}</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>

          <Input
            type="date"
            className="w-[130px] rounded-[10px] border-[1.5px] text-sm"
            value={deadline}
            min={today}
            onChange={(e) => setDeadline(e.target.value)}
          />

           <VoiceRecorder
            priority={priority}
            deadline={deadline}
            onTaskAdded={(task, err) => {
              if (err) { setError(err); return }
              setTasks((prev) => [task, ...prev])
              setDeadline("")
            }}
          />

          <Button className="btn-add-task" onClick={addTask}>
            {t("tasks.add_button")}
          </Button>

        </div>
          

        {/* flat task list */}
        <div className="task-section-divider mb-3">
          <span>{t("tasks.all_tasks")}</span>
        </div>

        {tasks.length === 0 && (
          <p className="text-muted-foreground mb-4">{t("tasks.no_tasks")}</p>
        )}

        {tasks.map((task) => (
          <div key={task.id} className="task-card">
            <div className="task-card-top">
              <span className="task-card-title">{task.name}</span>

              {/* status badge */}
              <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${STATUS_STYLES[task.status] ?? ""}`}>
                {t(`tasks.status.${task.status}`)}
              </span>

              {/* priority badge */}
              <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${PRIORITY_STYLES[task.priority]}`}>
  {t(`tasks.priority.${task.priority}`)}
</span>

              <div className="flex">
                <Button
                  size="sm" variant="ghost"
                  className="px-2.5 text-xs text-muted-foreground hover:text-foreground"
                  onClick={() => {
                    setEditingTask(task.id)
                    setEditName(task.name)
                    setEditPriority(task.priority)
                    setEditDeadline(task.deadline || "")
                    setError(null)
                  }}
                >
                  <Edit />
                </Button>

                <Button
                  size="sm" variant="ghost"
                  className="px-2.5 text-xs text-destructive hover:text-destructive hover:bg-destructive/10"
                  onClick={() => setDeletingId(task.id)}
                >
                  <Trash2 />
                </Button>
              </div>
            </div>

            {task.deadline && (
  <div className={`task-deadline ${task.deadline < today ? "task-deadline--overdue" : ""}`}>
    {task.deadline < today ? "⚠️" : "📅"} {task.deadline}
    {task.deadline < today && (
      <span className="task-overdue-badge">{t("tasks.overdue")}</span>
    )}
  </div>
)}
          </div>
        ))}

        {
          tasks.length !== 0 && <div className="w-full flex justify-center items-center mt-6">
          <Button className="btn-regulate" onClick={regulate} disabled={regulating}>
            {regulating ? t("common.loading") : t("tasks.plan_day")}
        </Button>
        </div>
        }

      </div>

      {/* edit modal */}
      <Dialog open={!!editingTask} onOpenChange={(open) => !open && setEditingTask(null)}>
        <DialogContent className="max-w-[420px] rounded-2xl">
          <DialogHeader>
            <DialogTitle>{t("tasks.edit_title")}</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-3 mt-2">
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              placeholder={t("tasks.add_placeholder")}
            />
            <Select value={editPriority} onValueChange={setEditPriority}>
              <SelectTrigger className="rounded-[10px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">{t("tasks.priority.low")}</SelectItem>
                <SelectItem value="medium">{t("tasks.priority.medium")}</SelectItem>
                <SelectItem value="high">{t("tasks.priority.high")}</SelectItem>
              </SelectContent>
            </Select>
            <Input
              type="date"
              value={editDeadline}
              min={today}
              onChange={(e) => setEditDeadline(e.target.value)}
            />
            <div className="flex gap-2.5 mt-1">
              <Button className="flex-1" onClick={updateTask}>{t("tasks.save")}</Button>
              <Button className="flex-1" variant="secondary" onClick={() => setEditingTask(null)}>
                {t("tasks.cancel")}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* delete confirm */}
      <AlertDialog open={!!deletingId} onOpenChange={(open) => !open && setDeletingId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t("tasks.delete_confirm")}</AlertDialogTitle>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t("tasks.cancel")}</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-white hover:bg-destructive/90"
              onClick={confirmDelete}
            >
              {t("tasks.delete")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

    </div>
  )
}