'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { getApiUrl } from '@/lib/config';
import axios from 'axios';
import Link from 'next/link';
import { Shield, Lock, Mail, Loader2, UserPlus } from 'lucide-react';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      await axios.post(getApiUrl('/auth/register'), { email, password });
      router.push('/login?registered=true');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al registrarse');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <div className="w-full max-w-md p-8 glass rounded-2xl border border-white/10 shadow-2xl">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-secondary/20 p-3 rounded-xl mb-4">
            <UserPlus className="w-8 h-8 text-secondary" />
          </div>
          <h1 className="text-2xl font-bold">Crea tu cuenta</h1>
          <p className="text-muted-foreground text-sm mt-1">Únete a la red de detección LuminaShield</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Mail className="w-4 h-4 text-secondary" /> Correo Electrónico
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-background/50 border border-white/10 rounded-xl px-4 py-3 outline-none focus:ring-2 ring-secondary/50 transition-all"
              placeholder="tu@escuela.com"
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Lock className="w-4 h-4 text-secondary" /> Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-background/50 border border-white/10 rounded-xl px-4 py-3 outline-none focus:ring-2 ring-secondary/50 transition-all"
              placeholder="••••••••"
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2">
              <Lock className="w-4 h-4 text-secondary" /> Confirmar Contraseña
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full bg-background/50 border border-white/10 rounded-xl px-4 py-3 outline-none focus:ring-2 ring-secondary/50 transition-all"
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
            className="w-full bg-secondary hover:bg-secondary/90 text-secondary-foreground font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Registrarse'}
          </button>
        </form>

        <p className="text-center mt-6 text-sm text-muted-foreground">
          ¿Ya tienes una cuenta?{' '}
          <Link href="/login" className="text-secondary hover:underline font-semibold">
            Inicia sesión aquí
          </Link>
        </p>
      </div>
    </div>
  );
}
