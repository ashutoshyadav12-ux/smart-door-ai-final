import { NavLink } from "react-router-dom";

const LINKS = [
  ["/", "Dashboard", "📊"],
  ["/users", "Users", "👥"],
  ["/enroll", "Face Enrollment", "📸"],
  ["/live", "Live Recognition", "🎥"],
  ["/logs", "Access Logs", "📜"],
  ["/iot", "IoT Devices", "📡"],
  ["/settings", "Settings", "⚙️"],
];

export default function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 border-r border-slate-800 bg-slate-900 p-4 md:block">
      <div className="mb-6 text-lg font-bold">🚪 Smart Door AI</div>
      <nav className="space-y-1">
        {LINKS.map(([to, label, icon]) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm ${isActive ? "bg-indigo-600 text-white" : "text-slate-300 hover:bg-slate-800"}`
            }
          >
            <span>{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
