import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"
import api from "../api/axios"
import "./Register.css"
import "./Login.css"
import { notify } from "../components/notifications"

function getPasswordStrength(password, t) {
  if (!password) return null
  let score = 0
  if (password.length >= 8)       score++
  if (/[A-Z]/.test(password))     score++
  if (/[a-z]/.test(password))     score++
  if (/\d/.test(password))        score++
  if (/[@$!%*?&]/.test(password)) score++

  if (score <= 2) return { label: t("register.strength.weak"),   color: "bg-red-400",    width: "w-1/4" }
  if (score === 3) return { label: t("register.strength.fair"),  color: "bg-yellow-400", width: "w-2/4" }
  if (score === 4) return { label: t("register.strength.good"),  color: "bg-blue-400",   width: "w-3/4" }
  return                  { label: t("register.strength.strong"), color: "bg-green-500",  width: "w-full" }
}

function validate({ first_name, last_name, username, email, password, password_confirm }, t) {
  const errors = {}
  if (!first_name.trim()) errors.first_name = t("register.errors.firstName")
  if (!last_name.trim())  errors.last_name  = t("register.errors.lastName")
  if (!username)                                      errors.username = t("register.errors.username")
  else if (username.length < 3)                       errors.username = t("register.errors.usernameMin")
  else if (!/^[a-zA-Z0-9]+$/.test(username))         errors.username = t("register.errors.usernameFormat")
  if (!email)                                         errors.email = t("register.errors.email")
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = t("register.errors.emailFormat")
  if (!password)                                      errors.password = t("register.errors.password")
  else if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/.test(password)) errors.password = t("register.errors.passwordFormat")
  if (!password_confirm)                              errors.password_confirm = t("register.errors.confirmPassword")
  else if (password !== password_confirm)             errors.password_confirm = t("register.errors.passwordMismatch")
  return errors
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const { t, i18n } = useTranslation()
  const isAr = i18n.language === "ar"

  const [form, setForm] = useState({
    first_name: "", last_name: "", username: "",
    email: "", password: "", password_confirm: "",
  })
  const [errors, setErrors]           = useState({})
  const [serverError, setServerError] = useState("")
  const [loading, setLoading]         = useState(false)

  const strength = getPasswordStrength(form.password, t)

  const set = (key) => (e) => {
    setForm((p) => ({ ...p, [key]: e.target.value }))
    setErrors((p) => ({ ...p, [key]: "" }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setServerError("")
    const errs = validate(form, t)
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
        setServerError(t("register.errors.failed"))
      }
    } finally {
      setLoading(false)
    }
  }

  const fieldError = (key) => errors[key]
    ? <p className="field-error-msg">{errors[key]}</p>
    : null

  return (
    <div className="register-root" dir={isAr ? "rtl" : "ltr"}>
      <div className="register-blob-sun" />
      <div className="register-blob-sage" />

      <div className="register-card">
        <p className="register-eyebrow">{t("register.eyebrow")}</p>
        <h1 className="register-title" dangerouslySetInnerHTML={{ __html: t("register.title") }} />
        <p className="register-sub">{t("register.sub")}</p>

        {serverError && <p className="login-error">{serverError}</p>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="mb-4 flex gap-3">
            <div className="flex-1">
              <label className="form-label">{t("register.firstName")}</label>
              <input type="text" className={`form-field ${errors.first_name ? "field-error" : ""}`}
                placeholder="Mariam" value={form.first_name} onChange={set("first_name")} />
              {fieldError("first_name")}
            </div>
            <div className="flex-1">
              <label className="form-label">{t("register.lastName")}</label>
              <input type="text" className={`form-field ${errors.last_name ? "field-error" : ""}`}
                placeholder="Ahmed" value={form.last_name} onChange={set("last_name")} />
              {fieldError("last_name")}
            </div>
          </div>

          <div className="mb-4">
            <label className="form-label">{t("register.username")}</label>
            <input type="text" className={`form-field ${errors.username ? "field-error" : ""}`}
              placeholder="mariam123" value={form.username} onChange={set("username")} />
            {fieldError("username")}
          </div>

          <div className="mb-4">
            <label className="form-label">{t("register.email")}</label>
            <input type="email" className={`form-field ${errors.email ? "field-error" : ""}`}
              placeholder="you@example.com" value={form.email} onChange={set("email")} />
            {fieldError("email")}
          </div>

          <div className="mb-4">
            <label className="form-label">{t("register.password")}</label>
            <input type="password" className={`form-field ${errors.password ? "field-error" : ""}`}
              placeholder="••••••••" value={form.password} onChange={set("password")} />
            {form.password && strength && (
              <div className="mt-2">
                <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className={`h-full rounded-full transition-all duration-300 ${strength.color} ${strength.width}`} />
                </div>
                <p className={`text-xs mt-1 font-medium
                  ${strength.label === t("register.strength.weak")   ? "text-red-500"    : ""}
                  ${strength.label === t("register.strength.fair")   ? "text-yellow-500" : ""}
                  ${strength.label === t("register.strength.good")   ? "text-blue-500"   : ""}
                  ${strength.label === t("register.strength.strong") ? "text-green-600"  : ""}
                `}>{strength.label}</p>
              </div>
            )}
            {fieldError("password")}
          </div>

          <div className="mb-4">
            <label className="form-label">{t("register.confirmPassword")}</label>
            <input type="password" className={`form-field ${errors.password_confirm ? "field-error" : ""}`}
              placeholder="••••••••" value={form.password_confirm} onChange={set("password_confirm")} />
            {fieldError("password_confirm")}
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? t("register.submitting") : t("register.submit")}
          </button>
        </form>

        <p className="text-center text-sm mt-6 text-muted-foreground">
          {t("register.hasAccount")}{" "}
          <Link to="/login" className="font-bold text-primary hover:underline">
            {t("register.signIn")}
          </Link>
        </p>
      </div>
    </div>
  )
}