import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { ThemeProvider } from 'next-themes'
import { useAuth } from '../lib/hooks/useAuth'
import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'

function MyApp({ Component, pageProps }: AppProps) {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    setIsReady(true)
  }, [])

  // Redirect unauthenticated users
  useEffect(() => {
    if (isReady && !loading) {
      const publicPages = ['/', '/login', '/signup']
      const isPublic = publicPages.includes(router.pathname)
      
      if (!user && !isPublic) {
        router.push('/login')
      } else if (user && (router.pathname === '/login' || router.pathname === '/signup')) {
        router.push('/dashboard')
      }
    }
  }, [user, loading, isReady, router])

  if (!isReady || (loading && !['/','login', '/signup'].includes(router.pathname))) {
    return <LoadingScreen />
  }

  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      <Component {...pageProps} />
    </ThemeProvider>
  )
}

function LoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-900 to-purple-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p className="text-white text-lg">Loading LLMlab...</p>
      </div>
    </div>
  )
}

export default MyApp
