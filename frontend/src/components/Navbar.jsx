import { useState } from "react"
import { NavLink, useLocation, useNavigate } from "react-router-dom"
import ThemeToggle from "../components/ThemeToggle"
import { Brain, Menu, X } from "lucide-react"
import LanguageToggle from "./LanguageToggle"
import { t } from "i18next"
import NotificationBell from "./NotificationBell"


const navLinkClass = ({ isActive }) =>
    `px-4 py-1 rounded-xl text-sm transition-all duration-300 ${isActive
        ? "bg-foreground text-background font-medium"
        : "text-foreground hover:text-background hover:bg-foreground"
    }`

export function Navbar() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const isPublic = ["/", "/login", "/register", "/forgot-password", "/reset-password"].includes(location.pathname)
  const isLanding = location.pathname === "/"

  
  const links = [
    { to: "/quiz", label: t("nav.quiz") },
    { to: "/result", label: t("nav.result") },
    { to: "/tasks", label: t("nav.tasks") },
    { to: "/dashboard", label: t("nav.dashboard") },
    { to: "/chat", label: t("nav.chat") },
    { to: "/documents", label: t("nav.documents") },
]

  const handleLogout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("user")

    setOpen(false)
    navigate("/login")
  }

  return (
    <nav className="fixed top-0 left-0 right-0 border-b border-border bg-background z-50">
      {/* Top bar */}
      <div className="px-6 py-3 flex items-center justify-between">

        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-2 font-semibold text-foreground">
          <Brain size={20} className="text-primary" />
          <p>
            {t("wizan").slice(0, 2)}
            <span className="text-primary">{t("wizan").slice(2)}</span>
          </p>
        </NavLink>

        {/* Desktop links */}
  {isLanding ? (
  <div className="hidden md:flex ms-auto me-4 items-center gap-2">
    <NavLink to="/register" className="bg-foreground text-background text-sm px-4 py-1 rounded-2xl cursor-pointer hove:bg-foreground/90">{t("nav.register")}</NavLink>
    <NavLink to="/login" className="bg-foreground text-background text-sm px-4 py-1 rounded-2xl cursor-pointer hove:bg-foreground/90">{t("nav.login")}</NavLink>
  </div>
) : !isPublic ? (
  <div className="hidden md:flex items-center gap-2">
    {links.map(({ to, label }) => (
      <NavLink key={to} to={to} className={navLinkClass}>
        {label}
      </NavLink>
    ))}
    <button
      onClick={handleLogout}
      className="px-4 py-1 rounded-xl text-sm text-red-500 hover:bg-red-500/10 transition"
    >
      {t("nav.logout")}
    </button>
  </div>
) : null}

        {/* Right side */}
       <div className="flex items-center gap-2">

  
  {!isPublic && <NotificationBell /> }

  <LanguageToggle />

  <ThemeToggle />

  {/* Hamburger */}
  {(isLanding || !isPublic) && (
  <button
    className="md:hidden p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
    onClick={() => setOpen(!open)}
  >
    {open ? <X size={20} /> : <Menu size={20} />}
  </button>
)}

</div>
      </div>

      {/* Mobile menu */}
      {open && (
  <div className="md:hidden border-t border-border px-4 py-3 flex flex-col gap-1">
    {isLanding ? (
      <>
        <NavLink to="/register" className="bg-foreground text-background text-sm px-4 py-1 rounded-2xl cursor-pointer hove:bg-foreground/90">{t("nav.register")}</NavLink>
    <NavLink to="/login" className="bg-foreground text-background text-sm px-4 py-1 rounded-2xl cursor-pointer hove:bg-foreground/90">{t("nav.login")}</NavLink>
      </>
    ) : !isPublic ? (
      <>
        {links.map(({ to, label }) => (
          <NavLink key={to} to={to} className={navLinkClass} onClick={() => setOpen(false)}>
            {label}
          </NavLink>
        ))}
        <button
          onClick={handleLogout}
          className="mt-2 px-4 py-2 rounded-xl text-sm text-red-500 hover:bg-red-500/10 transition text-left"
        >
          {t("nav.logout")}
        </button>
      </>
    ) : null}
  </div>
)}
    </nav>
  )
}