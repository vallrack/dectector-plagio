'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import Link from 'next/link';
import { Shield, Lock, Mail, Loader2, UserPlus, Eye, EyeOff, Check, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [strength, setStrength] = useState(0);
  const router = useRouter();

  // Strength calculator
  useEffect(() => {
    let s = 0;
    if (password.length > 5) s += 20;
    if (password.length > 8) s += 20;
    if (/[A-Z]/.test(password)) s += 20;
    if (/[0-9]/.test(password)) s += 20;
    if (/[^A-Za-z0-9]/.test(password)) s += 20;
    setStrength(s);
  }, [password]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      await api.post('/auth/register', { email, password });
      router.push('/login?registered=true');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al registrarse');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-8rem)] px-4 py-10">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg"
      >
        <div className="text-center mb-10">
          <motion.div 
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            className="inline-flex p-4 rounded-3xl bg-gradient-to-br from-secondary/20 to-primary/20 border border-white/10 mb-6"
          >
            <UserPlus className="w-10 h-10 text-secondary" />
          </motion.div>
          <h1 className="text-4xl font-extrabold tracking-tight mb-2">Nueva Cuenta</h1>
          <p className="text-muted-foreground">Únete a la red forense de LuminaShield</p>
        </div>

        <div className="glass-panel p-8 md:p-12 rounded-[3rem] border-white/10 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground ml-1">
                Correo Electrónico
              </label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-focus-within:text-secondary transition-colors" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-4 py-4 outline-none focus:border-secondary/50 focus:bg-white/10 transition-all text-lg"
                  placeholder="profe@institucion.edu"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground ml-1">
                Contraseña Segura
              </label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-focus-within:text-secondary transition-colors" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-12 py-4 outline-none focus:border-secondary/50 focus:bg-white/10 transition-all text-lg"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              
              {/* Password Strength Bar */}
              <div className="px-1 pt-2">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] uppercase font-bold text-muted-foreground">Seguridad</span>
                  <span className="text-[10px] font-bold text-secondary">{strength}%</span>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${strength}%` }}
                    className={cn(
                      "h-full rounded-full transition-colors duration-500",
                      strength < 40 ? "bg-red-500" : strength < 80 ? "bg-yellow-500" : "bg-green-500"
                    )}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground ml-1">
                Confirmar Contraseña
              </label>
              <div className="relative group">
                <Check className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-focus-within:text-secondary transition-colors" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-4 py-4 outline-none focus:border-secondary/50 focus:bg-white/10 transition-all text-lg"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-red-500/10 border border-red-500/20 text-red-400 text-xs p-4 rounded-2xl flex items-center gap-3"
                >
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  {error}
                </motion.div>
              )}
            </AnimatePresence>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isLoading}
              className="w-full bg-secondary text-secondary-foreground font-extrabold py-5 rounded-2xl transition-all flex items-center justify-center gap-3 shadow-xl hover:shadow-secondary/10 disabled:opacity-50 text-lg"
            >
              {isLoading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <>
                  Crear Mi Cuenta
                  <UserPlus className="w-5 h-5" />
                </>
              )}
            </motion.button>
          </form>
        </div>

        <p className="text-center mt-10 text-muted-foreground">
          ¿Ya eres parte de la red?{' '}
          <Link href="/login" className="text-white hover:text-secondary underline underline-offset-4 transition-colors font-bold">
            Inicia sesión aquí
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
