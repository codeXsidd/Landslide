import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import RiskDetails from './pages/RiskDetails';
import Evidence from './pages/Evidence';
import Verification from './pages/Verification';
import Impact from './pages/Impact';
import Simulation from './pages/Simulation';
import Decisions from './pages/Decisions';
import Audit from './pages/Audit';
import Demo from './pages/Demo';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="risk" element={<RiskDetails />} />
          <Route path="evidence" element={<Evidence />} />
          <Route path="verification" element={<Verification />} />
          <Route path="impact" element={<Impact />} />
          <Route path="simulation" element={<Simulation />} />
          <Route path="decisions" element={<Decisions />} />
          <Route path="audit" element={<Audit />} />
          <Route path="demo" element={<Demo />} />
        </Route>
      </Routes>
    </Router>
  );
}
