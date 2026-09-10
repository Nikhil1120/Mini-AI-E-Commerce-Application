import api from './api'

export async function getProducts(page = 1, limit = 10, search = '', category = '') {
  const response = await api.get('/products', {
    params: { page, limit, search, category },
  })
  return response.data
}

export async function getProduct(id) {
  const response = await api.get(`/products/${id}`)
  return response.data
}

export async function searchProducts(query) {
  return getProducts(1, 20, query)
}

export async function createProduct(productData) {
  const response = await api.post('/admin/products', productData)
  return response.data
}

export async function updateProduct(id, productData) {
  const response = await api.put(`/admin/products/${id}`, productData)
  return response.data
}

export async function deleteProduct(id) {
  const response = await api.delete(`/admin/products/${id}`)
  return response.data
}

export async function updateProductStock(id, stockQuantity) {
  const response = await api.put(`/admin/products/${id}/stock`, {
    stock_quantity: stockQuantity,
  })
  return response.data
}
