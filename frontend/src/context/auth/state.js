import { useReducer } from 'react'
import * as authService from '../../services/auth'
import Reducer from './reducer'
import { AuthActions } from './actions'

export const initialState = {
  user: JSON.parse(localStorage.getItem('user')) || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
}

export const AuthState = () => {
  const [state, dispatch] = useReducer(Reducer, initialState)

  const login = async (credential) => {
    dispatch({ type: AuthActions.SET_LOADING, payload: true })
    try {
      const data = await authService.googleLogin(credential)
      dispatch({
        type: AuthActions.LOGIN,
        payload: data,
      })
      return data
    } catch (error) {
      dispatch({ type: AuthActions.SET_LOADING, payload: false })
      throw error
    }
  }

  const logout = async () => {
    dispatch({ type: AuthActions.SET_LOADING, payload: true })
    try {
      await authService.logout()
      dispatch({ type: AuthActions.LOGOUT })
    } catch (error) {
      dispatch({ type: AuthActions.SET_LOADING, payload: false })
      throw error
    }
  }

  const checkAuth = async () => {
    try {
      const user = await authService.getCurrentUser()
      if (user) {
        dispatch({
          type: AuthActions.SET_USER,
          payload: user,
        })
      } else {
        dispatch({ type: AuthActions.LOGOUT })
      }
    } catch (error) {
      console.error('Auth check failed:', error)
    }
  }

  return {
    ...state,
    login,
    logout,
    checkAuth,
    dispatch,
  }
}
