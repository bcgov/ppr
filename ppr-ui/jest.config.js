module.exports = {
  globals: {
    'ts-jest': {
      diagnostics: false,
      isolatedModules: true,
      babelConfig: true
    }
  },
  setupFiles: ['jest-launchdarkly-mock'],
  preset: '@vue/cli-plugin-unit-jest/presets/typescript-and-babel',
  transformIgnorePatterns: []

}
