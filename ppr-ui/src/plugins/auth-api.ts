// export default defineNuxtPlugin(() => {
//   const authApiUrl = useRuntimeConfig().public.authApiURL
//   const authApiKey = useRuntimeConfig().public.authApiKey
//   const errorRedirectPath = useAppConfig().connect.core.plugin.authApi.errorRedirect[401]
//   const { $keycloak } = useNuxtApp()
//   const localePath = useLocalePath()
//
//   const api = $fetch.create({
//     baseURL: authApiUrl,
//     onRequest ({ options }) {
//       let headers = options.headers ||= {} as Headers
//       headers = addToHeaders(headers)
//     },
//     async onResponseError ({ response }) {
//       if (response.status === 401) {
//         await navigateTo(localePath(errorRedirectPath))
//       }
//     }
//   })
//
//   return {
//     provide: {
//       authApi: api
//     }
//   }
// })

export const addToHeaders = (headers: any) => {
  const { $keycloak } = useNuxtApp()
  const authApiKey = useRuntimeConfig().public.authApiKey
  const bearerToken = `Bearer ${$keycloak.token}`
  if (Array.isArray(headers)) {
    headers.push(['Authorization', bearerToken])
    if (authApiKey) {
      headers.push(['x-apikey', authApiKey])
    }
  } else if (headers instanceof Headers) {
    headers.set('Authorization', bearerToken)
    if (authApiKey) {
      headers.set('x-apikey', authApiKey)
    }
  } else {
    headers.Authorization = bearerToken
    if (authApiKey) {
      headers['x-apikey'] = authApiKey
    }
  }
  return headers
}
