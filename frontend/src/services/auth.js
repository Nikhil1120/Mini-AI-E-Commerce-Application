import api from './api'

export async function googleLogin(credential) {
  const response = await api.post('/auth/google', { credential })
  const data = response.data

  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('user', JSON.stringify(data.user))

  return data
}

export async function devLogin(email) {
  const response = await api.post('/auth/dev-login', { email })
  const data = response.data

  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('user', JSON.stringify(data.user))

  return data
}

export async function getCurrentUser() {
  try {
    const response = await api.get('/auth/me')
    const user = response.data
    localStorage.setItem('user', JSON.stringify(user))
    return user
  } catch (error) {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    return null
  }
}

export async function logout() {
  try {
    await api.post('/auth/logout')
  } catch (error) {
    console.log('Logout error:', error)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }
}
