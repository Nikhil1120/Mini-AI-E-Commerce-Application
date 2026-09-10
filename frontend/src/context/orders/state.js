import { useReducer } from 'react'
import ordersReducer, { initialOrdersState } from './reducer'
import { OrderActions } from './actions'
import * as orderService from '../../services/orders'

export const OrdersState = () => {
  const [state, dispatch] = useReducer(ordersReducer, initialOrdersState)

  const getOrders = async (page = 1, limit = 10) => {
    dispatch({ type: OrderActions.SET_LOADING, payload: true })
    try {
      const data = await orderService.getOrders(page, limit)
      dispatch({ type: OrderActions.SET_ORDERS, payload: data })
      return data
    } catch (error) {
      dispatch({ type: OrderActions.SET_ERROR, payload: error.message })
      throw error
    }
  }

  const getOrder = async (id) => {
    dispatch({ type: OrderActions.SET_LOADING, payload: true })
    try {
      const data = await orderService.getOrder(id)
      dispatch({ type: OrderActions.SET_ORDER, payload: data })
      return data
    } catch (error) {
      dispatch({ type: OrderActions.SET_ERROR, payload: error.message })
      throw error
    }
  }

  const createOrder = async () => {
    dispatch({ type: OrderActions.SET_LOADING, payload: true })
    try {
      const data = await orderService.createOrder()
      dispatch({ type: OrderActions.ADD_ORDER, payload: data })
      return data
    } catch (error) {
      dispatch({ type: OrderActions.SET_ERROR, payload: error.message })
      throw error
    }
  }

  const updateOrderStatus = async (id, status) => {
    dispatch({ type: OrderActions.SET_LOADING, payload: true })
    try {
      const data = await orderService.updateOrderStatus(id, status)
      dispatch({ type: OrderActions.UPDATE_ORDER, payload: data })
      return data
    } catch (error) {
      dispatch({ type: OrderActions.SET_ERROR, payload: error.message })
      throw error
    }
  }

  return {
    ...state,
    getOrders,
    getOrder,
    createOrder,
    updateOrderStatus,
    dispatch,
  }
}
