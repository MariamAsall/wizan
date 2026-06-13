import { useState, useEffect } from "react";
import axios from "axios";
import "./Tasks.css";

export default function TasksPage() {
  const [input, setInput] = useState("");
  const [priority, setPriority] = useState("medium");
  const [deadline, setDeadline] = useState("")

  const [allowed, setAllowed] = useState([]);
  const [postponed, setPostponed] = useState([]);

  const [sessionId, setSessionId] = useState(
  localStorage.getItem("task_session_id"));

  const [editingTask, setEditingTask] = useState(null);
const [editName, setEditName] = useState("");
const [editPriority, setEditPriority] = useState("medium");
const [editDeadline, setEditDeadline] = useState("");

const [agentResponse, setAgentResponse] = useState("");




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

    const today = new Date().toISOString().split("T")[0];


  const addTask = async () => {
    if (!input.trim()) return;


    const today = new Date().toISOString().split("T")[0];

    if (deadline && deadline < today) {
    alert("Deadline cannot be in the past");
    return;
    }


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
console.log("OVERRIDE CLICKED", taskId);
    const res = await axios.post(
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

    console.log(res.data);

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
  "http://localhost:8000/api/tasks/regulate/",
  {
    message: "Show me what I can do today",
    session_id: sessionId,
  },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
setAgentResponse(res.data.response);

      console.log(res.data);
      if (res.data.session_id) {
  setSessionId(res.data.session_id);

  localStorage.setItem(
    "task_session_id",
    res.data.session_id
  );
}

      fetchTasks();
    } catch (error) {
      console.error(
        "Regulate Error:",
        error.response?.data || error
      );
    }
  };

const updateTask = async () => {
  try {
    const token = localStorage.getItem("access_token");

    await axios.patch(
      `http://localhost:8000/api/tasks/${editingTask}/`,
      {
        name: editName,
        priority: editPriority,
        deadline: editDeadline || null,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    setEditingTask(null);
    fetchTasks();
  } catch (error) {
    console.error(error.response?.data || error);
  }
};


  

const deleteTask = async (taskId) => {

  const confirmed = window.confirm(
    "Are you sure you want to delete this task?"
  );

  if (!confirmed) return;

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

    fetchTasks();

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

             <input type="date" value={deadline} min={today}
            onChange={(e) => setDeadline(e.target.value)}/>

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
                {task.status === "overridden" && (
    <span className="override-badge">
      Override
    </span>
  )}

              <span
                className={`cost-${task.priority} `}
              >
                {task.priority}
              </span>

                <button
                  className="btn-edit"
                  onClick={() => {
                    setEditingTask(task.id);
                    setEditName(task.name);
                    setEditPriority(task.priority);
                    setEditDeadline(task.deadline || "");
                  }}
                >
                  Edit
                </button>


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
{editingTask && (
  <div className="modal-overlay">
    <div className="edit-modal">

      <h2>Edit Task</h2>

      <input
        type="text"
        value={editName}
        onChange={(e) => setEditName(e.target.value)}
        placeholder="Task name"
      />

      <select
        value={editPriority}
        onChange={(e) => setEditPriority(e.target.value)}
      >
        <option value="low">Low Priority</option>
        <option value="medium">Medium Priority</option>
        <option value="high">High Priority</option>
      </select>

      <input
        type="date"
        value={editDeadline}
        min={today}
        onChange={(e) => setEditDeadline(e.target.value)}
      />

      <div className="modal-actions">
        <button
          className="btn-save"
          onClick={updateTask}
        >
          Save Changes
        </button>

        <button
          className="btn-cancel"
          onClick={() => setEditingTask(null)}
        >
          Cancel
        </button>
      </div>

    </div>
  </div>
)}

{agentResponse && (
  <div className="agent-response">
    {agentResponse}
  </div>
)}


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