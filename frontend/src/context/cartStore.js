import { create } from 'zustand'
import * as cartService from '../services/cart'

export const useCartStore = create((set, get) => ({
  cart: null,
  isLoading: false,

  setCart: (cart) => set({ cart }),
  setIsLoading: (isLoading) => set({ isLoading }),

  fetchCart: async () => {
    set({ isLoading: true })
    try {
      const cart = await cartService.getCart()
      set({ cart, isLoading: false })
      return cart
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  addToCart: async (productId, quantity) => {
    set({ isLoading: true })
    try {
      await cartService.addToCart(productId, quantity)
      const cart = await cartService.getCart()
      set({ cart, isLoading: false })
      return cart
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  updateCartItem: async (itemId, quantity) => {
    set({ isLoading: true })
    try {
      await cartService.updateCartItem(itemId, quantity)
      const cart = await cartService.getCart()
      set({ cart, isLoading: false })
      return cart
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  removeFromCart: async (itemId) => {
    set({ isLoading: true })
    try {
      await cartService.removeFromCart(itemId)
      const cart = await cartService.getCart()
      set({ cart, isLoading: false })
      return cart
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  clearCart: async () => {
    set({ isLoading: true })
    try {
      await cartService.clearCart()
      const cart = await cartService.getCart()
      set({ cart, isLoading: false })
      return cart
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  }
}))
