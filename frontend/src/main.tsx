import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Toaster } from 'react-hot-toast'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './core/AuthContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <Toaster position="top-center" />
      <App />
    </AuthProvider>
  </StrictMode>,
)
