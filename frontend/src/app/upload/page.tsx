'use client';

import React, { useState, useRef } from 'react';
import { Upload, FileCode, CheckCircle2, AlertCircle, Loader2, FileText } from 'lucide-react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { getApiUrl } from '@/lib/config';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement> | React.DragEvent) => {
    let selectedFile: File | null = null;

    if ('dataTransfer' in e) {
      selectedFile = e.dataTransfer.files[0];
    } else if (e.target.files) {
      selectedFile = e.target.files[0];
    }

    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileChange(e);
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(getApiUrl('upload'), formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      router.push(`/project/${response.data.project_id}`);
    } catch (err) {
      console.error(err);
      setError('Error al subir el archivo. Asegúrate de que el backend esté en ejecución.');
      setIsUploading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-4xl mx-auto py-16 px-4"
    >
      <div className="text-center mb-16">
        <motion.div 
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6 border-secondary/30"
        >
          <FileText className="w-4 h-4 text-secondary" />
          <span className="text-sm font-medium tracking-wide">Ahora soporta Word, Excel y PDF</span>
        </motion.div>
        <h1 className="text-4xl md:text-5xl font-extrabold mb-4 tracking-tight">
          Analizar <span className="text-gradient">Nuevo Proyecto</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Sube un archivo .zip con el código fuente o documentos individuales. Extraeremos el texto y usaremos IA para detectar si fue generado por máquinas.
        </p>
      </div>

      <motion.div 
        layout
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "relative overflow-hidden border-2 border-dashed rounded-[2.5rem] p-12 flex flex-col items-center justify-center transition-all duration-300 min-h-[400px]",
          isDragging ? "border-primary bg-primary/10 scale-[1.02]" : "border-white/10 hover:border-white/20 bg-black/40",
          file && !isDragging ? "border-green-500/30 bg-green-500/5" : ""
        )}
      >
        <AnimatePresence mode="wait">
          {!file ? (
            <motion.div 
              key="upload-prompt"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center z-10"
            >
              <motion.div 
                animate={{ y: [0, -10, 0] }}
                transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                className="w-24 h-24 bg-gradient-to-tr from-primary/20 to-secondary/20 rounded-full flex items-center justify-center mb-8 shadow-[0_0_50px_-10px_rgba(59,130,246,0.3)]"
              >
                <Upload className="w-10 h-10 text-white" />
              </motion.div>
              <p className="text-2xl font-bold mb-3">Arrastra tu archivo aquí</p>
              <p className="text-muted-foreground mb-8 text-center text-lg">ZIP, PDF, DOCX, XLSX o Código Fuente</p>
              
              <input 
                type="file" 
                className="hidden" 
                ref={fileInputRef}
                onChange={handleFileChange}
              />
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => fileInputRef.current?.click()}
                className="bg-white text-black px-10 py-4 rounded-2xl font-bold cursor-pointer transition-all shadow-[0_0_30px_-10px_rgba(255,255,255,0.3)] hover:shadow-[0_0_40px_-5px_rgba(255,255,255,0.4)]"
              >
                Explorar Archivos
              </motion.button>
            </motion.div>
          ) : (
            <motion.div 
              key="file-ready"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center z-10 w-full max-w-md"
            >
              <div className="w-24 h-24 bg-green-500/20 rounded-full flex items-center justify-center mb-6 shadow-[0_0_50px_-10px_rgba(34,197,94,0.3)]">
                <FileCode className="w-10 h-10 text-green-400" />
              </div>
              <p className="text-2xl font-bold mb-2 text-center break-all">{file.name}</p>
              <p className="text-muted-foreground mb-10 text-lg">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              
              <div className="flex flex-col sm:flex-row w-full gap-4">
                <motion.button 
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setFile(null)}
                  disabled={isUploading}
                  className="flex-1 glass px-6 py-4 rounded-2xl font-bold hover:bg-white/10 transition-all"
                >
                  Cambiar
                </motion.button>
                <motion.button 
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="flex-[2] bg-primary hover:bg-blue-600 text-white px-8 py-4 rounded-2xl font-bold flex items-center justify-center gap-2 transition-all disabled:opacity-50 relative overflow-hidden"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analizando...
                    </>
                  ) : (
                    <>
                      Iniciar Análisis
                      <CheckCircle2 className="w-5 h-5" />
                    </>
                  )}
                  {isUploading && (
                     <div className="absolute top-0 left-0 w-full h-full bg-white/20 animate-pulse" />
                  )}
                </motion.button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="mt-8 p-5 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-500 flex items-center gap-4"
          >
            <AlertCircle className="w-6 h-6 flex-shrink-0" />
            <p className="text-sm md:text-base font-medium">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
