# Pathfinder 2e Content

## Structure

```
data/pf2e/
├── raw/              # SRD original EN (BACKUP - ne jamais modifier)
│   ├── spells/       # 60 fichiers JSON, 1584 sorts
│   ├── items/
│   ├── bestiary/
│   └── conditions.json
│
└── translated/       # Traductions générées
    └── fr/
        ├── spells.json      # 6 sorts traduits (MVP)
        ├── items.json       # 5 items traduits
        ├── monsters.json    # 3 monstres traduits
        └── conditions.json  # 27 conditions traduites
```

## Source

- **PF2eTools Data**: https://github.com/pf2etools/pf2etools-data
- **Archives of Nethys FR**: https://2e.aonprd.com/?Lang=fr
- **License**: Open Gaming License (OGL)

## Statistiques

- **Total sorts EN**: 1584
- **Sorts MVP (niv ≤3)**: 860
- **Traductions FR manuelles**: 6 sorts prioritaires
- **Conditions traduites**: 27 (complet)
- **Taille raw data**: ~18MB
- **Taille traductions**: ~10KB

## Usage

### Python

```python
from services.pf2e_content import get_pf2e_content

# Charger contenu
content = get_pf2e_content(language="fr")

# Récupérer sort
spell = content.get_spell("fireball")
print(spell.name)  # "Boule de feu"
print(spell.level)  # 3
print(spell.description)  # Description FR ou EN fallback

# Liste sorts MVP
mvp_spells = content.get_all_spells(filter_by_level=3)
print(f"{len(mvp_spells)} sorts niveau ≤3")  # 860 sorts

# Recherche
results = content.search_spells("feu", limit=5)
for spell in results:
    print(f"- {spell.name} (niv. {spell.level})")
```

### API REST

```bash
# Liste tous les sorts MVP
curl http://localhost:8000/api/pf2e/spells?level=3

# Détails d'un sort
curl http://localhost:8000/api/pf2e/spells/fireball

# Recherche
curl http://localhost:8000/api/pf2e/spells/search?q=feu&limit=5
```

## Mise à Jour Traductions

### Régénérer traductions FR

```bash
# Exécuter scraper (si Archives of Nethys disponible)
python -m src.jdvlh_ia_game.services.translation.pf2e_translator

# Ou ajouter traductions manuelles dans pf2e_translator.py
```

### Ajouter traductions manuelles

Éditer `src/jdvlh_ia_game/services/translation/pf2e_translator.py`:

```python
self.translations["spells"] = {
    "magic-missile": {
        "name": "Projectile magique",
        "description": "Vous lancez un projectile magique qui ne rate jamais."
    },
    # Ajouter d'autres sorts ici...
}
```

Puis régénérer:

```bash
python -m src.jdvlh_ia_game.services.translation.pf2e_translator
```

## Feature Flags

Configuration dans `src/jdvlh_ia_game/config/config.yaml`:

```yaml
pf2e:
  active_level: mvp # mvp | intermediate | full
```

### Niveaux disponibles

1. **MVP** (défaut) - Enfants 10-12 ans
   - Sorts niveau ≤3
   - Classes: fighter, wizard, ranger
   - Conditions simples

2. **Intermediate** - Enfants 12-14 ans
   - Sorts niveau ≤5
   - Toutes classes
   - Conditions complexes

3. **Full** - 14+ ans / Adultes
   - Tous sorts (niveau 1-10)
   - Toutes fonctionnalités
   - Archétypes activés

## Rollback

Si problème avec traductions:

```bash
# Supprimer traductions générées
rm -rf data/pf2e/translated/fr/

# Le système fallback automatiquement sur EN
# Ou régénérer les traductions manuelles
python -m src.jdvlh_ia_game.services.translation.pf2e_translator
```

## Traductions Prioritaires (MVP)

### Sorts traduits (6)

- acid-splash → Aspersion acide
- burning-hands → Mains brûlantes
- magic-missile → Projectile magique
- fireball → Boule de feu
- heal → Guérison
- shield → Bouclier

### À traduire (suggestions pour MVP)

- detect-magic → Détection de la magie
- light → Lumière
- mage-armor → Armure du mage
- sleep → Sommeil
- charm → Charme
- invisibility → Invisibilité

## Performance

- **Chargement initial**: ~5s (1584 sorts)
- **Recherche**: <100ms
- **API response**: <500ms
- **Mémoire**: ~50MB (cache en mémoire)

## Licence

Ce contenu utilise le SRD Pathfinder 2e sous Open Gaming License (OGL).

Les traductions françaises sont basées sur:

- Archives of Nethys FR (officiel Paizo)
- Black Book Éditions (éditeur officiel FR)
- Traductions communautaires (Pathfinder-FR.org)
