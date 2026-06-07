import { useState } from 'react'
import './App.css'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { MainLayout } from './layouts/MainLayout';
import Quiz from './pages/Quiz';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Tasks from './pages/Tasks';
import Chat from './pages/Chat';

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
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/login" />} />

        <Route element={<MainLayout />}>
          <Route path="/quiz" element={<Quiz />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/chat" element={<Chat />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App
