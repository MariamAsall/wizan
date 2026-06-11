import { useState, useEffect } from "react";
import axios from "axios";
import "./Tasks.css";

export default function TasksPage() {
  const [input, setInput] = useState("");
  const [priority, setPriority] = useState("medium");
  const [deadline, setDeadline] = useState("")

  const [allowed, setAllowed] = useState([]);
  const [postponed, setPostponed] = useState([]);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const token = localStorage.getItem("access_token");

      const res = await axios.get(
        "http://localhost:8000/api/tasks/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const tasks = res.data;

      setAllowed(
        tasks.filter(
          (task) =>
            task.status === "allowed" ||
            task.status === "pending" ||
            task.status === "overridden"
        )
      );

      setPostponed(
        tasks.filter((task) => task.status === "postponed")
      );
    } catch (error) {
      console.error("Fetch Tasks Error:", error.response?.data || error);
    }
  };

  const addTask = async () => {
    if (!input.trim()) return;

    try {
      const token = localStorage.getItem("access_token");

      const response = await axios.post(
        "http://localhost:8000/api/tasks/",
      {
        name: input.trim(),
        priority,
        cognitive_cost: 50,
        deadline: deadline || null,
      },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setAllowed((prev) => [...prev, response.data]);

      setInput("");
      setPriority("medium");
    } catch (error) {
      console.error(
        "Add Task Error:",
        error.response?.data || error
      );
    }
  };

  const overrideTask = async (taskId) => {
    try {
      const token = localStorage.getItem("access_token");

      await axios.post(
        "http://localhost:8000/api/tasks/",
        {
          task_id: taskId,
          reason: "User decided to proceed",
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      fetchTasks();
    } catch (error) {
      console.error(
        "Override Error:",
        error.response?.data || error
      );

      alert(
        error.response?.data?.error ||
          "Override failed"
      );
    }
  };

  const regulateTasks = async () => {
    try {
      const token = localStorage.getItem("access_token");

      const res = await axios.post(
        "http://localhost:8000/api/tasks/",
        {
          message: "Show me what I can do today",
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log(res.data);

      fetchTasks();
    } catch (error) {
      console.error(
        "Regulate Error:",
        error.response?.data || error
      );
    }
  };

  const deleteTask = async (taskId) => {
  try {
    const token = localStorage.getItem("access_token");

    await axios.delete(
      `http://localhost:8000/api/tasks/${taskId}/`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    fetchTasks(); // refresh UI
  } catch (error) {
    console.error(error.response?.data || error);
  }
};

  return (
    <div className="tasks-root">
      <div className="tasks-wrap">

        <div className="mb-7">
          <h1 className="tasks-title">Task Board</h1>
        </div>

        <div className="add-task-bar">
          <input
            type="text"
            className="add-task-input"
            placeholder="Add a new task..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) =>
              e.key === "Enter" && addTask()
            }
          />

          <select
            value={priority}
            onChange={(e) =>
              setPriority(e.target.value)
            }
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>

          <input
            type="date"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
          />

          <button
            className="btn-add-task"
            onClick={addTask}
          >
            + Add Task
          </button>

          <button onClick={regulateTasks}>
            Regulate Tasks
          </button>
        </div>

        <div className="task-section-divider mb-3">
          <span>✅ Allowed Today</span>
        </div>

        {allowed.map((task) => (
          <div key={task.id} className="task-card">
            <div className="task-card-top">
              <span className="task-card-title">
                {task.name}
              </span>

              <span
                className={`cost-${task.priority}`}
              >
                {task.priority}
              </span>


              <button
  className="btn-delete"
  onClick={() => deleteTask(task.id)}
>
  Delete
</button>
            </div>
            
                {task.deadline && (
      <div className="task-deadline">
        📅 {task.deadline}
      </div>
    )}

          </div>
        ))}

        {postponed.length > 0 && (
          <>
            <div className="task-section-divider mt-6 mb-3">
              <span>
                ⏳ Postponed (score too low)
              </span>

              
            </div>

            {postponed.map((task) => (
              <div
                key={task.id}
                className="task-card postponed"
              >
                <div className="task-card-top">
                  <span className="task-card-title">
                    {task.name}
                  </span>

                  <span
                    className={`cost-${task.priority}`}
                  >
                    {task.priority}
                  </span>
                  
                  

                  <button
                    className="btn-override"
                    onClick={() =>
                      overrideTask(task.id)
                    }
                  >
                    Override
                  </button>
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}