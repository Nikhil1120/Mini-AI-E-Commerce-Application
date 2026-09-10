import api from './api'

export async function getOrders(page = 1, limit = 10) {
  const response = await api.get('/orders', {
    params: { page, limit }
  })
  return response.data
}

export async function getOrder(id) {
  const response = await api.get(`/orders/${id}`)
  return response.data
}

export async function createOrder() {
  const response = await api.post('/orders')
  return response.data
}

export async function updateOrderItemQuantity(orderId, itemId, quantity) {
  const response = await api.put(`/orders/${orderId}/items/${itemId}`, { quantity })
  return response.data
}

export async function removeOrder(orderId) {
  const response = await api.delete(`/orders/${orderId}`)
  return response.data
}

// Admin
export async function getAllOrders(page = 1, limit = 10, statusFilter = '') {
  const response = await api.get('/admin/orders', {
    params: { page, limit, status_filter: statusFilter }
  })
  return response.data
}

export async function updateOrderStatus(id, status, paymentStatus = null) {
  const response = await api.put(`/admin/orders/${id}/status`, {
    status,
    payment_status: paymentStatus
  })
  return response.data
}
