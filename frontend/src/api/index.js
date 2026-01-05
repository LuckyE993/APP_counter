import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

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
