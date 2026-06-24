import { useState, useRef } from "react"
import { useTranslation } from "react-i18next"
import api from "../api/axios"
import { Button } from "./ui/button"

export default function VoiceRecorder({ priority, deadline, onTaskAdded }) {
  const { t } = useTranslation()
  const [recording, setRecording]   = useState(false)
  const [processing, setProcessing] = useState(false)

  const mediaRecorderRef = useRef(null)
  const streamRef        = useRef(null)
  const chunksRef        = useRef([])

  const today = new Date().toISOString().split("T")[0]

  const toggleMic = async () => {
    // stop
    if (recording) {
      mediaRecorderRef.current?.stop()
      streamRef.current?.getTracks().forEach((t) => t.stop())
      setRecording(false)
      return
    }

    if (deadline && deadline < today) {
      onTaskAdded(null, t("tasks.deadline_past"))
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      chunksRef.current = []

      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (e) => {
        if (e.data?.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        setProcessing(true)
        try {
          const formData = new FormData()
          formData.append("audio", new Blob(chunksRef.current, { type: "audio/webm" }), "voice.webm")
          if (priority) formData.append("priority", priority)
          if (deadline) formData.append("deadline", deadline)

          const res = await api.post("/add-task-by-voice/", formData)
          if (res.data?.success) onTaskAdded(res.data.task, null)
        } catch {
          onTaskAdded(null, t("tasks.error_add"))
        } finally {
          setProcessing(false)
        }
      }

      mediaRecorder.start()
      setRecording(true)
    } catch {
      onTaskAdded(null, t("tasks.mic_error"))
    }
  }

  return (
    <Button
      className={`text-lg transition-all cursor-pointer bg-card border-border hover:border-destructive hover:bg-destructive/10 text-foreground hover:text-destructive disabled:opacity-50 disabled:cursor-not-allowed ${recording ? " border-destructive bg-destructive/10 text-destructive animate-pulse" : ""}`}
      onClick={toggleMic}
      disabled={processing}
      title={t("tasks.mic")}
    >
      {processing ? "⏳" : recording ? "⏹" : "🎤"}
    </Button>
  )
}