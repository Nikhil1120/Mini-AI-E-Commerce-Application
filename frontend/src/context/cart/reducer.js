import { initialState } from './state'

const cartHandler = {
  SET_CART: (state, action) => ({
    ...state,
    cart: action.payload,
    isLoading: false,
  }),
  ADD_TO_CART: (state, action) => ({
    ...state,
    cart: action.payload,
    isLoading: false,
  }),
  UPDATE_CART_ITEM: (state, action) => ({
    ...state,
    cart: action.payload,
    isLoading: false,
  }),
  REMOVE_FROM_CART: (state, action) => ({
    ...state,
    cart: action.payload,
    isLoading: false,
  }),
  CLEAR_CART: (state, action) => ({
    ...state,
    cart: action.payload,
    isLoading: false,
  }),
  SET_LOADING: (state, action) => ({
    ...state,
    isLoading: action.payload,
  }),
  RESET: (state, action) => initialState,
}

const Reducer = (state, action) => {
  const handler = cartHandler[action.type]
  return handler ? handler(state, action) : state
}

export default Reducer
