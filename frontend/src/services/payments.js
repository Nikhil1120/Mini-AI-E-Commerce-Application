import api from './api'

export async function createCheckoutSession(orderId) {
  const response = await api.post('/payments/create-checkout-session', {
    order_id: orderId || null,
  })
  return response.data
}

export async function verifyPaymentSession(sessionId) {
  const response = await api.get(`/payments/verify-session/${sessionId}`)
  return response.data
}

export async function mockCompletePayment(sessionId) {
  const response = await api.post('/payments/mock-complete', { session_id: sessionId })
  return response.data
}

export async function mockFailPayment(sessionId) {
  const response = await api.post('/payments/mock-fail', { session_id: sessionId })
  return response.data
}

export async function mockCancelPayment(sessionId) {
  const response = await api.post('/payments/mock-cancel', { session_id: sessionId })
  return response.data
}
