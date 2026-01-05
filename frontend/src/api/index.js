import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// Token管理
const getToken = () => localStorage.getItem('token')
const setToken = (token) => localStorage.setItem('token', token)
const removeToken = () => localStorage.removeItem('token')

// 请求拦截器：自动添加token
api.interceptors.request.use(config => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理401错误
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      removeToken()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const login = async (username, password) => {
  const response = await api.post('/login', { username, password })
  setToken(response.data.access_token)
  return response.data
}

export const logout = () => {
  removeToken()
  window.location.href = '/login'
}

export const isAuthenticated = () => !!getToken()

export const parseImage = async (imageBase64) => {
  const response = await api.post('/parse/image', {
    image: imageBase64
  })
  return response.data
}

export const parseText = async (text) => {
  const response = await api.post('/parse/text', {
    text
  })
  return response.data
}

export const saveTransaction = async (transaction) => {
  const response = await api.post('/transaction', transaction)
  return response.data
}

export const getBalance = async () => {
  const response = await api.get('/balance')
  return response.data
}

export const getAccounts = async () => {
  const response = await api.get('/accounts')
  return response.data
}

export const getAccountConfig = async () => {
  const response = await api.get('/config/accounts')
  return response.data
}

export const startFava = async () => {
  const response = await api.post('/fava/start')
  return response.data
}

export const stopFava = async () => {
  const response = await api.post('/fava/stop')
  return response.data
}

export const getFavaStatus = async () => {
  const response = await api.get('/fava/status')
  return response.data
}
