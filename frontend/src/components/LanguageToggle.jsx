import { useTranslation } from 'react-i18next'
import { Button } from './ui/button'  

export default function LanguageToggle() {
  const { i18n } = useTranslation()
  const isArabic = i18n.language === 'ar'

  const toggle = () => {
    const next = isArabic ? 'en' : 'ar'
    i18n.changeLanguage(next)

    document.documentElement.dir  = next === 'ar' ? 'rtl' : 'ltr'
    document.documentElement.lang = next

    localStorage.setItem('wizan-lang', next)
  }

  return (
    <Button variant="outline" size="sm" onClick={toggle}>
      {isArabic ? 'English' : 'عربي'}
    </Button>
  )
}