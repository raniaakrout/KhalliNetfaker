'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { authAPI } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import Link from 'next/link';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const router = useRouter();
  const { setToken, setUser, token } = useAuthStore();

  // Redirect already-authenticated users away from /auth
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (token || storedToken) {
      router.replace('/chat');
    }
  }, [token, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const response = await authAPI.login(email, password);
        const { access_token, user_id, username, email: userEmail } = response.data;
        // setUser first — triggers clearAll() if a different user was previously logged in
        setUser({ user_id, username, email: userEmail });
        // setToken stores in Zustand + localStorage (for Axios Bearer interceptor)
        setToken(access_token);
        router.push('/chat');
      } else {
        const response = await authAPI.register(email, username, password);
        setUser(response.data);
        setIsLogin(true);
        setEmail('');
        setUsername('');
        setPassword('');
        setError('Registration successful! Please log in.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-slate-800 rounded-lg shadow-2xl p-8 border border-slate-700">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 mb-4">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">KhalliNetfaker</h1>
            <p className="text-slate-400 text-sm">Meeting Intelligence Agent</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-slate-300 text-sm font-medium mb-2">
                  Username
                </label>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="your username"
                  className="w-full bg-slate-700 border-slate-600 text-white placeholder-slate-500 focus:border-cyan-500"
                  required={!isLogin}
                />
              </div>
            )}

            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Email
              </label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full bg-slate-700 border-slate-600 text-white placeholder-slate-500 focus:border-cyan-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Password
              </label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-700 border-slate-600 text-white placeholder-slate-500 focus:border-cyan-500"
                required
              />
            </div>

            {error && (
              <div className={`p-3 rounded-lg text-sm ${
                error.includes('successful')
                  ? 'bg-green-900 text-green-200 border border-green-700'
                  : 'bg-red-900 text-red-200 border border-red-700'
              }`}>
                {error}
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold py-2 rounded-lg transition-all disabled:opacity-50"
            >
              {loading ? 'Loading...' : isLogin ? 'Sign In' : 'Sign Up'}
            </Button>
          </form>

          {/* Toggle */}
          <div className="mt-6 text-center">
            <p className="text-slate-400 text-sm">
              {isLogin ? 'No account? ' : 'Already have an account? '}
              <button
                type="button"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                }}
                className="text-cyan-400 hover:text-cyan-300 font-semibold transition-colors"
              >
                {isLogin ? 'Sign Up' : 'Sign In'}
              </button>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-slate-500 text-sm">
          <p>Meeting Intelligence Agent</p>
        </div>
      </div>
    </div>
  );
}
