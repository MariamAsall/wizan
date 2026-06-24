import toast from "react-hot-toast"

export const notify = {
  success: (action, data = {}) => {
    const messages = {
      login: `Welcome back, ${data.name || "user"} 👋`,
      register: `Account created successfully 🎉`,
      task_create: `Task "${data.task}" added successfully 🎯`,
      task_update: `Task updated successfully ✨`,
      password_change: `Password updated successfully 🔐`,
      logout: `See you soon 👋`,
    }

    toast.success(messages[action] || "Success ✔️")
  },

  error: (action, error) => {
    const messages = {
      login: "Login failed. Check your credentials.",
      register: "Registration failed. Please try again.",
      task_create: "Failed to add task.",
      task_update: "Failed to update task.",
      password_change: "Password update failed.",
    }

    const fallback =
      error?.response?.data?.detail ||
      error?.response?.data?.error ||
      messages[action] ||
      "Something went wrong ❌"

    toast.error(fallback)
  },
}