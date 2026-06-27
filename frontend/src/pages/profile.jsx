import { useEffect, useState } from "react"
import api from "../api/axios"
import "./profile.css"
import { notify } from "../components/notifications"


export default function Profile() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

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

  async function saveProfile(e) {
    e.preventDefault()

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
      setEditMode(false)
    } catch (err) {
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  async function changePassword(e) {
    e.preventDefault()

    if (
      !passwordForm.old_password ||
      !passwordForm.new_password ||
      !passwordForm.confirm_password
    ) return

    if (passwordForm.new_password !== passwordForm.confirm_password) return

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

    await api.delete("/users/me/")

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

  if (loading) return <div className="profile-page">Loading...</div>

  return (
    <div className="profile-page">
      <div className="profile-container">

        {/* HERO */}
        <div className="profile-hero">

          <img
            src={
              user?.profile_picture ||
              "https://ui-avatars.com/api/?name=User"
            }
            className="avatar"
          />

          <div className="hero-info">
            <h2>
              {user.first_name} {user.last_name}
            </h2>
            <p>{user.email}</p>

            <div className="hero-actions">
              <button onClick={() => setEditMode(true)}>Edit</button>
              <button onClick={() => setShowPasswordModal(true)}>
                Change Password
              </button>


               <button
                  className="delete-btn"
                  onClick={() => setShowDeleteModal(true)}
                >
                  Delete Account
                </button>
            </div>
          </div>
        </div>

        {/* VIEW */}
        {!editMode ? (
          <div className="profile-card">

            <Row label="Username" value={user.username} />
            <Row label="Phone" value={user.phone_number || "-"} />
            <Row label="Language" value={user.language} />
            <Row label="DOB" value={user.date_of_birth || "-"} />

          </div>
        ) : (
          <form className="profile-card form" onSubmit={saveProfile}>

            <input name="username" value={form.username} onChange={handleChange} placeholder="Username" />
            <input name="first_name" value={form.first_name} onChange={handleChange} placeholder="First name" />
            <input name="last_name" value={form.last_name} onChange={handleChange} placeholder="Last name" />
            <input name="phone_number" value={form.phone_number} onChange={handleChange} placeholder="Phone" />

            <input type="date" name="date_of_birth" value={form.date_of_birth} onChange={handleChange} />

            <select name="language" value={form.language} onChange={handleChange}>
              <option value="en">English</option>
              <option value="ar">Arabic</option>
            </select>

            <div className="actions">
              <button type="button" onClick={() => setEditMode(false)}>Cancel</button>
              <button disabled={saving}>
                {saving ? "Saving..." : "Save"}
              </button>
            </div>

          </form>
        )}

        {/* PASSWORD MODAL */}
        {showPasswordModal && (
          <div className="overlay">
            <div className="modal">

              <h3>Change Password</h3>

              <form onSubmit={changePassword} className="modal-form">

                <input
                  type="password"
                  name="old_password"
                  placeholder="Current password"
                  value={passwordForm.old_password}
                  onChange={handlePasswordChange}
                />

                <input
                  type="password"
                  name="new_password"
                  placeholder="New password"
                  value={passwordForm.new_password}
                  onChange={handlePasswordChange}
                />

                <input
                  type="password"
                  name="confirm_password"
                  placeholder="Confirm password"
                  value={passwordForm.confirm_password}
                  onChange={handlePasswordChange}
                />

                <div className="actions">
                  <button type="button" onClick={() => setShowPasswordModal(false)}>
                    Cancel
                  </button>

                  <button disabled={changingPassword}>
                    {changingPassword ? "Saving..." : "Save"}
                  </button>
                </div>

              </form>

            </div>
          </div>
        )}
        {showDeleteModal && (
  <div className="overlay">
    <div className="delete-modal">

      <h3>⚠️ Delete Account</h3>

      <p>
        Are you sure you want to delete your account?
      </p>

      <p className="delete-warning">
        This action cannot be undone.
      </p>

      <div className="delete-actions">
        <button
          className="cancel-btn"
          onClick={() => setShowDeleteModal(false)}
        >
          Cancel
        </button>

        <button
          className="confirm-delete-btn"
          onClick={deleteAccount}
          disabled={deleting}
        >
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