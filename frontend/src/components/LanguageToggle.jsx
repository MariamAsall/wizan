import { useTranslation } from "react-i18next"

export default function LanguageToggle() {
  const { i18n } = useTranslation()
  const isArabic = i18n.language === "ar"

  const toggle = () => {
    const next = isArabic ? "en" : "ar"
    i18n.changeLanguage(next)
    document.documentElement.dir  = next === "ar" ? "rtl" : "ltr"
    document.documentElement.lang = next
    localStorage.setItem("wizan-lang", next)
  }

  return (
    <button
      onClick={toggle}
      className="h-8 px-3 rounded-full text-[12px] font-bold border border-border text-muted-foreground hover:text-foreground hover:border-foreground transition-colors"
    >
      {isArabic ? "EN" : "ع"}
    </button>
  )
}