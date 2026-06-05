import { useState } from 'react'
import './App.css'

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/Login";
import QuizPage from "./pages/Quiz";
import DashboardPage from "./pages/Dashboard";
import TasksPage from "./pages/Tasks";
import ChatPage from "./pages/Chat";

function App() {

  return (
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
    </BrowserRouter>
  );
}

export default App
