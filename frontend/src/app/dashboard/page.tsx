'use client';

import React, { useEffect, useState } from 'react';
import { LayoutDashboard, FileCode, Clock, ArrowRight, Search, FileText, Plus, ShieldAlert } from 'lucide-react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

interface ProjectListItem {
  id: number;
  name: string;
  status: string;
  files_count: number;
  created_at: number;
}

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      fetchProjects();
    }
  }, [user]);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/projects');
      setProjects(response.data);
    } catch (err) {
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredProjects = projects.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (authLoading || !user) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-10 px-6">
      {/* Welcome Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between mb-12 gap-6">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight mb-2">
            Panel de <span className="text-gradient">Control</span>
          </h1>
          <p className="text-muted-foreground">Gestiona tus auditorías y análisis de código.</p>
        </div>
        
        <Link href="/upload">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-primary text-white px-8 py-4 rounded-2xl font-bold flex items-center gap-3 shadow-lg shadow-primary/20 hover:bg-blue-600 transition-all"
          >
            <Plus className="w-5 h-5" />
            Nuevo Análisis
          </motion.button>
        </Link>
      </header>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <StatSummaryCard 
          icon={<FileCode className="text-blue-400" />} 
          label="Total Análisis" 
          value={projects.length.toString()} 
        />
        <StatSummaryCard 
          icon={<ShieldAlert className="text-purple-400" />} 
          label="Archivos Revisados" 
          value={projects.reduce((acc, p) => acc + p.files_count, 0).toString()} 
        />
        <StatSummaryCard 
          icon={<Clock className="text-cyan-400" />} 
          label="Última Actividad" 
          value={projects.length > 0 ? "Hoy" : "—"} 
        />
      </div>

      {/* Search & Table */}
      <div className="glass-panel rounded-[2.5rem] overflow-hidden border-white/10 shadow-2xl">
        <div className="p-6 border-b border-white/5 bg-black/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h2 className="text-xl font-bold flex items-center gap-3">
            <LayoutDashboard className="w-5 h-5 text-primary" />
            Historial Reciente
          </h2>
          <div className="relative w-full md:w-80">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Buscar proyecto..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-sm focus:outline-none focus:border-primary/50 transition-all"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="py-20 text-center text-muted-foreground">Cargando proyectos...</div>
          ) : filteredProjects.length > 0 ? (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-white/[0.02] text-xs font-bold uppercase tracking-widest text-muted-foreground">
                  <th className="px-8 py-5">Proyecto</th>
                  <th className="px-8 py-5">Estado</th>
                  <th className="px-8 py-5 text-center">Archivos</th>
                  <th className="px-8 py-5">Fecha</th>
                  <th className="px-8 py-5 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                <AnimatePresence>
                  {filteredProjects.map((project, i) => (
                    <motion.tr 
                      key={project.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="group hover:bg-white/[0.03] transition-colors"
                    >
                      <td className="px-8 py-6">
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                            <FileText className="w-5 h-5" />
                          </div>
                          <div>
                            <p className="font-bold text-white group-hover:text-primary transition-colors">{project.name}</p>
                            <p className="text-xs text-muted-foreground font-mono">ID: {project.id}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-8 py-6">
                        <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase ${
                          project.status === 'completed' 
                            ? 'bg-green-500/10 text-green-400 border border-green-500/20' 
                            : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${project.status === 'completed' ? 'bg-green-400' : 'bg-yellow-400 animate-pulse'}`} />
                          {project.status === 'completed' ? 'Completado' : 'Procesando'}
                        </span>
                      </td>
                      <td className="px-8 py-6 text-center">
                        <span className="font-mono text-sm font-bold">{project.files_count}</span>
                      </td>
                      <td className="px-8 py-6">
                        <span className="text-sm text-muted-foreground">ID #{project.id}</span>
                      </td>
                      <td className="px-8 py-6 text-right">
                        <Link href={`/project/${project.id}`}>
                          <button className="p-3 hover:bg-primary/10 rounded-xl transition-all text-muted-foreground hover:text-primary group/btn">
                            <ArrowRight className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" />
                          </button>
                        </Link>
                      </td>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </tbody>
            </table>
          ) : (
            <div className="py-20 text-center">
              <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-6">
                <Search className="w-10 h-10 opacity-20" />
              </div>
              <p className="text-xl font-bold">No se encontraron proyectos</p>
              <p className="text-muted-foreground mt-2">¿Por qué no empiezas con tu primer análisis?</p>
              <Link href="/upload">
                <button className="mt-8 text-primary font-bold hover:underline">Subir mi primer proyecto</button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatSummaryCard({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) {
  return (
    <div className="glass-panel p-6 rounded-[2rem] border-white/5 relative overflow-hidden group">
      <div className="absolute top-4 right-4 opacity-10 group-hover:scale-125 transition-transform duration-500">
        {icon}
      </div>
      <p className="text-[10px] uppercase tracking-widest text-muted-foreground mb-2">{label}</p>
      <p className="text-3xl font-extrabold">{value}</p>
    </div>
  );
}
