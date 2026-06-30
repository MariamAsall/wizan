import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"
import { useGoogleLogin } from "@react-oauth/google"
import api from "../api/axios"
import "./Login.css"
import { notify } from "../components/notifications" 

function validate({ email, password }, t) {
  const errors = {}
  if (!email) errors.email = t("login.errors.email") 
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = t("login.errors.emailFormat")
  if (!password) errors.password = t("login.errors.password")
  return errors
}

export default function LoginPage() {
  const navigate = useNavigate()
  const { t, i18n } = useTranslation()
  const isAr = i18n.language === "ar"

  const [email, setEmail]             = useState("")
  const [password, setPassword]       = useState("")
  const [errors, setErrors]           = useState({})
  const [serverError, setServerError] = useState("")
  const [loading, setLoading]         = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setServerError("")
    const errs = validate({ email, password }, t)
    setErrors(errs)
    if (Object.keys(errs).length > 0) return
    setLoading(true)
    try {
      const { data } = await api.post("/auth/login/", { email, password })
      localStorage.setItem("access_token",  data.tokens.access)
      localStorage.setItem("refresh_token", data.tokens.refresh)
      localStorage.setItem("user",          JSON.stringify(data.user))
      navigate("/quiz")
      notify.success("login", { name: data.user.username } )
    } catch (err) {
      const msg =
        err.response?.data?.non_field_errors?.[0] ||
        err.response?.data?.detail ||
        t("login.error")
      setServerError(msg)
      notify.error("login")
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = useGoogleLogin({
    onSuccess: async (response) => {
      try {
        const { data } = await api.post("/auth/google/", {
          token: response.access_token,
        })
        localStorage.setItem("access_token", data.tokens.access)
        localStorage.setItem("refresh_token", data.tokens.refresh)
        localStorage.setItem("user", JSON.stringify(data.user))
        navigate("/quiz")
      } catch {
        setServerError(t("login.error"))
      }
    },
    onError: () => setServerError(t("login.error"))
  })

  return (
    <div className="login-root" dir={isAr ? "rtl" : "ltr"}>
      <div className="login-blob-sage" />
      <div className="login-blob-sun" />

      <div className="login-card">
        <p className="login-eyebrow">{t("login.eyebrow")}</p>
        <h1 className="login-title" dangerouslySetInnerHTML={{ __html: t("login.title") }} />
        <p className="login-sub">{t("login.sub")}</p>

        {serverError && <p className="login-error">{serverError}</p>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="mb-4">
            <label className="form-label">{t("login.email")}</label>
            <input
              type="email"
              className={`form-field ${errors.email ? "field-error" : ""}`}
              placeholder="you@example.com"
              value={email}
              onChange={(e) => { setEmail(e.target.value); setErrors((p) => ({ ...p, email: "" })) }}
            />
            {errors.email && <p className="field-error-msg">{errors.email}</p>}
          </div>

          <div className="mb-4">
            <label className="form-label">{t("login.password")}</label>
            <input
              type="password"
              className={`form-field ${errors.password ? "field-error" : ""}`}
              placeholder="••••••••"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setErrors((p) => ({ ...p, password: "" })) }}
            />
            {errors.password && <p className="field-error-msg">{errors.password}</p>}
            <p className="text-right mt-1">
              <Link to="/forgot-password" className="text-xs text-primary hover:underline font-bold">
                {t("login.forgotPassword")}
              </Link>
            </p>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? t("login.submitting") : t("login.submit")}
          </button>
        </form>

        <div className="login-divider"><span>or</span></div>

        <button type="button" className="btn-google" onClick={() => handleGoogleLogin()}>
            <svg width="20px" height="20px" viewBox="-3 0 262 262" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid"><path d="M255.878 133.451c0-10.734-.871-18.567-2.756-26.69H130.55v48.448h71.947c-1.45 12.04-9.283 30.172-26.69 42.356l-.244 1.622 38.755 30.023 2.685.268c24.659-22.774 38.875-56.282 38.875-96.027" fill="#4285F4"/><path d="M130.55 261.1c35.248 0 64.839-11.605 86.453-31.622l-41.196-31.913c-11.024 7.688-25.82 13.055-45.257 13.055-34.523 0-63.824-22.773-74.269-54.25l-1.531.13-40.298 31.187-.527 1.465C35.393 231.798 79.49 261.1 130.55 261.1" fill="#34A853"/><path d="M56.281 156.37c-2.756-8.123-4.351-16.827-4.351-25.82 0-8.994 1.595-17.697 4.206-25.82l-.073-1.73L15.26 71.312l-1.335.635C5.077 89.644 0 109.517 0 130.55s5.077 40.905 13.925 58.602l42.356-32.782" fill="#FBBC05"/><path d="M130.55 50.479c24.514 0 41.05 10.589 50.479 19.438l36.844-35.974C195.245 12.91 165.798 0 130.55 0 79.49 0 35.393 29.301 13.925 71.947l42.211 32.783c10.59-31.477 39.891-54.251 74.414-54.251" fill="#EB4335"/></svg>
          {t("login.googleButton")}
        </button>

        <p className="text-center text-sm mt-6 text-muted-foreground">
          {t("login.noAccount")}{" "}
          <Link to="/register" className="font-bold text-primary hover:underline">
            {t("login.signUp")}
          </Link>
        </p>
      </div>
    </div>
  )
}