'use client';

import React from 'react';
import { Shield, LayoutDashboard, FileUp, Settings, LogOut } from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass h-16 flex items-center justify-between px-8">
      <div className="flex items-center gap-2">
        <div className="bg-primary/20 p-2 rounded-lg border border-primary/50">
          <Shield className="w-6 h-6 text-primary" />
        </div>
        <Link href="/" className="text-xl font-bold tracking-tight">
          Lumina<span className="text-primary">Shield</span>
        </Link>
      </div>
      
      <div className="flex items-center gap-8">
        <Link href="/" className="flex items-center gap-2 text-sm font-medium hover:text-primary transition-colors">
          <LayoutDashboard className="w-4 h-4" />
          Dashboard
        </Link>
        <Link href="/upload" className="flex items-center gap-2 text-sm font-medium hover:text-primary transition-colors">
          <FileUp className="w-4 h-4" />
          Analizar Proyecto
        </Link>
        <Link href="/settings" className="flex items-center gap-2 text-sm font-medium hover:text-primary transition-colors">
          <Settings className="w-4 h-4" />
          Configuración
        </Link>
      </div>

      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end">
              <span className="text-sm font-semibold">{user.email.split('@')[0]}</span>
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold">Docente</span>
            </div>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold">
              {user.email[0].toUpperCase()}
            </div>
            <button 
              onClick={logout}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors text-muted-foreground hover:text-destructive"
              title="Cerrar sesión"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm font-medium hover:text-primary transition-colors">
              Entrar
            </Link>
            <Link href="/register" className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-bold hover:bg-primary/90 transition-all">
              Registrarse
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
