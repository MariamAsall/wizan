import { useState } from 'react'
import './App.css'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import MainLayout    from "./layouts/MainLayout"
import LoginPage     from "./pages/LoginPage"
import RegisterPage  from "./pages/RegisterPage"
import QuizPage from "./pages/QuizPage";
import DashboardPage from "./pages/DashboardPage";
import TasksPage from "./pages/TasksPage";
import RegulationPage from "./pages/RegulationPage";

import ChatPage from "./pages/ChatPage";
import QuizResultPage from './pages/QuizResultPage';
import DocumentsPage from './pages/DocumentsPage';

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
          <Route path="/result" element={<QuizResultPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/tasks"     element={<TasksPage />} />
          <Route path="/chat"      element={<ChatPage />} />
          <Route path="/documents"      element={<DocumentsPage />} />
          <Route path="/regulation" element={<RegulationPage />} />
        </Route>

        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
