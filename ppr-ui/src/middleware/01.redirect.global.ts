export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.client) {
    const { $keycloak } = useNuxtApp()
    if (to.meta.requiresAuth && !$keycloak.authenticated) {
      const registryHomeURL = useRuntimeConfig().public.VUE_APP_REGISTRY_URL
      const redirectUrl = encodeURIComponent(window.location.href)
      window.location.href = `${registryHomeURL}/en-CA/login/?return=${redirectUrl}`
    }
  }
})
