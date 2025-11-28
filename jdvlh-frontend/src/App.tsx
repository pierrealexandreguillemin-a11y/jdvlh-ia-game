import { useState, useEffect, useCallback } from 'react';
import { GameLayout, StoryDisplay, CharacterSheet } from './components';
import { useWebSocket } from './hooks/useWebSocket';
import { DiceRoller } from './components/combat/DiceRoller';
import type { Character, NarrativeResponse } from './types/game';

// Pathfinder 2e demo character
const pf2eCharacter: Character = {
  name: 'Valéria Sanspeur',
  race: 'Humaine',
  class: 'Guerrière',
  level: 3,
  stats: {
    strength: 16,
    dexterity: 14,
    constitution: 14,
    intelligence: 10,
    wisdom: 12,
    charisma: 12,
    hp: 42,
    maxHp: 42,
    mp: 0,
    maxMp: 0,
    xp: 750,
    xpToNext: 1000,
  },
  inventory: [],
  equipment: {
    weapon: { id: '1', name: 'Épée longue +1', description: 'Arme martiale PF2e', type: 'weapon', quantity: 1 },
    armor: { id: '2', name: 'Cotte de mailles', description: 'Armure moyenne CA +4', type: 'armor', quantity: 1 },
    accessory: { id: '3', name: 'Amulette de vie', description: '+2 aux jets de Vigueur', type: 'misc', quantity: 1 },
  },
};

// Initial narrative for Pathfinder 2e / Golarion
const initialNarrative: NarrativeResponse = {
  narrative: `Vous vous tenez sur les docks animés d'Absalom, la Cité au Centre du Monde. L'air marin se mêle aux effluves d'épices exotiques et au brouhaha des marchands criant leurs prix.

Une affiche attire votre attention sur le panneau des annonces : "Aventuriers recherchés - Exploration de ruines anciennes près de Sandpoint. Récompense généreuse. Se présenter à la Taverne du Gobelin Rouillé."

Les mouettes tournoient au-dessus de vous tandis qu'un groupe de Garde du Grand Conseil passe, leurs armures brillant au soleil.`,
  choices: [
    'Se rendre à la Taverne du Gobelin Rouillé',
    'Explorer les marchés du port',
    'Enquêter sur les ruines mentionnées',
    'Chercher la guilde des aventuriers',
  ],
  location: 'Absalom - Les Docks',
  sfx: 'port_ambiance',
};

function App() {
  const [narrative, setNarrative] = useState<NarrativeResponse>(initialNarrative);
  const [isLoading, setIsLoading] = useState(false);
  const [character] = useState<Character>(pf2eCharacter);
  const [playerId] = useState(() => `player_${Date.now()}`);
  const [connectionStatus, setConnectionStatus] = useState<'offline' | 'connecting' | 'online'>('offline');

  // Dice roller state
  const [diceRollRequest, setDiceRollRequest] = useState<{
    skill: string;
    dc: number;
    onResult: (result: number, success: boolean) => void;
  } | null>(null);

  // WebSocket connection
  const { socket, isConnected, send } = useWebSocket(playerId);

  // Handle WebSocket messages
  useEffect(() => {
    if (!isConnected) {
      setConnectionStatus('offline');
      return;
    }

    setConnectionStatus('online');
    const ws = socket();

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        setIsLoading(false);

        // Check for dice roll trigger
        if (data.animation_trigger?.startsWith('DICE_ROLL:')) {
          const [, skill, dcStr] = data.animation_trigger.split(':');
          const dc = parseInt(dcStr, 10);

          // Store narrative but request dice roll first
          setDiceRollRequest({
            skill,
            dc,
            onResult: (result, success) => {
              // Append result to narrative
              const resultText = success
                ? `\n\n✅ Jet de ${skill} : ${result} vs DC ${dc} - Succès !`
                : `\n\n❌ Jet de ${skill} : ${result} vs DC ${dc} - Échec...`;

              setNarrative({
                ...data,
                narrative: data.narrative + resultText,
              });
              setDiceRollRequest(null);
            },
          });

          // Show partial narrative while waiting for roll
          setNarrative({
            ...data,
            choices: [], // Hide choices until roll is done
          });
        } else {
          setNarrative(data);
        }
      } catch (err) {
        console.error('Failed to parse WS message:', err);
      }
    };

    ws.addEventListener('message', handleMessage);
    return () => ws.removeEventListener('message', handleMessage);
  }, [isConnected, socket]);

  const handleChoiceSelect = useCallback(async (choice: string) => {
    setIsLoading(true);

    if (isConnected) {
      // Send via WebSocket
      send({ action: 'choice', choice });
    } else {
      // Demo mode fallback
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const demoResponses: Record<string, NarrativeResponse> = {
        'Se rendre à la Taverne du Gobelin Rouillé': {
          narrative: `La Taverne du Gobelin Rouillé est un établissement typique des quartiers portuaires d'Absalom. Une enseigne représentant un gobelin hilare tenant une choppe se balance au vent.

À l'intérieur, l'atmosphère est chaleureuse malgré la fumée des pipes. Un homme barbu portant une cape de voyage usée vous fait signe depuis une table dans le coin. Il correspond à la description du commanditaire.

"Ah, vous êtes là pour les ruines de Sandpoint ? Approchez, j'ai besoin de gens capables..."`,
          choices: [
            'Approcher et écouter la proposition',
            'Commander une bière avant de négocier',
            'Observer les autres clients de la taverne',
          ],
          location: 'Absalom - Taverne du Gobelin Rouillé',
          animation_trigger: 'DICE_ROLL:perception:14',
          sfx: 'tavern',
        },
        'Explorer les marchés du port': {
          narrative: `Les marchés d'Absalom sont un kaléidoscope de couleurs et de sons. Des marchands venus des quatre coins de Golarion proposent leurs marchandises : épices du Qadira, armes naines de la Montagne des Cinq Rois, parchemins arcaniques de Nex.

Un marchand halfelin vous interpelle : "Hé, aventurière ! J'ai des potions de guérison, meilleur prix du port !"

Plus loin, vous apercevez un attroupement autour d'un conteur qui narre des légendes sur les ruines de Thassilon.`,
          choices: [
            'Acheter des potions au halfelin',
            'Écouter les légendes du conteur',
            'Chercher un armurier',
          ],
          location: 'Absalom - Grand Marché',
          sfx: 'market',
        },
      };

      const response = demoResponses[choice] || {
        narrative: `Vous faites votre choix avec détermination. L'aventure vous mène vers de nouveaux horizons sur Golarion.

"${choice}"

Les dieux de Golarion observent vos actions avec intérêt...`,
        choices: ['Continuer l\'exploration', 'Examiner les environs', 'Se reposer'],
        location: narrative.location,
        sfx: 'ambient',
      };

      // Check for dice roll in demo mode
      if (response.animation_trigger?.startsWith('DICE_ROLL:')) {
        const [, skill, dcStr] = response.animation_trigger.split(':');
        const dc = parseInt(dcStr, 10);

        setDiceRollRequest({
          skill,
          dc,
          onResult: (result, success) => {
            const resultText = success
              ? `\n\n✅ Jet de ${skill} : ${result} vs DC ${dc} - Succès !`
              : `\n\n❌ Jet de ${skill} : ${result} vs DC ${dc} - Échec...`;

            setNarrative({
              ...response,
              narrative: response.narrative + resultText,
            });
            setDiceRollRequest(null);
            setIsLoading(false);
          },
        });

        setNarrative({
          ...response,
          choices: [],
        });
        setIsLoading(false);
      } else {
        setNarrative(response);
        setIsLoading(false);
      }
    }
  }, [isConnected, send, narrative.location]);

  const header = (
    <div className="flex items-center justify-between">
      <h1 className="text-2xl font-bold text-amber-100">
        JDVLH - Pathfinder 2e
      </h1>
      <div className="flex items-center gap-4">
        <div className="text-amber-200 text-sm">
          Golarion - Aventure Interactive
        </div>
        <div className={`flex items-center gap-2 text-sm ${
          connectionStatus === 'online' ? 'text-green-400' :
          connectionStatus === 'connecting' ? 'text-yellow-400' : 'text-red-400'
        }`}>
          <span className={`w-2 h-2 rounded-full ${
            connectionStatus === 'online' ? 'bg-green-400' :
            connectionStatus === 'connecting' ? 'bg-yellow-400 animate-pulse' : 'bg-red-400'
          }`} />
          {connectionStatus === 'online' ? 'Connecté' :
           connectionStatus === 'connecting' ? 'Connexion...' : 'Mode Démo'}
        </div>
      </div>
    </div>
  );

  const sidebar = <CharacterSheet character={character} />;

  return (
    <GameLayout header={header} sidebar={sidebar}>
      <StoryDisplay
        narrative={narrative.narrative}
        choices={narrative.choices}
        location={narrative.location}
        isLoading={isLoading}
        onChoiceSelect={handleChoiceSelect}
      />

      {/* Dice Roller Modal */}
      {diceRollRequest && (
        <DiceRoller
          skill={diceRollRequest.skill}
          dc={diceRollRequest.dc}
          modifier={Math.floor((character.stats.wisdom - 10) / 2)} // Use wisdom for perception by default
          onRoll={diceRollRequest.onResult}
        />
      )}
    </GameLayout>
  );
}

export default App;
