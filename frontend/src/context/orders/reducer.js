import { OrderActions } from './actions'

export const initialOrdersState = {
  orders: [],
  currentOrder: null,
  isLoading: false,
  error: null,
  pagination: {
    page: 1,
    limit: 10,
    total: 0,
  },
}

const ordersReducer = (state, action) => {
  switch (action.type) {
    case OrderActions.SET_ORDERS:
      return {
        ...state,
        orders: action.payload.items || action.payload,
        pagination: action.payload.pagination || state.pagination,
        isLoading: false,
        error: null,
      }
    case OrderActions.SET_ORDER:
      return {
        ...state,
        currentOrder: action.payload,
        isLoading: false,
      }
    case OrderActions.ADD_ORDER:
      return {
        ...state,
        orders: [action.payload, ...state.orders],
      }
    case OrderActions.UPDATE_ORDER:
      return {
        ...state,
        orders: state.orders.map((o) =>
          o.id === action.payload.id ? action.payload : o
        ),
        currentOrder:
          state.currentOrder?.id === action.payload.id
            ? action.payload
            : state.currentOrder,
      }
    case OrderActions.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      }
    case OrderActions.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      }
    case OrderActions.RESET:
      return initialOrdersState
    default:
      return state
  }
}

export default ordersReducer
