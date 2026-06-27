// import { useEffect, useRef } from "react"
// import toast from "react-hot-toast"

// export default function useNotifications() {
//   const socketRef = useRef(null)
//   const isComponentMounted = useRef(true)

//   useEffect(() => {
//     isComponentMounted.current = true
//     const token = localStorage.getItem("access_token")
    
//     if (!token) return

//     const connectWebSocket = () => {
//       if (socketRef.current && (socketRef.current.readyState === WebSocket.OPEN || socketRef.current.readyState === WebSocket.CONNECTING)) {
//         return
//       }

//       const wsUrl = `ws://127.0.0.1:8000/ws/notifications/?token=${token}`
//       const socket = new WebSocket(wsUrl)
//       socketRef.current = socket

//       socket.onmessage = (event) => {
//         try {
//           const data = JSON.parse(event.data)
//           const fullMessage = `${data.title}\n${data.message}`

//           switch (data.notification_type) {
//             case "success":
//               toast.success(fullMessage)
//               break
//             case "warning":
//               toast.error(fullMessage, { icon: "⚠️" })
//               break
//             case "ai":
//               toast.success(fullMessage, {
//                 icon: "🧠",
//                 style: { background: "#f0f4ff", color: "#1e3a8a", border: "1px solid #bfdbfe" },
//               })
//               break
//             default:
//               toast(fullMessage)
//           }
//         } catch (error) {
//           console.error("Error parsing WebSocket message:", error)
//         }
//       }

//       socket.onclose = (e) => {
//         console.log("WebSocket closed:", e.reason)
        
//         // ⚠️ الحماية هنا: لا تحاول إعادة الاتصال إذا غادر المستخدم الصفحة أو إذا قام الـ Unmount بإغلاقه
//         if (isComponentMounted.current) {
//           setTimeout(() => {
//             console.log("Attempting to reconnect WebSocket...")
//             connectWebSocket()
//           }, 5000)
//         }
//       }

//       socket.onerror = (err) => {
//         console.error("WebSocket error observed:", err)
//       }
//     }

//     connectWebSocket()

//     return () => {
//       // تعديل حالة الـ Mount لمنع الـ Reconnect المزدوج
//       isComponentMounted.current = false
//       if (socketRef.current) {
//         socketRef.current.close()
//       }
//     }
//   }, [])
// }