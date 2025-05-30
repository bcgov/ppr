export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.client) {
    const { $keycloak } = useNuxtApp()
    if (to.meta.requiresAuth && !$keycloak.authenticated) {
      const registryHomeURL = removeSuffix(useRuntimeConfig().public.VUE_APP_REGISTRY_URL, '/dashboard')
      const redirectUrl = encodeURIComponent(window.location.href)
      window.location.href = `${registryHomeURL}/en-CA/login/?return=${redirectUrl}`
    }
  }
})

const removeSuffix = (url: string, suffix: string) => {
  if (url.endsWith(suffix)) {
    return url.slice(0, -suffix.length)
  }
  return url
}
