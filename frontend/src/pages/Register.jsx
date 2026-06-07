import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import "./Register.css"
import "./Login.css"   /* reuses .form-label .form-field .btn-primary */

const FIELDS = [
  { label: "Full name", type: "text",     key: "name",     placeholder: "Mariam"          },
  { label: "Email",     type: "email",    key: "email",    placeholder: "you@example.com" },
  { label: "Password",  type: "password", key: "password", placeholder: "••••••••"        },
]

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: "", email: "", password: "" })

  const handleSubmit = (e) => {
    e.preventDefault()
    navigate("/quiz")
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

        <form onSubmit={handleSubmit}>
          {FIELDS.map(({ label, type, key, placeholder }) => (
            <div key={key} className="mb-4">
              <label className="form-label">{label}</label>
              <input
                type={type}
                className="form-field"
                placeholder={placeholder}
                value={form[key]}
                onChange={(e) => setForm((p) => ({ ...p, [key]: e.target.value }))}
              />
            </div>
          ))}

          <button type="submit" className="btn-primary">
            Create account →
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