'use client';

import React from 'react';
import { ArrowRight, BarChart3, FileSearch, ShieldAlert, Zap, Lock, Code2 } from 'lucide-react';
import Link from 'next/link';
import { motion, Variants } from 'framer-motion';

const container: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15
    }
  }
};

const item: Variants = {
  hidden: { opacity: 0, y: 30 },
  show: { 
    opacity: 1, 
    y: 0, 
    transition: { 
      type: "spring" as const, 
      stiffness: 300, 
      damping: 24 
    } 
  }
};

export default function Home() {

  return (
    <div className="relative min-h-[calc(100vh-6rem)] flex flex-col justify-center overflow-hidden">
      {/* Background glowing orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px] -z-10 animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/20 rounded-full blur-[120px] -z-10 animate-pulse delay-1000" />
      
      <div className="max-w-7xl mx-auto py-20 px-6 w-full">
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center mb-24 relative z-10"
        >
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 border-primary/30"
          >
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium tracking-wide">Ahora integrado con Copyleaks AI</span>
          </motion.div>
          
          <h1 className="text-6xl md:text-8xl font-extrabold mb-8 tracking-tighter leading-[1.1]">
            Detecta la <span className="text-gradient">Firma de la IA</span> <br className="hidden md:block" /> en Segundos
          </h1>
          
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed mb-12">
            El sistema de protección académica más avanzado. Analiza más de 90 lenguajes, PDFs, Word y Excel para garantizar la total originalidad.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
            <Link href="/upload">
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-white text-black hover:bg-gray-100 px-10 py-5 rounded-2xl font-bold flex items-center gap-3 transition-colors shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] text-lg"
              >
                Comenzar Análisis
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="glass px-10 py-5 rounded-2xl font-bold hover:bg-white/10 transition-colors text-lg"
            >
              Documentación
            </motion.button>
          </div>
        </motion.div>

        <motion.div 
          variants={container as any}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          <motion.div variants={item as any}>
            <FeatureCard 
              icon={<FileSearch className="w-8 h-8 text-blue-400" />}
              title="Copyleaks Integration"
              description="Potenciado por la API comercial líder para detectar rastros de GPT-4, Claude y Gemini con precisión milimétrica."
            />
          </motion.div>
          <motion.div variants={item as any}>
            <FeatureCard 
              icon={<Code2 className="w-8 h-8 text-purple-400" />}
              title="Multiformato y +90 Lenguajes"
              description="Sube archivos ZIP con proyectos enteros, o documentos individuales como Word, PDF y Excel. Lo leemos todo."
            />
          </motion.div>
          <motion.div variants={item as any}>
            <FeatureCard 
              icon={<Lock className="w-8 h-8 text-cyan-400" />}
              title="Privacidad Extrema"
              description="Tus documentos se analizan en memoria y jamás se utilizan para entrenar otros modelos de IA."
            />
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="glass-panel p-10 rounded-3xl h-full group hover:glow-primary transition-all duration-500 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      <div className="bg-white/5 w-16 h-16 rounded-2xl flex items-center justify-center mb-8 group-hover:scale-110 group-hover:bg-primary/20 transition-all duration-300">
        {icon}
      </div>
      <h3 className="text-2xl font-bold mb-4 tracking-tight">{title}</h3>
      <p className="text-muted-foreground leading-relaxed text-lg">
        {description}
      </p>
    </div>
  );
}
