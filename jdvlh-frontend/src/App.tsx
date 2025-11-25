import { useState } from 'react';
import { GameLayout, StoryDisplay, CharacterSheet } from './components';
import type { Character, NarrativeResponse } from './types/game';

// Demo data
const demoCharacter: Character = {
  name: 'Frodon Sacquet',
  race: 'Hobbit',
  class: 'Porteur',
  level: 3,
  stats: {
    strength: 8,
    dexterity: 14,
    constitution: 12,
    intelligence: 13,
    wisdom: 16,
    charisma: 15,
    hp: 18,
    maxHp: 24,
    mp: 10,
    maxMp: 10,
    xp: 750,
    xpToNext: 1000,
  },
  inventory: [],
  equipment: {
    weapon: { id: '1', name: 'Dard', description: 'Épée elfique', type: 'weapon', quantity: 1 },
    armor: { id: '2', name: 'Mithril', description: 'Cotte de mailles', type: 'armor', quantity: 1 },
    accessory: { id: '3', name: "L'Anneau Unique", description: 'Un anneau pour les gouverner tous', type: 'misc', quantity: 1 },
  },
};

const demoNarrative: NarrativeResponse = {
  narrative: `Vous vous tenez à l'orée de la Forêt de Fangorn. Les arbres anciens murmurent des secrets oubliés, leurs branches tordues semblent vous observer avec une curiosité millénaire.

Un sentier sinueux s'enfonce dans les ténèbres verdoyantes, tandis qu'à l'est, vous apercevez les premières lueurs d'un feu de camp.

Le vent porte jusqu'à vous l'odeur de la terre humide et quelque chose d'autre... une présence ancienne qui veille.`,
  choices: [
    'Emprunter le sentier sombre dans la forêt',
    "S'approcher du feu de camp à l'est",
    'Appeler pour voir si quelqu\'un répond',
    'Rebrousser chemin vers la Comté',
  ],
  location: 'Forêt de Fangorn',
  sfx: 'forest_ambiance',
};

function App() {
  const [narrative, setNarrative] = useState<NarrativeResponse>(demoNarrative);
  const [isLoading, setIsLoading] = useState(false);
  const [character] = useState<Character>(demoCharacter);

  const handleChoiceSelect = async (choice: string) => {
    setIsLoading(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Demo response based on choice
    const responses: Record<string, NarrativeResponse> = {
      'Emprunter le sentier sombre dans la forêt': {
        narrative: `Vous vous enfoncez dans la forêt. Les arbres semblent se refermer derrière vous, plongeant le sentier dans une pénombre mystérieuse.

Soudain, une voix grave résonne autour de vous : "Petit être... que cherches-tu dans les bois de Fangorn ?"

C'est Sylvebarbe, le plus ancien des Ents !`,
        choices: [
          'Demander le chemin vers Isengard',
          'Raconter votre quête',
          'Fuir à toutes jambes',
        ],
        location: 'Coeur de Fangorn',
        sfx: 'ent_voice',
      },
      "S'approcher du feu de camp à l'est": {
        narrative: `Vous vous approchez prudemment du feu de camp. Autour des flammes, vous découvrez deux silhouettes familières : Merry et Pippin !

"Frodon !" s'exclame Pippin. "On ne s'attendait pas à te voir ici ! Viens, on a du pain de lembas et des histoires à partager."`,
        choices: [
          'Rejoindre vos amis autour du feu',
          'Demander ce qu\'ils font ici',
          'Rester sur vos gardes',
        ],
        location: 'Campement',
        sfx: 'campfire',
      },
    };

    const response = responses[choice] || {
      narrative: `Vous faites votre choix et l'aventure continue...

"${choice}"

Le destin de la Terre du Milieu repose entre vos mains.`,
      choices: ['Continuer', 'Explorer les environs', 'Se reposer'],
      location: narrative.location,
    };

    setNarrative(response);
    setIsLoading(false);
  };

  const header = (
    <div className="flex items-center justify-between">
      <h1 className="text-2xl font-bold text-amber-100">
        🏔️ JDVLH - Livre dont Vous êtes le Héros
      </h1>
      <div className="text-amber-200 text-sm">
        Terre du Milieu • Aventure Interactive
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
    </GameLayout>
  );
}

export default App;
