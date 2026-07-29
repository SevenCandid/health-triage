import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/index.css'
import App from './app/App.tsx'
import { connectivityService } from './services/ConnectivityService'

// Initialize network listeners and sync when online
connectivityService.init()
// Trigger initial download of offline knowledge base (if online)
connectivityService.syncKnowledgeBase()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
