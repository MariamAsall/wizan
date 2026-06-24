import { useState } from "react"
import { Link } from "react-router-dom"
import { useTranslation } from "react-i18next"
import api from "../api/axios"
import "./Login.css"

export default function ForgotPasswordPage() {
  const { t } = useTranslation()
  const [email, setEmail]     = useState("")
  const [error, setError]     = useState("")
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")

    if (!email) {
      setError(t("forgotPassword.error"))
      return
    }

    setLoading(true)
    try {
      await api.post("/auth/password/reset/", { email })
      setSuccess(true)
    } catch {
      setError(t("forgotPassword.error"))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-root">
      <div className="login-blob-sage" />
      <div className="login-blob-sun" />

      <div className="login-card">
        <p className="login-eyebrow">{t("wizan")}</p>
        <h1 className="login-title">{t("forgotPassword.title")}</h1>
        <p className="login-sub">{t("forgotPassword.sub")}</p>

        {success ? (
          <p className="login-sub" style={{ color: "#3C3489", fontWeight: 500 }}>
            {t("forgotPassword.success")}
          </p>
        ) : (
          <form onSubmit={handleSubmit} noValidate>
            {error && <p className="login-error">{error}</p>}

            <div className="mb-4">
              <label className="form-label">{t("forgotPassword.email")}</label>
              <input
                type="email"
                className="form-field"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? t("forgotPassword.submitting") : t("forgotPassword.submit")}
            </button>
          </form>
        )}

        <p className="text-center text-sm mt-6 text-muted-foreground">
          <Link to="/login" className="font-bold text-primary hover:underline">
            {t("forgotPassword.backToLogin")}
          </Link>
        </p>
      </div>
    </div>
  )
}