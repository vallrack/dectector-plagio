'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';
import {
  FileCode,
  Search,
  BarChart,
  ExternalLink,
  AlertCircle,
  FileText,
  ShieldCheck,
  Cpu,
  Brain,
  Gauge,
  Fingerprint,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import Semaphore from '@/components/Semaphore';
import CodeViewer from '@/components/CodeViewer';
import { motion, AnimatePresence } from 'framer-motion';
import { getApiUrl } from '@/lib/config';

// ─── Types ────────────────────────────────────────────────────────────────────

interface CodeFile {
  id: number;
  filename: string;
  language: string;
  ai_score: number;
  entropy: number;
  is_ai_generated: boolean;
  detected_model: string;
  detected_brand: string | null;
  detected_version: string | null;
  attribution_confidence: number;
  brand_color: string | null;
  analysis_engine: string;
  content: string;
}

interface Project {
  id: number;
  name: string;
  status: string;
  files_count: number;
  files: CodeFile[];
}

// ─── Brand badge ──────────────────────────────────────────────────────────────

function BrandBadge({ file }: { file: CodeFile }) {
  const brand  = file.detected_brand;
  const version = file.detected_version;
  const confidence = file.attribution_confidence ?? 0;
  const color  = file.brand_color ?? '#6B7280';

  // If no brand detected show a "human" badge
  if (!brand || file.ai_score < 40) {
    return (
      <div className="flex flex-col gap-2">
        <div
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-bold border"
          style={{ borderColor: '#22C55E33', backgroundColor: '#22C55E11', color: '#22C55E' }}
        >
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          Probable Humano
        </div>
        <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Confianza: —</span>
      </div>
    );
  }

  const ring = confidence >= 70 ? 'ring-2' : confidence >= 40 ? 'ring-1' : '';

  return (
    <div className="flex flex-col gap-1">
      {/* Brand pill */}
      <div
        className={cn('inline-flex items-center gap-2 px-3 py-1 rounded-lg text-[11px] font-bold border', ring)}
        style={{
          borderColor: color + '55',
          backgroundColor: color + '18',
          color: color,
          boxShadow: ring ? `0 0 0 ${ring === 'ring-2' ? '2px' : '1px'} ${color}` : undefined,
        }}
      >
        <span
          className="w-1.5 h-1.5 rounded-full animate-pulse"
          style={{ backgroundColor: color }}
        />
        {brand}
      </div>

      {/* Version chip */}
      {version && (
        <div
          className="inline-flex items-center gap-1 px-1.5 py-0 rounded-md text-[9px] font-semibold border self-start"
          style={{ borderColor: color + '33', color: color + 'CC', backgroundColor: color + '0C' }}
        >
          {version}
        </div>
      )}

      {/* Confidence bar */}
      <div className="flex items-center gap-2 mt-0.5">
        <div className="flex-1 h-1 bg-black/30 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${confidence}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className="h-full rounded-full"
            style={{ backgroundColor: color }}
          />
        </div>
        <span className="text-[9px] font-mono text-muted-foreground shrink-0">
          {confidence.toFixed(0)}%
        </span>
      </div>
    </div>
  );
}

// ─── Stat card ────────────────────────────────────────────────────────────────

function StatCard({
  icon,
  label,
  children,
  className,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('bg-black/20 p-5 rounded-2xl border border-white/5 relative overflow-hidden group', className)}>
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <div className="w-12 h-12">{icon}</div>
      </div>
      <p className="text-[10px] uppercase tracking-widest text-muted-foreground mb-3">{label}</p>
      {children}
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function ProjectDetailPage() {
  const params = useParams();
  const [project, setProject]           = useState<Project | null>(null);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<CodeFile | null>(null);
  const [searchTerm, setSearchTerm]     = useState('');

  const fetchProject = async () => {
    try {
      const response = await axios.get(getApiUrl(`project/${params.id}`));
      setProject(response.data);
      if (response.data.files?.length > 0 && !selectedFile) {
        setSelectedFile(response.data.files[0]);
      }
    } catch (err) {
      console.error(err);
      setError('No se pudo cargar el proyecto. Verifica la conexión con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProject();
    let interval: NodeJS.Timeout;
    if (!project || project.status !== 'completed' || project.files.length === 0) {
      interval = setInterval(() => fetchProject(), 2000);
    }
    return () => { if (interval) clearInterval(interval); };
  }, [params.id, project?.status, project?.files.length]);

  // ── Loading ────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh]">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
          className="relative w-20 h-20 mb-8"
        >
          <div className="absolute inset-0 rounded-full border-t-2 border-primary border-r-2 border-r-transparent" />
          <div className="absolute inset-2 rounded-full border-l-2 border-secondary border-b-2 border-b-transparent animate-reverse-spin" />
        </motion.div>
        <p className="text-xl font-medium text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary animate-pulse">
          Analizando firmas de IA en profundidad...
        </p>
      </div>
    );
  }

  // ── Error ──────────────────────────────────────────────────────────────────
  if (error || !project) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-2xl mx-auto py-32 text-center"
      >
        <div className="w-24 h-24 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-8">
          <AlertCircle className="w-12 h-12 text-red-500" />
        </div>
        <h1 className="text-4xl font-bold mb-4">Error al Cargar</h1>
        <p className="text-muted-foreground text-lg mb-10">{error || 'El proyecto no existe.'}</p>
        <button
          onClick={() => window.location.reload()}
          className="bg-primary hover:bg-blue-600 transition-colors px-10 py-4 rounded-2xl font-bold text-white shadow-lg shadow-primary/20"
        >
          Reintentar Conexión
        </button>
      </motion.div>
    );
  }

  const averageScore  = project.files.reduce((acc, f) => acc + f.ai_score, 0) / (project.files.length || 1);
  const filteredFiles = project.files.filter(f => f.filename.toLowerCase().includes(searchTerm.toLowerCase()));

  const handleDownloadReport = async () => {
    const url  = getApiUrl(`project/${params.id}/report`);
    const link = document.createElement('a');
    link.href  = url;
    link.setAttribute('download', `reporte_ia_${params.id}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-[1600px] mx-auto py-6 px-4 md:px-8">

      {/* ── Header ── */}
      <header className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-6">
        <div>
          <div className="flex items-center gap-4 mb-3">
            <h1 className="text-4xl font-extrabold tracking-tight">{project.name}</h1>
            <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-md text-xs font-mono text-muted-foreground">
              ID: {project.id}
            </span>
          </div>
          <div className="flex items-center gap-8 text-sm font-medium">
            <span className="flex items-center gap-2 text-muted-foreground">
              <FileCode className="w-4 h-4 text-blue-400" />
              {project.files_count} documentos
            </span>
            <span className="flex items-center gap-2 text-muted-foreground">
              <BarChart className="w-4 h-4 text-purple-400" />
              Score Promedio: <strong className="text-foreground">{averageScore.toFixed(1)}% IA</strong>
            </span>
            <span className="flex items-center gap-2 text-green-400 bg-green-400/10 px-3 py-1 rounded-full">
              <ShieldCheck className="w-4 h-4" />
              Análisis Completado
            </span>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleDownloadReport}
            className="glass-panel px-6 py-3 rounded-2xl text-sm font-bold flex items-center gap-2 hover:bg-white/10 transition-all text-white"
          >
            <FileText className="w-4 h-4" />
            Exportar Informe PDF
          </motion.button>
          <div className="glass p-2 rounded-2xl flex items-center gap-4 border-white/10">
            <span className="text-xs font-bold uppercase tracking-widest pl-3 text-muted-foreground">Riesgo Global</span>
            <Semaphore score={averageScore} size="lg" />
          </div>
        </div>
      </header>

      {/* ── Layout ── */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 h-[calc(100vh-180px)]">

        {/* ── Sidebar ── */}
        <div className="md:col-span-4 lg:col-span-3 glass-panel rounded-3xl flex flex-col overflow-hidden">
          <div className="p-5 border-b border-white/5 bg-black/20">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Buscar archivo..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-sm focus:outline-none focus:border-primary/50 transition-colors placeholder:text-muted-foreground/50"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
            <AnimatePresence>
              {filteredFiles.map((file, i) => (
                <motion.button
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  key={file.id}
                  onClick={() => setSelectedFile(file)}
                  className={cn(
                    'w-full flex flex-col p-4 rounded-2xl transition-all duration-300 relative overflow-hidden group',
                    selectedFile?.id === file.id
                      ? 'bg-primary/10 border border-primary/30 shadow-[inset_0_0_20px_rgba(59,130,246,0.1)]'
                      : 'bg-transparent border border-transparent hover:bg-white/5'
                  )}
                >
                  <div className="flex items-center justify-between w-full mb-2">
                    <div className="flex items-center gap-3 overflow-hidden">
                      <div className={cn(
                        'w-8 h-8 shrink-0 rounded-lg flex items-center justify-center font-bold text-[10px] uppercase shadow-inner',
                        file.ai_score > 70 ? 'bg-red-500/20 text-red-400 border border-red-500/20' :
                        file.ai_score > 30 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/20' :
                        'bg-green-500/20 text-green-400 border border-green-500/20'
                      )}>
                        {file.language.substring(0, 3)}
                      </div>
                      <p className="text-sm font-medium truncate text-left">{file.filename}</p>
                    </div>
                    <div className={cn(
                      'px-2 py-1 rounded-md text-[10px] font-bold shrink-0 ml-2',
                      file.ai_score > 70 ? 'text-red-400 bg-red-500/10' :
                      file.ai_score > 30 ? 'text-yellow-400 bg-yellow-500/10' :
                      'text-green-400 bg-green-500/10'
                    )}>
                      {file.ai_score}%
                    </div>
                  </div>

                  {/* Mini brand label */}
                  {file.detected_brand && file.ai_score >= 40 && (
                    <p
                      className="text-[10px] font-semibold truncate text-left mt-0.5 mb-1"
                      style={{ color: file.brand_color ?? '#6B7280' }}
                    >
                      {file.detected_brand}
                      {file.detected_version ? ` — ${file.detected_version}` : ''}
                    </p>
                  )}

                  {/* Mini progress bar */}
                  <div className="w-full h-1 bg-black/40 rounded-full overflow-hidden mt-1">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${file.ai_score}%` }}
                      transition={{ duration: 1 }}
                      className={cn(
                        'h-full',
                        file.ai_score > 70 ? 'bg-red-500' :
                        file.ai_score > 30 ? 'bg-yellow-500' :
                        'bg-green-500'
                      )}
                    />
                  </div>
                </motion.button>
              ))}
            </AnimatePresence>
            {filteredFiles.length === 0 && (
              <p className="text-center text-muted-foreground text-sm mt-10">No se encontraron archivos</p>
            )}
          </div>
        </div>

        {/* ── Main detail panel ── */}
        <div className="md:col-span-8 lg:col-span-9 flex flex-col h-full">
          <AnimatePresence mode="wait">
            {selectedFile ? (
              <motion.div
                key={selectedFile.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="glass-panel rounded-3xl p-6 md:p-8 flex flex-col h-full overflow-hidden"
              >
                {/* File header */}
                <div className="flex items-start justify-between mb-8">
                  <div>
                    <h2 className="text-2xl font-bold mb-2 break-all">{selectedFile.filename}</h2>
                    <div className="flex items-center gap-3">
                      <span className="px-3 py-1 bg-white/5 rounded-md text-xs font-mono text-muted-foreground uppercase border border-white/5">
                        {selectedFile.language}
                      </span>
                      <button className="text-primary text-sm flex items-center gap-1 hover:text-blue-400 transition-colors">
                        <ExternalLink className="w-3 h-3" /> Pantalla Completa
                      </button>
                    </div>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-[10px] uppercase tracking-widest text-muted-foreground mb-2">Veredicto IA</span>
                    <Semaphore score={selectedFile.ai_score} size="md" />
                  </div>
                </div>

                {/* Stat cards row */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-4 shrink-0">

                  {/* Score */}
                  <StatCard icon={<BarChart />} label="Score Confianza">
                    <p className="text-2xl font-mono font-bold text-white">
                      {selectedFile.ai_score}
                      <span className="text-sm text-muted-foreground ml-1">%</span>
                    </p>
                  </StatCard>

                  {/* Brand Attribution (NEW INTEGRATED POSITION) */}
                  <div className="bg-black/20 p-4 rounded-2xl border border-white/5 relative overflow-hidden group">
                    <p className="text-[10px] uppercase tracking-widest text-muted-foreground mb-2 flex items-center gap-2">
                      <Brain className="w-3 h-3" /> IA Detectada
                    </p>
                    <BrandBadge file={selectedFile} />
                  </div>

                  {/* Entropy */}
                  <StatCard icon={<Gauge className="text-purple-400" />} label="Entropía">
                    <p className="text-2xl font-mono font-bold text-purple-300">
                      {selectedFile.entropy.toFixed(2)}
                    </p>
                    <p className="text-[9px] text-muted-foreground mt-1 truncate">
                      {selectedFile.entropy < 4.4 ? '↓ IA' : selectedFile.entropy < 5.2 ? '↘ Sospechoso' : '↑ Humano'}
                    </p>
                  </StatCard>

                  {/* Verdict */}
                  <div className={cn(
                    'p-4 rounded-2xl border relative overflow-hidden flex flex-col justify-center',
                    selectedFile.is_ai_generated ? 'bg-red-500/10 border-red-500/20' : 'bg-green-500/10 border-green-500/20'
                  )}>
                    <p className="text-[9px] uppercase tracking-widest mb-1 opacity-70">Evaluación</p>
                    <p className={cn(
                      'text-lg font-extrabold leading-tight',
                      selectedFile.is_ai_generated ? 'text-red-400' : 'text-green-400'
                    )}>
                      {selectedFile.is_ai_generated ? 'Sintético' : 'Humano'}
                    </p>
                  </div>

                  {/* Identifier */}
                  <StatCard icon={<Fingerprint className="text-blue-300" />} label="Modelo" className="hidden lg:block">
                     <p className="text-[11px] font-mono font-semibold break-all leading-tight mt-1" style={{ color: selectedFile.brand_color ?? '#9CA3AF' }}>
                        {selectedFile.detected_model || '—'}
                     </p>
                  </StatCard>
                </div>


                {/* Code viewer */}
                <div className="flex-1 min-h-0 bg-[#1e1e1e] rounded-2xl overflow-hidden border border-white/10 shadow-inner">
                  <CodeViewer
                    code={selectedFile.content}
                    language={selectedFile.language === 'txt' ? 'plaintext' : selectedFile.language}
                  />
                </div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex-1 glass-panel rounded-3xl flex flex-col items-center justify-center text-muted-foreground"
              >
                <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center mb-6">
                  <FileCode className="w-12 h-12 opacity-50" />
                </div>
                <p className="text-xl font-medium">Selecciona un archivo</p>
                <p className="text-sm mt-2 opacity-70">El análisis detallado aparecerá aquí</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
}
