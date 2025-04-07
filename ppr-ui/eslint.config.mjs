// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt(
  {ignores: ['**/*.spec/*', '**/tests/*']},
  {
    "rules": {
      "max-len": [
        "warn",
        { "code": 120, "ignoreRegExpLiterals": true, "ignoreTrailingComments": true }
      ],
      "no-console": ["error", { "allow": ["warn", "error", "info"] }],
      "space-before-function-paren": "off",
      "vue/no-unused-vars": "warn",
      "vue/multi-word-component-names": "off",
      "vue/no-v-html": "off",
      "vue/no-template-shadow": "off",
      "@typescript-eslint/no-dynamic-delete": "off",
      "no-constant-binary-expression": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unused-expressions": "off",
      "@typescript-eslint/no-duplicate-enum-values": "off",
      "@typescript-eslint/no-empty-object-type": "off",
      "@typescript-eslint/no-invalid-void-type": "off",
      "vue/no-side-effects-in-computed-properties": "off"
    }
  })
