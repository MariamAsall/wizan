import { Outlet } from "react-router-dom"
import { Navbar } from "../components/Navbar"

export function MainLayout() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-8 mt-10">
        <Outlet />
      </main>
    </div>
  )
}