import { useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import "./RegulationPage.css";

export default function RegulationPage() {
  const { state } = useLocation();

  const [allowed, setAllowed] = useState([]);
  const [postponed, setPostponed] = useState([]);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
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
        (t) =>
          t.status === "allowed" ||
          t.status === "overridden"
      )
    );

    setPostponed(
      tasks.filter(
        (t) => t.status === "postponed"
      )
    );
  };

const overrideTask = async (taskId) => {
  try {
    const token = localStorage.getItem("access_token");

    await axios.post(
      "http://localhost:8000/api/tasks/override/",
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
      error.response?.data || error
    );

    alert(
      error.response?.data?.error ||
      "Override failed"
    );
  }
};

const handleOverride = (taskId) => {
  const confirmed = window.confirm(
    "⚠️ This task was postponed because your cognitive load may be too high.\n\nIt might be too much for you today and could affect your productivity.\n\nAre you sure you want to continue?"
  );

  if (!confirmed) return;

  overrideTask(taskId);
};



  return (
    <div className="regulation-page">

      <h1>Today's Regulation</h1>

      {state?.message && (
        <div className="agent-message">
          🤖 {state.message}
        </div>
      )}

      {state?.plan && (
        <div className="plan-card">
          <h3>Today's Plan</h3>

          <p>
            Estimated Time:
            {state.plan.estimated_time} min
          </p>

          {state.plan.steps.map(
            (step, index) => (
              <div key={index}>
                ✅ {step}
              </div>
            )
          )}
        </div>
      )}

      <h2>✅ Allowed Tasks</h2>

      {allowed.map((task) => (
        <div className="task-card" key={task.id}>
          <h3>{task.name}</h3>

          <span className="status allowed">
            {task.status}
          </span>
        </div>
      ))}

      <h2>⏳ Postponed Tasks</h2>

      {postponed.map((task) => (
  <div
    className="task-card postponed"
    key={task.id}
  >
    <h3>{task.name}</h3>

    <div className="task-actions">
      <span className="status postponed">
        Postponed
      </span>

        <button
        className="btn-override"
        onClick={() => handleOverride(task.id)}
        >
        Override
        </button>
    </div>
  </div>
))}
    </div>
  );
}