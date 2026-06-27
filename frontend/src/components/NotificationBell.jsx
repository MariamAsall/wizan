import { useEffect, useRef, useState } from "react"
import api from "../api/axios"
import "./NotificationBell.css"

export default function NotificationBell() {
const [notifications, setNotifications] = useState([])
const [count, setCount] = useState(0)
const [open, setOpen] = useState(false)
const [loading, setLoading] = useState(true)

const dropdownRef = useRef(null)

useEffect(() => {
fetchNotifications()
}, [])

useEffect(() => {
function handleClickOutside(event) {
if (
dropdownRef.current &&
!dropdownRef.current.contains(event.target)
) {
setOpen(false)
}
}


document.addEventListener(
  "mousedown",
  handleClickOutside
)

return () =>
  document.removeEventListener(
    "mousedown",
    handleClickOutside
)


}, [])

async function fetchNotifications() {
try {
setLoading(true)


  const [listRes, countRes] = await Promise.all([
    api.get("/notifications/"),
    api.get("/notifications/count/")
  ])

  setNotifications(listRes.data || [])
  setCount(
    countRes.data.unread_count ||
    countRes.data.count ||
    0
  )
} catch (err) {
  console.error(err)
} finally {
  setLoading(false)
}


}

async function markAllRead() {
try {
await api.post(
"/notifications/read-all/"
)


  setNotifications(prev =>
    prev.map(notification => ({
      ...notification,
      is_read: true
    }))
  )

  setCount(0)
} catch (err) {
  console.error(err)
}


}

function getIcon(type) {
switch (type) {
case "success":
return "✅"


  case "warning":
    return "⚠️"

  case "ai":
    return "🧠"

  default:
    return "ℹ️"
}


}

return ( <div
   className="notif-wrapper"
   ref={dropdownRef}
 >
<button
className="notif-btn"
onClick={() => setOpen(!open)}
>
🔔

    {count > 0 && (
      <span className="notif-badge">
        {count > 99 ? "99+" : count}
      </span>
    )}
  </button>

  {open && (
    <div className="notif-dropdown">

      <div className="notif-header">
        <h4>Notifications</h4>

        {count > 0 && (
          <button
            className="notif-read-btn"
            onClick={markAllRead}
          >
            Mark all read
          </button>
        )}
      </div>

      {loading ? (
        <div className="notif-empty">
          Loading...
        </div>
      ) : notifications.length === 0 ? (
        <div className="notif-empty">
          No notifications yet
        </div>
      ) : (
        notifications
          .slice(0, 10)
          .map(notification => (
            <div
              key={notification.id}
              className={`notif-item ${
                !notification.is_read
                  ? "unread"
                  : ""
              }`}
            >
              <div className="notif-item-top">
                <span className="notif-icon">
                  {getIcon(
                    notification.notification_type
                  )}
                </span>

                <strong>
                  {notification.title}
                </strong>
              </div>

              <p>
                {notification.message}
              </p>

              <small>
                {new Date(
                  notification.created_at
                ).toLocaleString()}
              </small>
            </div>
          ))
      )}
    </div>
  )}
</div>


)
}
