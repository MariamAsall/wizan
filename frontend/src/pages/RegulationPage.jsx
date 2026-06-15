import { useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import "./RegulationPage.css";
import { useNavigate } from "react-router-dom";

export default function RegulationPage() {
  const { state } = useLocation();

const navigate = useNavigate();

  const [allowed, setAllowed] = useState([]);
  const [postponed, setPostponed] = useState([]);

  const [showOverrideModal, setShowOverrideModal] =
  useState(false);

const [selectedTaskId, setSelectedTaskId] =
  useState(null);


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



const handleOverrideClick = (taskId) => {
  setSelectedTaskId(taskId);
  setShowOverrideModal(true);
};
const confirmOverride = async () => {
  if (!selectedTaskId) return;

  try {
    const token =
      localStorage.getItem("access_token");

    await axios.post(
      "http://localhost:8000/api/tasks/override/",
      {
        task_id: selectedTaskId,
        reason: "User decided to proceed",
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    setShowOverrideModal(false);
    setSelectedTaskId(null);

    fetchTasks();
  } catch (error) {
  console.error(error.response?.data || error);

  setShowOverrideModal(false);
  setSelectedTaskId(null);

  alert(
    error.response?.data?.error ||
    "Override failed"
  );
}
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
  onClick={() =>
    handleOverrideClick(task.id)
  }
>
  Override
</button>
    </div>
    
  </div>
))}
{showOverrideModal && (
  <div  className="modal-overlay"
  onClick={() => {
    setShowOverrideModal(false);
    setSelectedTaskId(null);
  }}>
   <div
  className="override-modal"
  onClick={(e) => e.stopPropagation()}
>

      <div className="warning-icon">
        ⚠️
      </div>

      <h2>Override Recommendation?</h2>

      <p>
        This task was postponed because your
        cognitive load may be high.
      </p>

     <p className="warning-text">
  Your cognitive load is already high today.
  Completing this task may be more difficult than usual.
  Are you sure you want to continue?
</p>
      <div className="modal-buttons">
        <button
          className="btn-cancel"
          onClick={() => {
            setShowOverrideModal(false);
            setSelectedTaskId(null);
          }}
        >
          Cancel
        </button>

        <button
          className="btn-confirm"
          onClick={confirmOverride}
        >
          Override Anyway
        </button>
      </div>
    </div>
  </div>
)}

<button
  className="btn-back"
  onClick={() => navigate("/tasks")}
>
  ← Back to Tasks
</button>
    </div>
  );
}