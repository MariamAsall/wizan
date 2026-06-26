import { useEffect } from "react"
import toast from "react-hot-toast"

export default function useNotifications() {
  useEffect(() => {
    const token = localStorage.getItem("access_token")

    const socket = new WebSocket(
      `ws://127.0.0.1:8000/ws/notifications/?token=${token}`
    )

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)

      toast.success(`${data.title}: ${data.message}`)
    }

    socket.onclose = () => {
      console.log("WebSocket closed")
    }

    return () => socket.close()
  }, [])
}