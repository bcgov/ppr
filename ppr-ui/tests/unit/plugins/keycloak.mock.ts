
// tests/plugins/keycloak.mock.ts
export default defineNuxtPlugin(() => {
  // Only active in Vitest runs
  if (!(import.meta as any).env?.VITEST && process.env.NODE_ENV !== 'test') return
  return {
    provide: {
      keycloak: {
        authenticated: true,       // flip to false in specific tests to assert redirects
        token: 'test',
        userinfo: { sub: 'vitest' }
      }
    }
  }
})
