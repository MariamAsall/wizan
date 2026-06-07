import { useState } from 'react'
import './App.css'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import MainLayout    from "./layouts/MainLayout"
import LoginPage     from "./pages/Login"
import RegisterPage  from "./pages/Register"
import QuizPage from "./pages/Quiz";
import DashboardPage from "./pages/Dashboard";
import TasksPage from "./pages/Tasks";
import ChatPage from "./pages/Chat";

function App() {
  const { i18n } = useTranslation()

  useEffect(() => {
    // Restore saved language on first load
    const saved = localStorage.getItem('wizan-lang') || 'en'
    i18n.changeLanguage(saved)
    document.documentElement.dir = saved === 'ar' ? 'rtl' : 'ltr'
    document.documentElement.lang = saved
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        {/* Public — no navbar */}
        <Route path="/login"    element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected — with navbar via MainLayout */}
        <Route element={<MainLayout />}>
          <Route path="/quiz"      element={<QuizPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/tasks"     element={<TasksPage />} />
          <Route path="/chat"      element={<ChatPage />} />
        </Route>

        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
