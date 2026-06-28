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
import Profile from './pages/profile';

import { Toaster } from "react-hot-toast"
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';

// import useNotifications from "./hooks/useNotifications"

import ProtectedRoute from './components/ProtectedRoute'
import LandingPage from './pages/LandingPage'
import PublicLayout from './layouts/PublicLayout';

function App() {
  const { i18n } = useTranslation()

  // useNotifications()
  useEffect(() => {
    // Restore saved language on first load
    const saved = localStorage.getItem('wizan-lang') || 'en'
    i18n.changeLanguage(saved)
    document.documentElement.dir = saved === 'ar' ? 'rtl' : 'ltr'
    document.documentElement.lang = saved
  }, [])

  return (
    <>
   
      <Toaster
        position="buttom-right"
        reverseOrder={false}
        toastOptions={{
          duration: 4000,

          style: {
            background: "var(--card)",
            color: "var(--foreground)",
            border: "1px solid var(--border)",
            borderRadius: "12px",
          },
        }}
      />

    <BrowserRouter>
      <Routes>

{/* Public routes — navbar with no links */}
<Route element={<PublicLayout />}>
  <Route path="/" element={<LandingPage />} />
  <Route path="/login" element={<LoginPage />} />
  <Route path="/register" element={<RegisterPage />} />
  <Route path="/forgot-password" element={<ForgotPasswordPage />} />
  <Route path="/reset-password" element={<ResetPasswordPage />} />
</Route>

  {/* Protected routes */}
<Route element={<ProtectedRoute />}>
  <Route element={<MainLayout />}>
    <Route path="/quiz" element={<QuizPage />} />
    <Route path="/result" element={<QuizResultPage />} />
    <Route path="/dashboard" element={<DashboardPage />} />
    <Route path="/tasks" element={<TasksPage />} />
    <Route path="/chat" element={<ChatPage />} />
    <Route path="/documents" element={<DocumentsPage />} />
    <Route path="/regulation" element={<RegulationPage />} />
    <Route path="/profile" element={<Profile />} />
  </Route>
</Route>
</Routes>
   
    </BrowserRouter>
    </>
  )
}

export default App
