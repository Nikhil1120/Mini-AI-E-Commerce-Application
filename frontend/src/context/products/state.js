import { useReducer } from 'react'
import productsReducer, { initialProductsState } from './reducer'
import { ProductActions } from './actions'
import * as productService from '../../services/products'

export const ProductsState = () => {
  const [state, dispatch] = useReducer(productsReducer, initialProductsState)

  const getProducts = async (page = 1, limit = 10, search = '', category = '') => {
    dispatch({ type: ProductActions.SET_LOADING, payload: true })
    try {
      const data = await productService.getProducts(page, limit, search, category)
      dispatch({ type: ProductActions.SET_PRODUCTS, payload: data })
      return data
    } catch (error) {
      dispatch({ type: ProductActions.SET_ERROR, payload: error.message })
      throw error
    }
  }

  const getProduct = async (id) => {
    dispatch({ type: ProductActions.SET_LOADING, payload: true })
    try {
      const data = await productService.getProduct(id)
      dispatch({ type: ProductActions.SET_PRODUCT, payload: data })
      return data
    } catch (error) {
      dispatch({ type: ProductActions.SET_ERROR, payload: error.message })
      throw error
    }
  }

  const createProduct = async (productData) => {
    dispatch({ type: ProductActions.SET_LOADING, payload: true })
    try {
      const data = await productService.createProduct(productData)
      dispatch({ type: ProductActions.ADD_PRODUCT, payload: data })
      return data
    } catch (error) {
      dispatch({ type: ProductActions.SET_ERROR, payload: error.message })
      throw error
    }
  }

  const updateProduct = async (id, productData) => {
    dispatch({ type: ProductActions.SET_LOADING, payload: true })
    try {
      const data = await productService.updateProduct(id, productData)
      dispatch({ type: ProductActions.UPDATE_PRODUCT, payload: data })
      return data
    } catch (error) {
      dispatch({ type: ProductActions.SET_ERROR, payload: error.message })
      throw error
    }
  }

  const deleteProduct = async (id) => {
    dispatch({ type: ProductActions.SET_LOADING, payload: true })
    try {
      await productService.deleteProduct(id)
      dispatch({ type: ProductActions.DELETE_PRODUCT, payload: id })
    } catch (error) {
      dispatch({ type: ProductActions.SET_ERROR, payload: error.message })
      throw error
    }
  }

  return {
    ...state,
    getProducts,
    getProduct,
    createProduct,
    updateProduct,
    deleteProduct,
    dispatch,
  }
}
