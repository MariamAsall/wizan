import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../api/axios"
import "./Register.css"
import "./Login.css"
import { notify } from "../components/notifications"


function getPasswordStrength(password) {
  if (!password) return null
  let score = 0
  if (password.length >= 8)       score++
  if (/[A-Z]/.test(password))     score++
  if (/[a-z]/.test(password))     score++
  if (/\d/.test(password))        score++
  if (/[@$!%*?&]/.test(password)) score++

  if (score <= 2) return { label: "Weak",   color: "bg-red-400",    width: "w-1/4" }
  if (score === 3) return { label: "Fair",   color: "bg-yellow-400", width: "w-2/4" }
  if (score === 4) return { label: "Good",   color: "bg-blue-400",   width: "w-3/4" }
  return                  { label: "Strong", color: "bg-green-500",  width: "w-full" }
}

function validate({ first_name, last_name, username, email, password, password_confirm }) {
  const errors = {}

  if (!first_name.trim())
    errors.first_name = "First name is required."

  if (!last_name.trim())
    errors.last_name = "Last name is required."

  if (!username)
    errors.username = "Username is required."
  else if (username.length < 3)
    errors.username = "Username must be at least 3 characters."
  else if (!/^[a-zA-Z0-9]+$/.test(username))
    errors.username = "Username can only contain letters and numbers."

  if (!email)
    errors.email = "Email is required."
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    errors.email = "Enter a valid email address."

  if (!password)
    errors.password = "Password is required."
  else if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/.test(password))
    errors.password = "Password must be 8+ chars with uppercase, lowercase, number, and special character (@$!%*?&)."

  if (!password_confirm)
    errors.password_confirm = "Please confirm your password."
  else if (password !== password_confirm)
    errors.password_confirm = "Passwords do not match."

  return errors
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    first_name: "", last_name: "", username: "",
    email: "", password: "", password_confirm: "",
  })
  const [errors, setErrors]           = useState({})
  const [serverError, setServerError] = useState("")
  const [loading, setLoading]         = useState(false)

  const strength = getPasswordStrength(form.password)

  const set = (key) => (e) => {
    setForm((p) => ({ ...p, [key]: e.target.value }))
    setErrors((p) => ({ ...p, [key]: "" }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setServerError("")

    const errs = validate(form)
    setErrors(errs)
    if (Object.keys(errs).length > 0) return

    setLoading(true)
    try {
      await api.post("/auth/register/", form)
      notify.success("register")
      navigate("/login")
    } catch (err) {
      notify.error("register", err)
      const data = err.response?.data
      if (data && typeof data === "object") {
        const firstKey = Object.keys(data)[0]
        const firstMsg = Array.isArray(data[firstKey]) ? data[firstKey][0] : data[firstKey]
        setServerError(`${firstKey}: ${firstMsg}`)
      } else {
        setServerError("Registration failed. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  const fieldError = (key) => (
    errors[key] ? <p className="field-error-msg">{errors[key]}</p> : null
  )

  return (
    <div className="register-root">
      <div className="register-blob-sun" />
      <div className="register-blob-sage" />

      <div className="register-card">
        <p className="register-eyebrow">Get started</p>
        <h1 className="register-title">Start your <em>journey.</em></h1>
        <p className="register-sub">
          Create your Wizan account and let it learn how you work best.
        </p>

        {serverError && <p className="login-error">{serverError}</p>}

        <form onSubmit={handleSubmit} noValidate>

          {/* First + Last name */}
          <div className="mb-4 flex gap-3">
            <div className="flex-1">
              <label className="form-label">First name</label>
              <input
                type="text"
                className={`form-field ${errors.first_name ? "field-error" : ""}`}
                placeholder="Mariam"
                value={form.first_name}
                onChange={set("first_name")}
              />
              {fieldError("first_name")}
            </div>
            <div className="flex-1">
              <label className="form-label">Last name</label>
              <input
                type="text"
                className={`form-field ${errors.last_name ? "field-error" : ""}`}
                placeholder="Ahmed"
                value={form.last_name}
                onChange={set("last_name")}
              />
              {fieldError("last_name")}
            </div>
          </div>

          {/* Username */}
          <div className="mb-4">
            <label className="form-label">Username</label>
            <input
              type="text"
              className={`form-field ${errors.username ? "field-error" : ""}`}
              placeholder="mariam123"
              value={form.username}
              onChange={set("username")}
            />
            {fieldError("username")}
          </div>

          {/* Email */}
          <div className="mb-4">
            <label className="form-label">Email</label>
            <input
              type="email"
              className={`form-field ${errors.email ? "field-error" : ""}`}
              placeholder="you@example.com"
              value={form.email}
              onChange={set("email")}
            />
            {fieldError("email")}
          </div>

          {/* Password */}
          <div className="mb-4">
            <label className="form-label">Password</label>
            <input
              type="password"
              className={`form-field ${errors.password ? "field-error" : ""}`}
              placeholder="••••••••"
              value={form.password}
              onChange={set("password")}
            />

            {/* Strength bar */}
            {form.password && strength && (
              <div className="mt-2">
                <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className={`h-full rounded-full transition-all duration-300 ${strength.color} ${strength.width}`} />
                </div>
                <p className={`text-xs mt-1 font-medium
                  ${strength.label === "Weak"   ? "text-red-500"    : ""}
                  ${strength.label === "Fair"   ? "text-yellow-500" : ""}
                  ${strength.label === "Good"   ? "text-blue-500"   : ""}
                  ${strength.label === "Strong" ? "text-green-600"  : ""}
                `}>
                  {strength.label} password
                </p>
              </div>
            )}

            {fieldError("password")}
          </div>

          {/* Confirm password */}
          <div className="mb-4">
            <label className="form-label">Confirm password</label>
            <input
              type="password"
              className={`form-field ${errors.password_confirm ? "field-error" : ""}`}
              placeholder="••••••••"
              value={form.password_confirm}
              onChange={set("password_confirm")}
            />
            {fieldError("password_confirm")}
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