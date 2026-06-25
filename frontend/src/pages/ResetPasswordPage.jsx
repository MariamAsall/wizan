import { useState } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import api from "../api/axios"
import "./Login.css"

export default function ResetPasswordPage() {
    const { t } = useTranslation()
    const [searchParams] = useSearchParams()
    const token = searchParams.get("token")
    const uid = searchParams.get("uid")

    const [password, setPassword] = useState("")
    const [confirm, setConfirm] = useState("")
    const [error, setError] = useState("")
    const [success, setSuccess] = useState(false)
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError("")

        if (!password || !confirm) {
            setError(t("resetPassword.error"))
            return
        }
        if (password !== confirm) {
            setError(t("resetPassword.mismatch"))
            return
        }
        if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/.test(password)){
            setError("Password must be 8+ chars with uppercase, lowercase, number, and special character (@$!%*?&).")
            return
        }
        setLoading(true)
        try {
            await api.post("/auth/password/reset/confirm/", {token,uid,new_password: password,})
            setSuccess(true)
        } catch {
            setError(t("resetPassword.error"))
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
                <h1 className="login-title">{t("resetPassword.title")}</h1>
                <p className="login-sub">{t("resetPassword.sub")}</p>

                {success ? (
                    <p className="login-sub" style={{ color: "#3C3489", fontWeight: 500 }}>
                        {t("resetPassword.success")}
                    </p>
                ) : (
                    <form onSubmit={handleSubmit} noValidate>
                        {error && <p className="login-error">{error}</p>}

                        <div className="mb-4">
                            <label className="form-label">{t("resetPassword.password")}</label>
                            <input
                                type="password"
                                className="form-field"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>

                        <div className="mb-4">
                            <label className="form-label">{t("resetPassword.confirm")}</label>
                            <input
                                type="password"
                                className="form-field"
                                placeholder="••••••••"
                                value={confirm}
                                onChange={(e) => setConfirm(e.target.value)}
                            />
                        </div>

                        <button type="submit" className="btn-primary" disabled={loading}>
                            {loading ? t("resetPassword.submitting") : t("resetPassword.submit")}
                        </button>
                    </form>
                )}

                <p className="text-center text-sm mt-6 text-muted-foreground">
                    <Link to="/login" className="font-bold text-primary hover:underline">
                        {t("resetPassword.backToLogin")}
                    </Link>
                </p>
            </div>
        </div>
    )
}