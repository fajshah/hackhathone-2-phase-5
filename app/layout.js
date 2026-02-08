import './globals.css';

export const metadata = {
  title: 'Todo AI Assistant',
  description: 'A modern chat interface for managing your todos',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
