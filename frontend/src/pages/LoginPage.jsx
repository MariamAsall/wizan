import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../api/axios"
import "./Login.css"

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail]       = useState("")
  const [password, setPassword] = useState("")
  const [error, setError]       = useState("")
  const [loading, setLoading]   = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const { data } = await api.post("/auth/login/", { email, password })

      localStorage.setItem("access_token",  data.tokens.access)
      localStorage.setItem("refresh_token", data.tokens.refresh)
      localStorage.setItem("user",          JSON.stringify(data.user))

      navigate("/quiz")
    } catch (err) {
      const msg =
        err.response?.data?.non_field_errors?.[0] ||
        err.response?.data?.detail ||
        "Login failed. Please check your credentials."
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-root">
      <div className="login-blob-sage" />
      <div className="login-blob-sun" />

      <div className="login-card">
        <p className="login-eyebrow">Welcome back</p>

        <h1 className="login-title">
          Your mind,<br />
          <em>measured</em> daily.
        </h1>

        <p className="login-sub">
          Wizan checks in with you every morning and builds your day around how you actually feel.
        </p>

        {error && (
          <p className="login-error">{error}</p>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-field"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="mb-4">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Signing in…" : "Start my day →"}
          </button>
        </form>

        <div className="login-divider"><span>or</span></div>

        <button type="button" className="btn-google">
          <span className="google-icon">
            <span style={{ background: "#4285F4", display: "block" }} />
            <span style={{ background: "#34A853", display: "block" }} />
            <span style={{ background: "#FBBC05", display: "block" }} />
            <span style={{ background: "#EA4335", display: "block" }} />
          </span>
          Continue with Google
        </button>

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