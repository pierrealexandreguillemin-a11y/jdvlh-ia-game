import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { PaperCard } from '../ui/PaperCard';
import { PaperButton } from '../ui/PaperButton';
import { useGameState } from '../../stores/useGameState';

interface FormData {
  pin: string;
  maxSessionTime: number;
  allowedStartHour: number;
  allowedEndHour: number;
  parentEmail: string;
}

const ParentalControl: React.FC = () => {
  const playerId = useGameState((state) => state.playerId);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit, reset } = useForm<FormData>({
    defaultValues: {
      pin: '',
      maxSessionTime: 60,
      allowedStartHour: 14,
      allowedEndHour: 20,
      parentEmail: '',
    },
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setStatus('');

    try {
      // Set PIN
      const pinRes = await fetch(`http://localhost:8000/parental/set_pin/${playerId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pin: data.pin }),
      });
      const pinData = await pinRes.json();
      if (!pinData.success) {
        setStatus(pinData.message || 'Erreur PIN');
        return;
      }

      // Update settings
      const settingsRes = await fetch(`http://localhost:8000/parental/update_settings/${playerId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pin: data.pin,
          settings: {
            max_session_time: data.maxSessionTime,
            allowed_hours: [data.allowedStartHour, data.allowedEndHour],
          },
        }),
      });
      await settingsRes.json();

      // Export logs
      if (data.parentEmail) {
        await fetch(`http://localhost:8000/parental/export_logs/${playerId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ parent_email: data.parentEmail }),
        });
      }

      setStatus('Configuration sauvegardée !');
      reset();
    } catch {
      setStatus('Erreur connexion serveur');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PaperCard variant="book-desk">
      <h2>Contrôle Parental</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label>Code PIN (4 chiffres)</label>
          <input
            {...register('pin', { minLength: 4, maxLength: 4 })}
            type="password"
            className="paper-input w-full"
            placeholder="1234"
          />
        </div>

        <div>
          <label>Temps max session (min)</label>
          <input
            type="range"
            min="30"
            max="120"
            {...register('maxSessionTime', { valueAsNumber: true })}
            className="paper-slider"
          />
          <span>{60} min</span>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label>Heure début</label>
            <input
              type="number"
              min="0"
              max="23"
              {...register('allowedStartHour', { valueAsNumber: true })}
              className="paper-input"
            />
          </div>
          <div>
            <label>Heure fin</label>
            <input
              type="number"
              min="0"
              max="23"
              {...register('allowedEndHour', { valueAsNumber: true })}
              className="paper-input"
            />
          </div>
        </div>

        <div>
          <label>Email parents (optionnel)</label>
          <input
            {...register('parentEmail')}
            type="email"
            className="paper-input w-full"
            placeholder="parent@example.com"
          />
        </div>

        <PaperButton type="submit" disabled={loading}>
          {loading ? 'Sauvegarde...' : 'Sauvegarder'}
        </PaperButton>
      </form>

      {status && <p className="mt-4 p-2 bg-paper-status">{status}</p>}
    </PaperCard>
  );
};

export { ParentalControl };