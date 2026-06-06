import { useState } from 'react'
import './App.css'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'

function App() {
  const { i18n } = useTranslation()

  useEffect(() => {
    // Restore saved language on first load
    const saved = localStorage.getItem('wizan-lang') || 'en'
    i18n.changeLanguage(saved)
    document.documentElement.dir  = saved === 'ar' ? 'rtl' : 'ltr'
    document.documentElement.lang = saved
  }, [])

  return (
    <>
      <h1>Wizan</h1>
    </>
  )
}

export default App
