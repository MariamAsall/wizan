import { useTheme } from "next-themes"
import { Moon, Sun, SunDim, SunIcon, SunMedium, Sunrise } from "lucide-react"

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const isDark = theme === "dark"

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      aria-label="Toggle theme"
      className={`relative flex items-center w-14 h-7 rounded-full border transition-colors duration-300 bg-muted border-border`}
    >

      {/* labels */}
      <span className={`absolute left-2 transition-all duration-200 ${isDark ? "opacity-0" : "opacity-100"}`}>
        <SunMedium size={19} className="text-destructive" />
      </span>
      <span className={`absolute right-2 transition-all duration-200 ${isDark ? "opacity-100" : "opacity-0"}`}>
        <Moon size={19} className="text-primary" />
      </span>
    </button>
  )
}