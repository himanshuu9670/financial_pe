import { motion } from 'framer-motion'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GlassCard } from '@/components/ui/GlassCard'
import { toast } from '@/components/ui/Toast'
import { authApi } from '@/services/authApi'
import { useAuthStore } from '@/store/useAuthStore'

export function RegisterPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data: tokens } = await authApi.register(email, password, name || undefined)
      useAuthStore.getState().setTokens(tokens.access_token, tokens.refresh_token)
      const { data: user } = await authApi.me()
      setAuth(user, tokens.access_token, tokens.refresh_token)
      toast('Account created', 'success')
      navigate('/')
    } catch {
      toast('Registration failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-6">
      <GlassCard className="p-8 w-full max-w-md">
        <h1 className="text-xl font-bold mb-6">Create account</h1>
        <form onSubmit={submit} className="space-y-4">
          <input
            placeholder="Full name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-black/30 border border-white/10"
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-black/30 border border-white/10"
            required
          />
          <input
            type="password"
            placeholder="Password (min 8 chars)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-black/30 border border-white/10"
            minLength={8}
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-medium"
          >
            Register
          </button>
        </form>
        <p className="text-xs text-zinc-500 mt-4 text-center">
          <Link to="/login" className="text-indigo-400">
            Sign in
          </Link>
        </p>
      </GlassCard>
    </div>
  )
}
