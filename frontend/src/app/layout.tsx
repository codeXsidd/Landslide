import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'NER-SAGE | Intelligence Platform',
  description: 'Self-Adaptive Geospatial Emergency Intelligence',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div style={{ display: 'flex', minHeight: '100vh' }}>
          {/* Sidebar */}
          <aside style={{
            width: '80px',
            borderRight: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            padding: '2rem 0',
            background: 'var(--bg-panel)'
          }}>
            <div className="title-gradient" style={{ fontWeight: 800, fontSize: '1.5rem', marginBottom: '3rem' }}>
              N
            </div>
            {/* Mock Navigation Icons */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', opacity: 0.6 }}>
              <div style={{ width: '24px', height: '24px', background: 'var(--accent-cyan)', borderRadius: '4px' }}></div>
              <div style={{ width: '24px', height: '24px', background: 'var(--text-secondary)', borderRadius: '4px' }}></div>
              <div style={{ width: '24px', height: '24px', background: 'var(--text-secondary)', borderRadius: '4px' }}></div>
            </div>
          </aside>
          
          {/* Main Content Area */}
          <main style={{ flex: 1, padding: '2rem', height: '100vh', overflowY: 'auto' }}>
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
