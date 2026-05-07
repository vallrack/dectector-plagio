'use client';

import React, { useState } from 'react';
import { Shield, LayoutDashboard, FileUp, Settings, LogOut, Menu, X } from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';

const Navbar = () => {
  const { user, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinks = [
    { href: '/', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { href: '/upload', label: 'Analizar Proyecto', icon: <FileUp className="w-4 h-4" /> },
    { href: '/settings', label: 'Configuración', icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 glass h-16 flex items-center justify-between px-4 md:px-8">
        <div className="flex items-center gap-2">
          <div className="bg-primary/20 p-2 rounded-lg border border-primary/50">
            <Shield className="w-6 h-6 text-primary" />
          </div>
          <Link href="/" className="text-xl font-bold tracking-tight">
            Lumina<span className="text-primary">Shield</span>
          </Link>
        </div>
        
        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link key={link.href} href={link.href} className="flex items-center gap-2 text-sm font-medium hover:text-primary transition-colors">
              {link.icon}
              {link.label}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-2 md:gap-4">
          {user ? (
            <div className="flex items-center gap-3 md:gap-4">
              <div className="hidden sm:flex flex-col items-end">
                <span className="text-sm font-semibold">{user.email.split('@')[0]}</span>
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold">Docente</span>
              </div>
              <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold text-sm md:text-base">
                {user.email[0].toUpperCase()}
              </div>
              <button 
                onClick={logout}
                className="hidden md:block p-2 hover:bg-white/10 rounded-lg transition-colors text-muted-foreground hover:text-destructive"
                title="Cerrar sesión"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="hidden md:flex items-center gap-3">
              <Link href="/login" className="text-sm font-medium hover:text-primary transition-colors">
                Entrar
              </Link>
              <Link href="/register" className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-bold hover:bg-primary/90 transition-all">
                Registrarse
              </Link>
            </div>
          )}

          {/* Mobile Menu Toggle */}
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-0 z-40 bg-background/95 backdrop-blur-xl md:hidden pt-20 px-6"
          >
            <div className="flex flex-col gap-6">
              {navLinks.map((link) => (
                <Link 
                  key={link.href} 
                  href={link.href} 
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="flex items-center gap-4 text-xl font-bold p-4 rounded-2xl bg-white/5 border border-white/10"
                >
                  <div className="p-3 bg-primary/10 rounded-xl text-primary">
                    {React.cloneElement(link.icon as React.ReactElement, { className: "w-6 h-6" })}
                  </div>
                  {link.label}
                </Link>
              ))}
              
              <div className="h-px bg-white/10 my-2" />
              
              {user ? (
                <button 
                  onClick={() => {
                    logout();
                    setIsMobileMenuOpen(false);
                  }}
                  className="flex items-center gap-4 text-xl font-bold p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500"
                >
                  <div className="p-3 bg-red-500/10 rounded-xl">
                    <LogOut className="w-6 h-6" />
                  </div>
                  Cerrar Sesión
                </button>
              ) : (
                <div className="flex flex-col gap-4">
                  <Link 
                    href="/login" 
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center justify-center py-4 rounded-2xl border border-white/10 font-bold"
                  >
                    Iniciar Sesión
                  </Link>
                  <Link 
                    href="/register" 
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center justify-center py-4 rounded-2xl bg-primary text-white font-bold"
                  >
                    Registrarse
                  </Link>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Navbar;
