import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { api, clearSession, getStoredUser, setSession } from "./api";
import "./styles.css";

const statuses = ["To Do", "In Progress", "Review", "Done"];
const priorities = ["Low", "Medium", "High", "Urgent"];
const iconMap = {
  alert: "!",
  chart: "B",
  projects: "P",
  clock: "D",
  done: "C",
  tasks: "T",
  logout: "L",
  plus: "+",
  shield: "S",
  spark: "*",
  users: "U",
};

function Icon({ name, size = 18 }) {
  return <span className="icon" style={{ width: size, height: size, fontSize: Math.max(11, size * 0.58) }}>{iconMap[name]}</span>;
}

function AuthScreen({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const path = mode === "login" ? "/auth/login" : "/auth/signup";
      const payload = mode === "login" ? { email: form.email, password: form.password } : form;
      const data = await api(path, { method: "POST", body: JSON.stringify(payload) });
      setSession(data);
      onAuth(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-hero">
        <div className="brand-lockup">
          <div className="brand-mark"><Icon name="tasks" size={28} /></div>
          <span>TaskFlow</span>
        </div>
        <h1>Organize project delivery with clarity, ownership, and momentum.</h1>
        <p>
          A role-aware workspace for teams to plan projects, assign work, monitor overdue tasks,
          and keep leadership aligned from one command center.
        </p>
        <div className="hero-metrics">
          <div><strong>RBAC</strong><span>Admin and Member access</span></div>
          <div><strong>Live</strong><span>Project and task progress</span></div>
          <div><strong>API</strong><span>FastAPI Swagger-ready backend</span></div>
        </div>
      </section>

      <section className="auth-card">
        <div className="switcher">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
          <button className={mode === "signup" ? "active" : ""} onClick={() => setMode("signup")}>Signup</button>
        </div>
        <h2>{mode === "login" ? "Welcome back" : "Create your workspace account"}</h2>
        <form onSubmit={submit} className="form">
          {mode === "signup" && (
            <label>
              Full name
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required minLength={2} />
            </label>
          )}
          <label>
            Email
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          </label>
          <label>
            Password
            <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={6} />
          </label>
          {error && <p className="error"><Icon name="alert" size={16} />{error}</p>}
          <button className="primary" disabled={loading}>{loading ? "Please wait..." : mode === "login" ? "Login" : "Create account"}</button>
          <p className="hint">The first registered user automatically becomes Admin.</p>
        </form>
      </section>
    </main>
  );
}

function StatCard({ icon, label, value, tone }) {
  return (
    <article className={`stat ${tone || ""}`}>
      <Icon name={icon} size={22} />
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function App() {
  const [user, setUser] = useState(getStoredUser());
  const [dashboard, setDashboard] = useState(null);
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [projectForm, setProjectForm] = useState({ name: "", description: "", member_ids: [] });
  const [taskForm, setTaskForm] = useState({
    title: "",
    description: "",
    project_id: "",
    assignee_id: "",
    priority: "Medium",
    due_date: new Date().toISOString().slice(0, 10),
  });

  const isAdmin = user?.role === "Admin";

  async function loadData() {
    if (!user) return;
    setError("");
    try {
      const [dash, projectList, taskList, userList] = await Promise.all([
        api("/dashboard"),
        api("/projects"),
        api("/tasks"),
        api("/users"),
      ]);
      setDashboard(dash);
      setProjects(projectList);
      setTasks(taskList);
      setUsers(userList);
      if (!taskForm.project_id && projectList[0]) {
        setTaskForm((prev) => ({ ...prev, project_id: projectList[0].id, assignee_id: projectList[0].members[0] || "" }));
      }
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadData();
  }, [user]);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === taskForm.project_id),
    [projects, taskForm.project_id],
  );

  const projectMembers = useMemo(() => {
    if (!selectedProject) return users;
    return users.filter((member) => selectedProject.members.includes(member.id));
  }, [selectedProject, users]);

  async function createProject(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await api("/projects", { method: "POST", body: JSON.stringify(projectForm) });
      setProjectForm({ name: "", description: "", member_ids: [] });
      await loadData();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function createTask(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await api("/tasks", { method: "POST", body: JSON.stringify(taskForm) });
      setTaskForm({ ...taskForm, title: "", description: "" });
      await loadData();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function updateTaskStatus(task, status) {
    try {
      await api(`/tasks/${task.id}`, { method: "PATCH", body: JSON.stringify({ status }) });
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  function logout() {
    clearSession();
    setUser(null);
  }

  if (!user) return <AuthScreen onAuth={setUser} />;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup compact">
          <div className="brand-mark"><Icon name="tasks" size={23} /></div>
          <span>TaskFlow</span>
        </div>
        <nav>
          <a href="#dashboard"><Icon name="chart" size={18} />Dashboard</a>
          <a href="#projects"><Icon name="projects" size={18} />Projects</a>
          <a href="#tasks"><Icon name="done" size={18} />Tasks</a>
          <a href="#team"><Icon name="users" size={18} />Team</a>
        </nav>
        <button className="ghost" onClick={logout}><Icon name="logout" size={18} />Logout</button>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Corporate workspace</p>
            <h1>Good to see you, {user.name.split(" ")[0]}</h1>
          </div>
          <div className="user-chip"><Icon name="shield" size={16} />{user.role}</div>
        </header>

        {error && <p className="notice"><Icon name="alert" size={16} />{error}</p>}

        <section id="dashboard" className="stats-grid">
          <StatCard icon="projects" label="Projects" value={dashboard?.total_projects ?? 0} />
          <StatCard icon="tasks" label="Total tasks" value={dashboard?.total_tasks ?? 0} />
          <StatCard icon="done" label="Completed" value={dashboard?.completed_tasks ?? 0} tone="green" />
          <StatCard icon="clock" label="Overdue" value={dashboard?.overdue_tasks ?? 0} tone="red" />
        </section>

        <section className="content-grid">
          <div className="panel" id="projects">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Portfolio</p>
                <h2>Projects</h2>
              </div>
              <Icon name="projects" />
            </div>
            {isAdmin && (
              <form className="form inline" onSubmit={createProject}>
                <input placeholder="Project name" value={projectForm.name} onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })} required />
                <textarea placeholder="Project objective" value={projectForm.description} onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })} required />
                <select multiple value={projectForm.member_ids} onChange={(e) => setProjectForm({ ...projectForm, member_ids: Array.from(e.target.selectedOptions, (option) => option.value) })}>
                  {users.map((member) => <option key={member.id} value={member.id}>{member.name} - {member.role}</option>)}
                </select>
                <button className="primary" disabled={busy}><Icon name="plus" size={17} />Add project</button>
              </form>
            )}
            <div className="project-list">
              {projects.map((project) => (
                <article className="project-card" key={project.id}>
                  <h3>{project.name}</h3>
                  <p>{project.description}</p>
                  <div className="progress-line"><span style={{ width: `${project.task_count ? (project.completed_count / project.task_count) * 100 : 0}%` }} /></div>
                  <small>{project.completed_count}/{project.task_count} tasks complete</small>
                </article>
              ))}
              {!projects.length && <p className="empty">No projects yet. Admins can create the first project here.</p>}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Execution</p>
                <h2>Create task</h2>
              </div>
              <Icon name="spark" />
            </div>
            <form className="form" onSubmit={createTask}>
              <input placeholder="Task title" value={taskForm.title} onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })} required />
              <textarea placeholder="Task details" value={taskForm.description} onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })} required />
              <select value={taskForm.project_id} onChange={(e) => setTaskForm({ ...taskForm, project_id: e.target.value })} required>
                <option value="">Select project</option>
                {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
              </select>
              <select value={taskForm.assignee_id} onChange={(e) => setTaskForm({ ...taskForm, assignee_id: e.target.value })} required>
                <option value="">Assign to</option>
                {projectMembers.map((member) => <option key={member.id} value={member.id}>{member.name}</option>)}
              </select>
              <div className="two-col">
                <select value={taskForm.priority} onChange={(e) => setTaskForm({ ...taskForm, priority: e.target.value })}>
                  {priorities.map((priority) => <option key={priority}>{priority}</option>)}
                </select>
                <input type="date" value={taskForm.due_date} onChange={(e) => setTaskForm({ ...taskForm, due_date: e.target.value })} />
              </div>
              <button className="primary" disabled={busy}><Icon name="plus" size={17} />Create task</button>
            </form>
          </div>
        </section>

        <section className="panel wide" id="tasks">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Delivery board</p>
              <h2>Tasks</h2>
            </div>
            <Icon name="tasks" />
          </div>
          <div className="kanban">
            {statuses.map((status) => (
              <div className="lane" key={status}>
                <h3>{status}<span>{tasks.filter((task) => task.status === status).length}</span></h3>
                {tasks.filter((task) => task.status === status).map((task) => (
                  <article className={`task-card ${task.overdue ? "overdue" : ""}`} key={task.id}>
                    <div className="task-top">
                      <strong>{task.title}</strong>
                      <span className={`priority ${task.priority.toLowerCase()}`}>{task.priority}</span>
                    </div>
                    <p>{task.description}</p>
                    <small>{task.project_name} · {task.assignee_name} · due {task.due_date}</small>
                    <select value={task.status} onChange={(e) => updateTaskStatus(task, e.target.value)}>
                      {statuses.map((item) => <option key={item}>{item}</option>)}
                    </select>
                  </article>
                ))}
              </div>
            ))}
          </div>
        </section>

        <section className="panel wide" id="team">
          <div className="panel-header">
            <div>
              <p className="eyebrow">People</p>
              <h2>Team directory</h2>
            </div>
            <Icon name="users" />
          </div>
          <div className="team-grid">
            {users.map((member) => (
              <article className="member-card" key={member.id}>
                <div className="avatar">{member.name.slice(0, 1).toUpperCase()}</div>
                <div><strong>{member.name}</strong><span>{member.email}</span></div>
                <em>{member.role}</em>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
