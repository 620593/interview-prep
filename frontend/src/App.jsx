import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Dashboard from './pages/TrackerPage'
import Login from './pages/Login'

// Simple frontend-only auth wrapper
function PrivateRoute({ children }) {
  const user = localStorage.getItem('prep_user')
  const location = useLocation()

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return children
}

export default function App() {
  return (
    <div className="font-inter">
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Protected routes */}
        <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
        <Route path="/dashboard/:sessionId" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        
        {/* 404 fallback */}
        <Route path="*" element={
          <div className="flex flex-col items-center justify-center min-h-screen text-center px-4">
            <p className="text-7xl mb-4">🔍</p>
            <h1 className="text-3xl font-bold text-white mb-3">Page Not Found</h1>
            <p className="text-slate-400 mb-8">The page you're looking for doesn't exist.</p>
            <a href="/" className="btn-primary">Go Home</a>
          </div>
        } />
      </Routes>
    </div>
  )
}
