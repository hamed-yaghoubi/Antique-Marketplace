export interface User {
  id: number
  username: string
  role: 'user' | 'admin' | 'owner'
  is_active: boolean
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token?: string
  token_type: string
}

export interface RegisterRequest {
  username: string
  password: string
  confirm_password: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
  confirm_password: string
}
