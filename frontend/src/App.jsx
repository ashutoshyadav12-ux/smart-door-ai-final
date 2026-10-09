import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Sidebar from "./components/Sidebar.jsx";
import { useAuth } from "./context/AuthContext.jsx";
import AccessLogs from "./pages/AccessLogs.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import FaceEnrollment from "./pages/FaceEnrollment.jsx";
import IoTDevices from "./pages/IoTDevices.jsx";
import LiveRecognition from "./pages/LiveRecognition.jsx";
import Login from "./pages/Login.jsx";
import Settings from "./pages/Settings.jsx";
import Users from "./pages/Users.jsx";

function Layout() {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />
        <main className="flex-1 p-5"><Outlet /></main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/users" element={<Users />} />
        <Route path="/enroll" element={<FaceEnrollment />} />
        <Route path="/live" element={<LiveRecognition />} />
        <Route path="/logs" element={<AccessLogs />} />
        <Route path="/iot" element={<IoTDevices />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
