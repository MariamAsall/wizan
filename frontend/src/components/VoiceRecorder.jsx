import { useState, useRef } from "react"
import api from "../api/axios"

export default function VoiceRecorder({ onPlanReceived, currentPriority, currentDeadline }) {
  const [recording, setRecording] = useState(false)
  const [loading, setLoading] = useState(false) 
  
  const mediaRecorderRef = useRef(null)
  const streamRef = useRef(null)
  const chunksRef = useRef([])

  const startRecording = async () => {
    // 🔍 🔥 التحقق من التاريخ: منع المواعيد القديمة
    if (currentDeadline) {
      const selectedDate = new Date(currentDeadline);
      const today = new Date();
      
      // تصغير التاريخين لمقارنة الأيام فقط دون الساعات والدقائق
      selectedDate.setHours(0, 0, 0, 0);
      today.setHours(0, 0, 0, 0);

      if (selectedDate < today) {
        alert("❌ لا يمكن اختيار تاريخ قديم للمهمة! يرجى تحديد تاريخ اليوم أو تاريخ مستقبلي.");
        return; // إيقاف الدالة وعدم فتح المايكروفون
      }
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = async () => {
        setLoading(true)
        try {
          const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" })
          const formData = new FormData()
          
          formData.append("audio", audioBlob, "voice.webm")

          if (currentPriority) {
            formData.append("priority", currentPriority)
          }
          if (currentDeadline) {
            formData.append("deadline", currentDeadline)
          }

          const res = await api.post("/add-task-by-voice/", formData)
          
          if (res.data && res.data.success) {
            onPlanReceived(res.data.task) 
          }
        } catch (error) {
          console.error("Voice Task Error:", error)
          alert("حدث خطأ أثناء إضافة المهمة بالصوت.")
        } finally {
          setLoading(false)
        }
      }

      mediaRecorder.start()
      setRecording(true)
    } catch (err) {
      console.error("Failed to start recording:", err)
      alert("يرجى السماح بالوصول إلى المايكروفون.")
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop()
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
      setRecording(false)
    }
  }

  return (
    <div className="flex gap-2 mb-4 items-center">
      {!recording ? (
        <button
          onClick={startRecording}
          disabled={loading}
          className={`px-4 py-2 text-white rounded-lg transition ${
            loading ? "bg-gray-400 cursor-not-allowed" : "bg-green-600 hover:bg-green-700"
          }`}
        >
          {loading ? "⏳ Processing..." : "🎤 Start Recording"}
        </button>
      ) : (
        <button
          onClick={stopRecording}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg animate-pulse"
        >
          ⏹ Stop Recording
        </button>
      )}
    </div>
  )
}