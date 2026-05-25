export interface AuthUser {
  id: string
  email: string
  full_name: string | null
  role: string
  is_active: boolean
  is_superuser: boolean
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}
