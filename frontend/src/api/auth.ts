import { api } from './client'
import type { TokenResponse, User } from './client'

export interface Credentials {
  email: string
  password: string
}

export const register = (body: Credentials) =>
  api<TokenResponse>('/auth/register', { method: 'POST', body })

export const login = (body: Credentials) =>
  api<TokenResponse>('/auth/login', { method: 'POST', body })

export const getMe = (token: string) => api<User>('/me', { token })
