import { useState, useRef } from "react"
import api from "../api/axios"
import { getVoicePlan } from "../api/voice"

export default function VoiceRecorder({ onPlanReceived }) {
  const [recording, setRecording] = useState(false)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    const mediaRecorder = new MediaRecorder(stream)
    mediaRecorderRef.current = mediaRecorder
    chunksRef.current = []

    mediaRecorder.ondataavailable = (e) => {
      chunksRef.current.push(e.data)
    }

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" })

      const formData = new FormData()
      formData.append("audio", audioBlob, "voice.webm")

      // 1️⃣ STT API
      const sttRes = await api.post("/voice/transcribe/", formData)
      const text = sttRes.data.transcript

      // 2️⃣ Voice Plan API
      const planRes = await getVoicePlan(text)

      // 3️⃣ رجّع الداتا للـ Dashboard
      onPlanReceived(planRes.plan)
    }

    mediaRecorder.start()
    setRecording(true)
  }

  const stopRecording = () => {
    mediaRecorderRef.current.stop()
    setRecording(false)
  }

  return (
    <div className="flex gap-2 mb-4">
      {!recording ? (
        <button
          onClick={startRecording}
          className="px-4 py-2 bg-green-600 text-white rounded-lg"
        >
          🎤 Start Recording
        </button>
      ) : (
        <button
          onClick={stopRecording}
          className="px-4 py-2 bg-red-600 text-white rounded-lg"
        >
          ⏹ Stop
        </button>
      )}
    </div>
  )
}