import { ProductActions } from './actions'

export const initialProductsState = {
  products: [],
  currentProduct: null,
  isLoading: false,
  error: null,
  pagination: {
    page: 1,
    limit: 10,
    total: 0,
  },
}

const productsReducer = (state, action) => {
  switch (action.type) {
    case ProductActions.SET_PRODUCTS:
      return {
        ...state,
        products: action.payload.items || action.payload,
        pagination: action.payload.pagination || state.pagination,
        isLoading: false,
        error: null,
      }
    case ProductActions.SET_PRODUCT:
      return {
        ...state,
        currentProduct: action.payload,
        isLoading: false,
      }
    case ProductActions.ADD_PRODUCT:
      return {
        ...state,
        products: [action.payload, ...state.products],
      }
    case ProductActions.UPDATE_PRODUCT:
      return {
        ...state,
        products: state.products.map((p) =>
          p.id === action.payload.id ? action.payload : p
        ),
        currentProduct:
          state.currentProduct?.id === action.payload.id
            ? action.payload
            : state.currentProduct,
      }
    case ProductActions.DELETE_PRODUCT:
      return {
        ...state,
        products: state.products.filter((p) => p.id !== action.payload),
      }
    case ProductActions.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      }
    case ProductActions.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      }
    case ProductActions.RESET:
      return initialProductsState
    default:
      return state
  }
}

export default productsReducer
