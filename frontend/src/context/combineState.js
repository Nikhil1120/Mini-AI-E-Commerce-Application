import { useMemo } from 'react'
import { AuthState } from './auth/state'
import { CartState } from './cart/state'
import { ProductsState } from './products/state'
import { OrdersState } from './orders/state'

const useCombineState = () => {
  const Auth = AuthState()
  const Cart = CartState()
  const Products = ProductsState()
  const Orders = OrdersState()

  return useMemo(
    () => ({
      Auth,
      Cart,
      Products,
      Orders,
    }),
    [Auth, Cart, Products, Orders]
  )
}

export default useCombineState
