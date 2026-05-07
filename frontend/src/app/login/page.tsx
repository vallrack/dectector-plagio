'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { getApiUrl } from '@/lib/config';
import axios from 'axios';
import Link from 'next/link';
import { Shield, Lock, Mail, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.post(getApiUrl('/auth/login'), { email, password });
      login(response.data.access_token, response.data.user);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <div className="w-full max-w-md p-8 glass rounded-2xl border border-white/10 shadow-2xl">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-primary/20 p-3 rounded-xl mb-4">
            <Shield className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold">Bienvenido de nuevo</h1>
          <p className="text-muted-foreground text-sm mt-1">Ingresa tus credenciales para continuar</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Mail className="w-4 h-4 text-primary" /> Correo Electrónico
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-background/50 border border-white/10 rounded-xl px-4 py-3 outline-none focus:ring-2 ring-primary/50 transition-all"
              placeholder="tu@escuela.com"
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Lock className="w-4 h-4 text-primary" /> Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-background/50 border border-white/10 rounded-xl px-4 py-3 outline-none focus:ring-2 ring-primary/50 transition-all"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div className="bg-destructive/10 border border-destructive/20 text-destructive text-sm p-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Iniciar Sesión'}
          </button>
        </form>

        <p className="text-center mt-6 text-sm text-muted-foreground">
          ¿No tienes una cuenta?{' '}
          <Link href="/register" className="text-primary hover:underline font-semibold">
            Regístrate aquí
          </Link>
        </p>
      </div>
    </div>
  );
}
