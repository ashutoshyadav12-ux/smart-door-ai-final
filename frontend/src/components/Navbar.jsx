import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const { logout } = useAuth();
  return (
    <header className="flex items-center justify-between border-b border-slate-800 bg-slate-900 px-5 py-3">
      <div className="flex gap-3 overflow-x-auto md:hidden text-sm">
        {[["/", "Home"], ["/users", "Users"], ["/enroll", "Enroll"], ["/live", "Live"], ["/logs", "Logs"], ["/iot", "IoT"], ["/settings", "Settings"]].map(
          ([to, l]) => (
            <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => (isActive ? "text-indigo-400" : "text-slate-300")}>
              {l}
            </NavLink>
          )
        )}
      </div>
      <div className="hidden text-sm text-slate-400 md:block">Biometric access control</div>
      <button className="btn-ghost" onClick={logout}>Logout</button>
    </header>
  );
}
