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
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  async function fetchNotifications() {
    try {
      setLoading(true)
      const [listRes, countRes] = await Promise.all([
        api.get("/notifications/"),
        api.get("/notifications/count/")
      ])
      setNotifications(listRes.data || [])
      setCount(countRes.data.unread_count || countRes.data.count || 0)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // 1. الدالة الجديدة لعمل Mark Read لإشعار واحد فقط 🎯
  async function markAsRead(id, isRead) {
    // إذا كان الإشعار مقروءاً بالفعل، لا تفعل شيئاً
    if (isRead) return;

    try {
      // استدعاء الـ endpoint الخاص بك
      await api.post(`/notifications/${id}/read/`)

      // تحديث الحالة في الـ UI فوراً ليصبح مقروءاً
      setNotifications(prev =>
        prev.map(n => (n.id === id ? { ...n, is_read: true } : n))
      )

      // تقليل عداد الإشعارات غير المقروءة بمقدار 1
      setCount(prev => Math.max(0, prev - 1))
    } catch (err) {
      console.error("Failed to mark notification as read:", err)
    }
  }

  async function markAllRead() {
    try {
      await api.post("/notifications/read-all/")
      setNotifications(prev =>
        prev.map(notification => ({ ...notification, is_read: true }))
      )
      setCount(0)
    } catch (err) {
      console.error(err)
    }
  }

  async function deleteNotification(id, isRead) {
    try {
      await api.delete(`/notifications/delete/${id}/`)
      setNotifications(prev => prev.filter(n => n.id !== id))
      if (!isRead) {
        setCount(prev => Math.max(0, prev - 1))
      }
    } catch (err) {
      console.error("Failed to delete notification:", err)
    }
  }

  function getIcon(type) {
    switch (type) {
      case "success": return "✅"
      case "warning": return "⚠️"
      case "ai": return "🧠"
      default: return "ℹ️"
    }
  }

  return (
    <div className="notif-wrapper" ref={dropdownRef}>
      <button className="notif-btn" onClick={() => setOpen(!open)} aria-label="Notifications">
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
            <h4>Notifications ({notifications.length})</h4>
            {count > 0 && (
              <button className="notif-read-btn" onClick={markAllRead}>
                Mark all read
              </button>
            )}
          </div>

          <div className="notif-body-scroll">
            {loading ? (
              <div className="notif-empty">Loading...</div>
            ) : notifications.length === 0 ? (
              <div className="notif-empty">No notifications yet</div>
            ) : (
              notifications.map(notification => (
                <div
                  key={notification.id}
                  className={`notif-item ${!notification.is_read ? "unread" : ""}`}
                  /* 2. إضافة حدث الضغط على الإشعار لقراءته هنا */
                  onClick={() => markAsRead(notification.id, notification.is_read)}
                  style={{ cursor: !notification.is_read ? "pointer" : "default" }}
                >
                  <div className="notif-item-main">
                    <div className="notif-item-top">
                      <span className="notif-icon">
                        {getIcon(notification.notification_type)}
                      </span>
                      <strong>{notification.title}</strong>
                    </div>
                    <p className="notif-message">{notification.message}</p>
                    <small className="notif-date">
                      {new Date(notification.created_at).toLocaleString()}
                    </small>
                  </div>
                  
                  <button 
                    className="notif-delete-btn"
                    /* 3. استخدام e.stopPropagation() لمنع تداخل حدث الحذف مع حدث القراءة */
                    onClick={(e) => {
                      e.stopPropagation(); 
                      deleteNotification(notification.id, notification.is_read);
                    }}
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}