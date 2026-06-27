import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../api/axios"
import { GoogleLogin } from '@react-oauth/google'
import { useTranslation } from 'react-i18next'
import "./Login.css"

import { notify } from "../components/notifications"

function validate({ email, password }) {
  const errors = {}

  if (!email)
    errors.email = "Email is required."
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    errors.email = "Enter a valid email address."

  if (!password)
    errors.password = "Password is required."
  // else if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/.test(password))
  //   errors.password = "Password must be 8+ chars with uppercase, lowercase, number, and special character (@$!%*?&)."

  return errors
}

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState("")
  const [loading, setLoading] = useState(false)
  const { t } = useTranslation()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setServerError("")

    const errs = validate({ email, password })
    setErrors(errs)
    if (Object.keys(errs).length > 0) return

    setLoading(true)
    try {
      const { data } = await api.post("/auth/login/", { email, password })
      localStorage.setItem("access_token", data.tokens.access)
      localStorage.setItem("refresh_token", data.tokens.refresh)
      localStorage.setItem("user",          JSON.stringify(data.user))
      
      notify.success("login", {name: data.user.first_name || data.user.username,})

      localStorage.setItem("user", JSON.stringify(data.user))
      navigate("/quiz")
    } catch (err) {
      notify.error("login", err)
      const msg =
        err.response?.data?.non_field_errors?.[0] ||
        err.response?.data?.detail ||
        "Login failed. Please check your credentials."
      setServerError(msg)
    } finally {
      setLoading(false)
    }
  }

// const handleGoogleLogin = useGoogleLogin({
//   onSuccess: async (response) => {
//     try {
//       const { data } = await api.post("/auth/google/", {
//         token: response.access_token,
//       })
//       localStorage.setItem("access_token", data.tokens.access)
//       localStorage.setItem("refresh_token", data.tokens.refresh)
//       localStorage.setItem("user", JSON.stringify(data.user))
//       navigate("/quiz")
//     } catch {
//       setServerError("Google login failed. Please try again.")
//     }
//   },
//   onError: () => {
//     setServerError("Google login failed. Please try again.")
//   }
// })

  return (
    <div className="login-root">
      <div className="login-blob-sage" />
      <div className="login-blob-sun" />

      <div className="login-card">
        <p className="login-eyebrow">Welcome back</p>
        <h1 className="login-title">
          Your mind,<br /><em>measured</em> daily.
        </h1>
        <p className="login-sub">
          Wizan checks in with you every morning and builds your day around how you actually feel.
        </p>

        {serverError && <p className="login-error">{serverError}</p>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="mb-4">
            <label className="form-label">Email</label>
            <input
              type="email"
              className={`form-field ${errors.email ? "field-error" : ""}`}
              placeholder="you@example.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                setErrors((p) => ({ ...p, email: "" }))
              }}
            />
            {errors.email && <p className="field-error-msg">{errors.email}</p>}
          </div>

          <div className="mb-4">
            <label className="form-label">Password</label>
            <input
              type="password"
              className={`form-field ${errors.password ? "field-error" : ""}`}
              placeholder="••••••••"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                setErrors((p) => ({ ...p, password: "" }))
              }}
            />
            {errors.password && <p className="field-error-msg">{errors.password}</p>}
            <p className="text-right mt-1">
              <Link to="/forgot-password" className="text-xs text-primary hover:underline font-bold">
                Forgot password?
              </Link>
            </p>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Signing in…" : "Start my day →"}
          </button>
        </form>

        <div className="login-divider"><span>or</span></div>

        <GoogleLogin
        className="bg-red-500"
  onSuccess={async (response) => {
    try {
      const { data } = await api.post("/auth/google/", {
        token: response.credential, 
      })
      localStorage.setItem("access_token", data.tokens.access)
      localStorage.setItem("refresh_token", data.tokens.refresh)
      localStorage.setItem("user", JSON.stringify(data.user))
      navigate("/quiz")
    } catch {
      setServerError("Google login failed. Please try again.")
    }
  }}
  onError={() => setServerError("Google login failed. Please try again.")}
/>

        <p className="text-center text-sm mt-6 text-muted-foreground">
          No account?{" "}
          <Link to="/register" className="font-bold text-primary hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}