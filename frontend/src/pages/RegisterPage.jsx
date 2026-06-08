import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../api/axios"
import "./Register.css"
import "./Login.css"

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    first_name:       "",
    last_name:        "",
    username:         "",
    email:            "",
    password:         "",
    password_confirm: "",
  })
  const [error, setError]   = useState("")
  const [loading, setLoading] = useState(false)

  const set = (key) => (e) => setForm((p) => ({ ...p, [key]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      await api.post("/auth/register/", form)
      // Registration successful → send to login
      navigate("/login")
    } catch (err) {
      const data = err.response?.data
      if (data && typeof data === "object") {
        // Show the first field-level error returned by DRF
        const firstKey = Object.keys(data)[0]
        const firstMsg = Array.isArray(data[firstKey])
          ? data[firstKey][0]
          : data[firstKey]
        setError(`${firstKey}: ${firstMsg}`)
      } else {
        setError("Registration failed. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="register-root">
      <div className="register-blob-sun" />
      <div className="register-blob-sage" />

      <div className="register-card">
        <p className="register-eyebrow">Get started</p>

        <h1 className="register-title">
          Start your <em>journey.</em>
        </h1>

        <p className="register-sub">
          Create your Wizan account and let it learn how you work best.
        </p>

        {error && (
          <p className="login-error">{error}</p>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4 flex gap-3">
            <div className="flex-1">
              <label className="form-label">First name</label>
              <input
                type="text"
                className="form-field"
                placeholder="Mariam"
                value={form.first_name}
                onChange={set("first_name")}
                required
              />
            </div>
            <div className="flex-1">
              <label className="form-label">Last name</label>
              <input
                type="text"
                className="form-field"
                placeholder="Ahmed"
                value={form.last_name}
                onChange={set("last_name")}
                required
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-field"
              placeholder="mariam123"
              value={form.username}
              onChange={set("username")}
              required
            />
          </div>

          <div className="mb-4">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-field"
              placeholder="you@example.com"
              value={form.email}
              onChange={set("email")}
              required
            />
          </div>

          <div className="mb-4">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-field"
              placeholder="••••••••"
              value={form.password}
              onChange={set("password")}
              required
            />
          </div>

          <div className="mb-4">
            <label className="form-label">Confirm password</label>
            <input
              type="password"
              className="form-field"
              placeholder="••••••••"
              value={form.password_confirm}
              onChange={set("password_confirm")}
              required
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Creating account…" : "Create account →"}
          </button>
        </form>

        <p className="text-center text-sm mt-6 text-muted-foreground">
          Already have an account?{" "}
          <Link to="/login" className="font-bold text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}