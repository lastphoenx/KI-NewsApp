import { StrictMode, Component, type ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Simple error boundary to surface runtime errors instead of a white screen
class ErrorBoundary extends Component<{ children: ReactNode }, { error: any }> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { error: null }
  }
  static getDerivedStateFromError(error: any) {
    return { error }
  }
  componentDidCatch(error: any, info: any) {
    console.error('React render error:', error, info)
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 24, fontFamily: 'system-ui, sans-serif' }}>
          <h1 style={{ marginBottom: 8 }}>Dashboard error</h1>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{String(this.state.error)}</pre>
          <p style={{ color: '#666' }}>Check the browser console for details.</p>
        </div>
      )
    }
    return this.props.children
  }
}

// Global listener to log uncaught errors
window.addEventListener('error', (e) => {
  console.error('Uncaught error:', e.error || e.message)
})

const rootEl = document.getElementById('root')!
createRoot(rootEl).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
