import { useState, useRef } from "react"

export default function VoicePlanControls({ text }) {
  const [speaking, setSpeaking] = useState(false)
  const utteranceRef = useRef(null)

  const speak = () => {
    if (!text) return

    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)

    utterance.lang = "en-US"
    utterance.rate = 1
    utterance.pitch = 1

    utterance.onend = () => setSpeaking(false)

    utteranceRef.current = utterance
    window.speechSynthesis.speak(utterance)

    setSpeaking(true)
  }

  const stop = () => {
    window.speechSynthesis.cancel()
    setSpeaking(false)
  }

  return (
    <div className="flex gap-2 mb-4">
      <button
        onClick={speak}
        className="px-4 py-2 rounded-lg bg-primary text-white text-sm"
      >
        ▶ Play Plan
      </button>

      <button
        onClick={stop}
        className="px-4 py-2 rounded-lg bg-red-500 text-white text-sm"
      >
        ⏹ Stop
      </button>
    </div>
  )
}