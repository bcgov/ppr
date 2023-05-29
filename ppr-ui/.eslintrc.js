module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'plugin:vue/essential',
    '@vue/standard',
    '@vue/typescript',
    'plugin:vue/base',
    'plugin:vuetify/base',
    'plugin:vuetify/recommended'
  ],
  rules: {
    'standard/computed-property-even-spacing': 'off',
    'vue/multi-word-component-names': 'off',
    'vue/no-side-effects-in-computed-properties': 'off',
    'vue/valid-v-slot': ['error', { allowModifiers: true }],
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'max-len': ['warn', { code: 120, ignoreRegExpLiterals: true }]
  },
  parserOptions: {
    parser: '@typescript-eslint/parser',
    plugins: ['@typescript-eslint']
  },
  overrides: [
    {
      files: [
        '**/__tests__/*.{j,t}s?(x)',
        '**/tests/unit/**/*.spec.{j,t}s?(x)'
      ],
      env: {
        jest: true
      }
    }
  ]
}
