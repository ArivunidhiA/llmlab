import { useState, useEffect } from 'react'
import { auth } from '../api'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const response = await auth.getMe()
        setUser(response.data)
      } catch (error) {
        localStorage.removeItem('access_token')
        setUser(null)
      }
    }
    setLoading(false)
  }

  const signup = async (email: string, password: string, first_name?: string, last_name?: string) => {
    const response = await auth.signup(email, password, first_name, last_name)
    const { access_token } = response.data
    localStorage.setItem('access_token', access_token)
    const userResponse = await auth.getMe()
    setUser(userResponse.data)
    return userResponse.data
  }

  const login = async (email: string, password: string) => {
    const response = await auth.login(email, password)
    const { access_token } = response.data
    localStorage.setItem('access_token', access_token)
    const userResponse = await auth.getMe()
    setUser(userResponse.data)
    return userResponse.data
  }

  const logout = async () => {
    try {
      await auth.logout()
    } catch (error) {
      // Logout anyway if API fails
    }
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return { user, loading, signup, login, logout }
}
