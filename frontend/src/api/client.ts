// Thin fetch wrapper. Types come from the frozen contract (docs/openapi.json, ADR-010).
import type { components } from '../types/api'

type Schemas = components['schemas']
export type User = Schemas['UserOut']
export type TokenResponse = Schemas['TokenResponse']
export type ErrorCode = Schemas['ErrorBody']['code'] | 'network'

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  code: ErrorCode
  retryAfter: number | null

  constructor(status: number, code: ErrorCode, message: string, retryAfter: number | null = null) {
    super(message)
    this.status = status
    this.code = code
    this.retryAfter = retryAfter
  }
}

interface Options {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: unknown
  token?: string | null
}

export async function api<T>(path: string, { method = 'GET', body, token }: Options = {}): Promise<T> {
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  let response: Response
  try {
    response = await fetch(BASE_URL + path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, 'network', 'Cannot reach the server. It may be waking up; try again.')
  }

  if (response.status === 204) return undefined as T
  const data: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    const error = (data as Schemas['ErrorResponse'] | null)?.error
    throw new ApiError(
      response.status,
      error?.code ?? 'internal_error',
      error?.message ?? 'Something went wrong.',
      error?.retry_after ?? null,
    )
  }
  return data as T
}
