import { motion } from 'framer-motion'
import { Loader2, Lock } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GlassCard } from '@/components/ui/GlassCard'
import { toast } from '@/components/ui/Toast'
import { authApi } from '@/services/authApi'
import { useAuthStore } from '@/store/useAuthStore'

export function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [email, setEmail] = useState('demo@pdfeditor.local')
  const [password, setPassword] = useState('demo-password-change-me')
  const [loading, setLoading] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data: tokens } = await authApi.login(email, password)
      useAuthStore.getState().setTokens(tokens.access_token, tokens.refresh_token)
      const { data: user } = await authApi.me()
      setAuth(user, tokens.access_token, tokens.refresh_token)
      toast('Welcome back', 'success')
      navigate('/')
    } catch {
      toast('Invalid credentials', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-6">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <GlassCard className="p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-lg bg-indigo-500/20">
              <Lock className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Sign in</h1>
              <p className="text-sm text-zinc-500">Enterprise secure access</p>
            </div>
          </div>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="text-xs text-zinc-500">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-black/30 border border-white/10"
                required
              />
            </div>
            <div>
              <label className="text-xs text-zinc-500">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-black/30 border border-white/10"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-medium disabled:opacity-50 flex justify-center gap-2"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              Sign in
            </button>
          </form>
          <p className="text-xs text-zinc-500 mt-4 text-center">
            No account?{' '}
            <Link to="/register" className="text-indigo-400 hover:text-indigo-300">
              Register
            </Link>
          </p>
        </GlassCard>
      </motion.div>
    </div>
  )
}
