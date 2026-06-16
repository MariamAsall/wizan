import api from "./axios"

export const getVoicePlan = async (transcribedText) => {
  const res = await api.post("/voice/plan/", {
    transcribed_text: transcribedText,
  })

  return res.data
}