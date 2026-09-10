import { initialState } from './state'

const authHandler = {
  LOGIN: (state, action) => ({
    ...state,
    user: action.payload.user,
    isAuthenticated: true,
    isLoading: false,
  }),
  LOGOUT: (state, action) => ({
    ...state,
    user: null,
    isAuthenticated: false,
    isLoading: false,
  }),
  SET_LOADING: (state, action) => ({
    ...state,
    isLoading: action.payload,
  }),
  SET_USER: (state, action) => ({
    ...state,
    user: action.payload,
  }),
  RESET: (state, action) => initialState,
}

const Reducer = (state, action) => {
  const handler = authHandler[action.type]
  return handler ? handler(state, action) : state
}

export default Reducer
