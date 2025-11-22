module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // Nouvelle fonctionnalité
        'fix',      // Correction de bug
        'docs',     // Documentation
        'style',    // Formatage code (pas de changement logique)
        'refactor', // Refactoring
        'perf',     // Amélioration performance
        'test',     // Ajout/modification tests
        'chore',    // Tâches maintenance (deps, config, etc.)
        'ci',       // CI/CD
        'build',    // Build system
        'revert',   // Revert commit
        'wip',      // Work in progress (éviter en prod)
      ],
    ],
    'subject-case': [0], // Pas de contrainte sur la casse
    'header-max-length': [2, 'always', 100],
  },
};
