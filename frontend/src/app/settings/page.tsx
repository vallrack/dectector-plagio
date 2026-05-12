'use client';

import React from 'react';
import { Settings, Shield, User, Bell, Database, Save } from 'lucide-react';
import { motion } from 'framer-motion';

export default function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto py-10 px-4">
      <div className="mb-10">
        <h1 className="text-4xl font-extrabold tracking-tight mb-2">Configuración</h1>
        <p className="text-muted-foreground">Gestiona tus preferencias de análisis y cuenta</p>
      </div>

      <div className="grid gap-8">
        {/* Perfil */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel p-8 rounded-[2rem] border-white/10"
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-primary/20 rounded-2xl text-primary">
              <User className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold">Perfil de Usuario</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground ml-1">
                Nombre Completo
              </label>
              <input
                type="text"
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-primary/50 transition-all"
                placeholder="Juan Pérez"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground ml-1">
                Institución
              </label>
              <input
                type="text"
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-primary/50 transition-all"
                placeholder="Universidad Nacional"
              />
            </div>
          </div>
        </motion.div>

        {/* Preferencias de Análisis */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-panel p-8 rounded-[2rem] border-white/10"
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-secondary/20 rounded-2xl text-secondary">
              <Shield className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold">Configuración de Análisis</h2>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5">
              <div>
                <h3 className="font-bold">Detección de IA Profunda</h3>
                <p className="text-sm text-muted-foreground">Utiliza múltiples modelos para mayor precisión</p>
              </div>
              <div className="w-12 h-6 bg-primary rounded-full relative">
                <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm" />
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5">
              <div>
                <h3 className="font-bold">Informes PDF Automáticos</h3>
                <p className="text-sm text-muted-foreground">Generar reporte al finalizar el análisis</p>
              </div>
              <div className="w-12 h-6 bg-white/10 rounded-full relative">
                <div className="absolute left-1 top-1 w-4 h-4 bg-white/50 rounded-full shadow-sm" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Botón Guardar */}
        <div className="flex justify-end">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-primary text-primary-foreground px-8 py-4 rounded-2xl font-bold flex items-center gap-2 shadow-xl shadow-primary/20"
          >
            <Save className="w-5 h-5" />
            Guardar Cambios
          </motion.button>
        </div>
      </div>
    </div>
  );
}
