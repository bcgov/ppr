// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt(
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
      "@typescript-eslint/no-unused-vars": "warn",
      "@typescript-eslint/no-explicit-any": "off"
    }
  })
