import { useEffect, useState } from "react"
import api from "../api/axios"
import "./profile.css"
import { notify } from "../components/notifications"
import { useTranslation } from "react-i18next"

export default function Profile() {
  
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const { t, i18n } = useTranslation()
  const isAr = i18n.language === "ar"

  const [editMode, setEditMode] = useState(false)
  const [showPasswordModal, setShowPasswordModal] = useState(false)

  const [saving, setSaving] = useState(false)
  const [changingPassword, setChangingPassword] = useState(false)

  const [form, setForm] = useState({
    username: "",
    first_name: "",
    last_name: "",
    phone_number: "",
    language: "en",
    date_of_birth: "",
    profile_picture: null,
  })

  const [passwordForm, setPasswordForm] = useState({
    old_password: "",
    new_password: "",
    confirm_password: "",
  })

  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    fetchProfile()
  }, [])

  async function fetchProfile() {
    try {
      const res = await api.get("/auth/profile/")
      setUser(res.data)

      setForm({
        username: res.data.username || "",
        first_name: res.data.first_name || "",
        last_name: res.data.last_name || "",
        phone_number: res.data.phone_number || "",
        language: res.data.language || "en",
        date_of_birth: res.data.date_of_birth || "",
        profile_picture: null,
      })
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  function handlePasswordChange(e) {
    setPasswordForm({ ...passwordForm, [e.target.name]: e.target.value })
  }

  // --- Validation للفورم الخاص بالملف الشخصي ---
  function validateProfileForm() {
    if (!form.username.trim()) {
      notify.error(isAr ? "اسم المستخدم مطلوب" : "Username is required")
      return false
    }
    if (!form.first_name.trim()) {
      notify.error(isAr ? "الاسم الأول مطلوب" : "First name is required")
      return false
    }
    if (!form.last_name.trim()) {
      notify.error(isAr ? "الاسم الأخير مطلوب" : "Last name is required")
      return false
    }
    if (!form.phone_number.trim()) {
      notify.error(isAr ? "رقم الهاتف مطلوب" : "Phone number is required")
      return false
    }
    if (!/^\d+$/.test(form.phone_number)) {
      notify.error(isAr ? "رقم الهاتف يجب أن يحتوي على أرقام فقط" : "Phone number must contain digits only")
      return false
    }

    // التعديل هنا: منع اختيار تاريخ ميلاد في المستقبل
    if (form.date_of_birth) {
      const selectedDate = new Date(form.date_of_birth)
      const today = new Date()
      
      // تصغير الوقت لتجنب الفروق الطفيفة في الأجزاء من الثانية أثناء المقارنة
      today.setHours(0, 0, 0, 0)
      selectedDate.setHours(0, 0, 0, 0)

      if (selectedDate > today) {
        notify.error(isAr ? "لا يمكن أن يكون تاريخ الميلاد في المستقبل" : "Date of birth cannot be in the future")
        return false
      }
    }

    return true
  }

  async function saveProfile(e) {
    e.preventDefault()

    if (!validateProfileForm()) return

    try {
      setSaving(true)

      const fd = new FormData()
      Object.keys(form).forEach((k) => {
        if (form[k]) fd.append(k, form[k])
      })

      await api.patch("/auth/profile/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      })

      await fetchProfile()
      notify.success(isAr ? "تم تحديث الملف الشخصي بنجاح" : "Profile updated successfully")
      setEditMode(false)
    } catch (err) {
      console.error(err)
      notify.error(isAr ? "فشل في حفظ البيانات" : "Failed to save profile")
    } finally {
      setSaving(false)
    }
  }

  // --- Validation لفورم تغيير كلمة المرور ---
  function validatePasswordForm() {
    if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.confirm_password) {
      notify.error(isAr ? "يرجى ملء جميع الحقول" : "Please fill in all fields")
      return false
    }

    if (passwordForm.old_password === passwordForm.new_password) {
      notify.error(
        isAr 
          ? "كلمة المرور الجديدة يجب أن تكون مختلفة عن كلمة المرور الحالية" 
          : "New password must be different from the current password"
      )
      return false
    }

    if (passwordForm.new_password.length < 8) {
      notify.error(isAr ? "كلمة المرور الجديدة يجب ألا تقل عن 8 أحرف" : "New password must be at least 8 characters")
      return false
    }

    const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).+$/
    
    if (!strongPasswordRegex.test(passwordForm.new_password)) {
      notify.error(
        isAr 
          ? "يجب أن تحتوي كلمة المرور على حرف كبير، حرف صغير، ورمز خاص واحد على الأقل" 
          : "Password must contain at least one uppercase letter, one lowercase letter, and one special character"
      )
      return false
    }

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      notify.error(isAr ? "كلمتا المرور غير متطابقتين" : "Passwords do not match")
      return false
    }
    return true
  }

  async function changePassword(e) {
    e.preventDefault()

    if (!validatePasswordForm()) return

    try {
      setChangingPassword(true)

      await api.post("/auth/change-password/", {
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password,
        confirm_password: passwordForm.confirm_password,
      })

      notify.success("password_change")
      setShowPasswordModal(false)

      setPasswordForm({
        old_password: "",
        new_password: "",
        confirm_password: "",
      })
    } catch (err) {
      notify.error("password_change")
    } finally {
      setChangingPassword(false)
    }
  }

  async function deleteAccount() {
    try {
      setDeleting(true)
      await api.delete("/auth/me/")
      notify.success("Account deleted successfully")
      localStorage.clear()
      window.location.href = "/login"
    } catch (err) {
      console.error(err)
      notify.error("Failed to delete account")
    } finally {
      setDeleting(false)
      setShowDeleteModal(false)
    }
  }

  if (loading) {
    return (
      <div className="profile-page">
        {t("profile.loading")}
      </div>
    )
  }

  // كود لإضافة خاصية (max) لحقل التاريخ في الـ HTML كخط دفاع أول لمنع اختيار تاريخ مستقبلي من الواجهة مباشرة
  const todayStr = new Date().toISOString().split("T")[0]

  return (
    <div className="profile-page" dir={isAr ? "rtl" : "ltr"}>
      <div className="profile-container">

        {/* HERO */}
        <div className="profile-hero">
          <img
            src={user?.profile_picture || "https://ui-avatars.com/api/?name=User"}
            className="avatar"
            alt="Avatar"
          />

          <div className="hero-info">
            <h2>
              {user?.first_name} {user?.last_name}
            </h2>
            <p>{user?.email}</p>

            <div className="hero-actions">
              <button onClick={() => setEditMode(true)}>{t("profile.edit")}</button>
              <button onClick={() => setShowPasswordModal(true)}>
                {t("profile.change_password")}
              </button>
              <button className="delete-btn" onClick={() => setShowDeleteModal(true)}>
                Delete Account
              </button>
            </div>
          </div>
        </div>

        {/* VIEW */}
        {!editMode ? (
          <div className="profile-card">
            <Row label={t("profile.username")} value={user?.username} />
            <Row label={t("profile.phone")} value={user?.phone_number || "-"} />
            <Row
              label={t("profile.language")}
              value={user?.language === "ar" ? t("profile.arabic") : t("profile.english")}
            />
            <Row label={t("profile.dob")} value={user?.date_of_birth || "-"} />
          </div>
        ) : (
          <form className="profile-card form" onSubmit={saveProfile}>
            <input name="username" value={form.username} onChange={handleChange} placeholder={t("profile.username")} />
            <input name="first_name" value={form.first_name} onChange={handleChange} placeholder={t("profile.first_name")} />
            <input name="last_name" value={form.last_name} onChange={handleChange} placeholder={t("profile.last_name")} />
            <input name="phone_number" value={form.phone_number} onChange={handleChange} placeholder={t("profile.phone")} />
            
            {/* تم إضافة max={todayStr} هنا لمنع اختيار تواريخ مستقبلية من الـ التقويم (Calendar Picker) الخاص بالمتصفح */}
            <input type="date" name="date_of_birth" value={form.date_of_birth} onChange={handleChange} max={todayStr} />

            <select name="language" value={form.language} onChange={handleChange}>
              <option value="en">{t("profile.english")}</option>
              <option value="ar">{t("profile.arabic")}</option>
            </select>

            <div className="actions">
              <button type="button" onClick={() => setEditMode(false)}>{t("common.cancel")}</button>
              <button disabled={saving}>
                {saving ? t("common.saving") : t("common.save")}
              </button>
            </div>
          </form>
        )}

        {/* PASSWORD MODAL */}
        {showPasswordModal && (
          <div className="overlay">
            <div className="modal">
              <h3>{t("profile.change_password")}</h3>

              <form onSubmit={changePassword} className="modal-form">
                <input
                  type="password"
                  name="old_password"
                  placeholder={t("profile.current_password")}
                  value={passwordForm.old_password}
                  onChange={handlePasswordChange}
                />
                <input
                  type="password"
                  name="new_password"
                  placeholder={t("profile.new_password")}
                  value={passwordForm.new_password}
                  onChange={handlePasswordChange}
                />
                <input
                  type="password"
                  name="confirm_password"
                  placeholder={t("profile.confirm_password")}
                  value={passwordForm.confirm_password}
                  onChange={handlePasswordChange}
                />

                <div className="actions">
                  <button type="button" onClick={() => setShowPasswordModal(false)}>
                    {t("common.cancel")}
                  </button>
                  <button disabled={changingPassword}>
                    {changingPassword ? t("common.saving") : t("common.save")}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* DELETE MODAL */}
        {showDeleteModal && (
          <div className="overlay">
            <div className="delete-modal">
              <h3>⚠️ Delete Account</h3>
              <p>Are you sure you want to delete your account?</p>
              <p className="delete-warning">This action cannot be undone.</p>

              <div className="delete-actions">
                <button className="cancel-btn" onClick={() => setShowDeleteModal(false)}>
                  Cancel
                </button>
                <button className="confirm-delete-btn" onClick={deleteAccount} disabled={deleting}>
                  {deleting ? "Deleting..." : "Delete"}
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div className="row">
      <span>{label}</span>
      <b>{value}</b>
    </div>
  )
}