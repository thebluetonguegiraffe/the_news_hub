'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';


export default function LoginPage() {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (password === process.env.NEXT_PUBLIC_AUTH_PASSWORD) {
      // Set cookie
      document.cookie = 'authenticated=true; path=/; max-age=86400'; // 24h
      router.push('/');
      router.refresh();
    } else {
      setError('Incorrect password');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            The News Hub
          </h1>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-secondary/20 rounded-full">
            <span className="text-sm text-muted-foreground">🔒 Restricted Access</span>
          </div>
        </div>

        <div className="bg-card rounded-lg shadow-lg p-8 border border-border">
          <h2 className="text-2xl font-semibold text-card-foreground mb-6">
            Sign In
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-card-foreground mb-2"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-background border border-input rounded-lg 
                         text-foreground placeholder:text-muted-foreground
                         focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent
                         transition-all"
                placeholder="Enter your password"
                disabled={loading}
                required
              />
            </div>

            {error && (
              <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground 
                       font-medium py-3 px-4 rounded-lg transition-colors
                       disabled:opacity-50 disabled:cursor-not-allowed
                       shadow-sm hover:shadow-md"
            >
              {loading ? 'Authenticating...' : 'Enter'}
            </button>
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            Enter credentials to access the platform
          </p>
        </div>
      </div>
    </div>
  );
}