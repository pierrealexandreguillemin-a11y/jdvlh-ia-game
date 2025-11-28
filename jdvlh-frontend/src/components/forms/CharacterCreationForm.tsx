import React from 'react';
import { useForm } from 'react-hook-form';

interface FormData {
  name: string;
  pegi16: boolean;
}

const CharacterCreationForm: React.FC = () => {
  const { register, handleSubmit } = useForm<FormData>();

  const onSubmit = (data: FormData) => {
    if (!data.pegi16) {
      alert('PEGI 16 requis : 16 ans ou plus');
      return;
    }
    console.log('Personnage créé :', data);
    // Dispatch to store or backend
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 p-6 bg-slate-800/90 rounded-2xl shadow-2xl border border-amber-500/30">
      <div>
        <label className="block text-amber-200 mb-2">Nom du Personnage</label>
        <input 
          {...register('name', { required: true })}
          placeholder="Entrez votre nom"
          className="w-full p-4 rounded-xl bg-slate-700/50 border border-slate-500 text-white placeholder-slate-400 focus:border-amber-400 focus:outline-none transition-all"
        />
      </div>
      <label className="flex items-center space-x-3 p-4 bg-slate-900/50 rounded-xl">
        <input type="checkbox" {...register('pegi16')} className="w-5 h-5 text-amber-500 rounded" />
        <span className="text-sm text-amber-300">J'ai 16 ans ou plus (PEGI 16 - Contenu adapté adolescents)</span>
      </label>
      <button 
        type="submit" 
        className="w-full p-4 bg-gradient-to-r from-amber-500 to-amber-600 rounded-xl font-bold text-lg shadow-lg hover:from-amber-600 hover:to-amber-700 transform hover:scale-[1.02] transition-all"
      >
        Créer le Héros
      </button>
    </form>
  );
};

export default CharacterCreationForm;