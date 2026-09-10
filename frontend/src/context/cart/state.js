import { useReducer } from 'react'
import * as cartService from '../../services/cart'
import Reducer from './reducer'
import { CartActions } from './actions'

export const initialState = {
  cart: null,
  isLoading: false,
}

export const CartState = () => {
  const [state, dispatch] = useReducer(Reducer, initialState)

  const fetchCart = async () => {
    dispatch({ type: CartActions.SET_LOADING, payload: true })
    try {
      const cart = await cartService.getCart()
      dispatch({
        type: CartActions.SET_CART,
        payload: cart,
      })
      return cart
    } catch (error) {
      dispatch({ type: CartActions.SET_LOADING, payload: false })
      throw error
    }
  }

  const addToCart = async (productId, quantity) => {
    dispatch({ type: CartActions.SET_LOADING, payload: true })
    try {
      await cartService.addToCart(productId, quantity)
      const cart = await cartService.getCart()
      dispatch({
        type: CartActions.ADD_TO_CART,
        payload: cart,
      })
      return cart
    } catch (error) {
      dispatch({ type: CartActions.SET_LOADING, payload: false })
      throw error
    }
  }

  const updateCartItem = async (itemId, quantity) => {
    dispatch({ type: CartActions.SET_LOADING, payload: true })
    try {
      await cartService.updateCartItem(itemId, quantity)
      const cart = await cartService.getCart()
      dispatch({
        type: CartActions.UPDATE_CART_ITEM,
        payload: cart,
      })
      return cart
    } catch (error) {
      dispatch({ type: CartActions.SET_LOADING, payload: false })
      throw error
    }
  }

  const removeFromCart = async (itemId) => {
    dispatch({ type: CartActions.SET_LOADING, payload: true })
    try {
      await cartService.removeFromCart(itemId)
      const cart = await cartService.getCart()
      dispatch({
        type: CartActions.REMOVE_FROM_CART,
        payload: cart,
      })
      return cart
    } catch (error) {
      dispatch({ type: CartActions.SET_LOADING, payload: false })
      throw error
    }
  }

  const clearCart = async () => {
    dispatch({ type: CartActions.SET_LOADING, payload: true })
    try {
      await cartService.clearCart()
      const cart = await cartService.getCart()
      dispatch({
        type: CartActions.CLEAR_CART,
        payload: cart,
      })
      return cart
    } catch (error) {
      dispatch({ type: CartActions.SET_LOADING, payload: false })
      throw error
    }
  }

  return {
    ...state,
    fetchCart,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    dispatch,
  }
}
