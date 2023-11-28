module.exports = {
  root: true,
  env: {
    node: true,
    es2022: true
  },
  plugins: ['vue'],
  extends: [
    'plugin:vuetify/base',
    'plugin:vue/vue3-recommended',
    '@vue/typescript/recommended'
  ],
  rules: {
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/ban-ts-comment': 'off',
    '@typescript-eslint/no-duplicate-enum-values': 'off',
    'object-curly-spacing': ['error', 'always'],
    'standard/computed-property-even-spacing': 'off',
    'vue/multi-word-component-names': 'off',
    'vue/no-side-effects-in-computed-properties': 'off',
    'vue/valid-v-slot': ['error', { allowModifiers: true }],
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'max-len': ['warn', { code: 120, ignoreRegExpLiterals: true }],
    'vue/require-explicit-emits': 'error',
    'vue/require-default-prop': 'error',
    'vue/require-prop-types': 'error',
    'vue/no-template-shadow': 'off',
    'vue/attribute-hyphenation': 'off',
    'vue/v-on-event-hyphenation': 'off',
    'vue/prop-name-casing': ['error', 'camelCase'],
    'vue/custom-event-name-casing': ['error', 'camelCase'],
    'vue/no-v-html': 'off'
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    sourceType: 'module'
  }
}
