import React from 'react';
import { Shield, LayoutDashboard, FileUp, Settings } from 'lucide-react';
import Link from 'next/link';

const Navbar = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass h-16 flex items-center justify-between px-8">
      <div className="flex items-center gap-2">
        <div className="bg-primary/20 p-2 rounded-lg border border-primary/50">
          <Shield className="w-6 h-6 text-primary" />
        </div>
        <span className="text-xl font-bold tracking-tight">
          Lumina<span className="text-primary">Shield</span>
        </span>
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
        <div className="flex flex-col items-end">
          <span className="text-sm font-semibold">Prof. García</span>
          <span className="text-xs text-muted-foreground">Administrador</span>
        </div>
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary" />
      </div>
    </nav>
  );
};

export default Navbar;
