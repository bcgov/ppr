import { nextTick } from 'vue'
import type { Route} from 'vue-router';
import { createWebHistory, createRouter } from 'vue-router'
import { routes } from './routes'
import { RouteNames } from '@/enums'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'

/** Returns True if route requires authentication, else False. */
function requiresAuth (route: Route): boolean {
  return route.matched.some(r => r.meta?.requiresAuth)
}

/** Returns True if user is authenticated, else False. */
function isAuthenticated (): boolean {
  // FUTURE: also check that token isn't expired!
  return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
}

/** Returns True if route is Signin, else False. */
// eslint-disable-next-line
function isSigninRoute (route: Route): boolean {
  return Boolean(route.name === 'signin')
}

/** Returns True if route is Signout, else False. */
// eslint-disable-next-line
function isSignoutRoute (route: Route): boolean {
  return Boolean(route.name === 'signout')
}

/** Returns True if route is Login success, else False. */
function isLogin (route: Route): boolean {
  return Boolean(route.name === RouteNames.LOGIN)
}

/** Returns True if route is Login success, else False. */
function isLoginSuccess (route: Route): boolean {
  return Boolean(route.name === RouteNames.LOGIN && route.hash)
}

export default defineNuxtRouteMiddleware((to) => {
  console.log('Global middleware', to)
  if (isLoginSuccess(to)) {
    console.log('Login success')
    // this route is to verify login
    navigateTo({
      name: RouteNames.SIGN_IN,
      query: { redirect: to.query.redirect }
    })
  } else {
    console.log('Not login success')
    if (requiresAuth(to) && !isAuthenticated()) {
      // this route needs authentication, so re-route to login
      navigateTo({
        name: RouteNames.LOGIN,
        query: { redirect: to.fullPath }
      })
    } else {
      console.log('Not requires auth')
      if (isLogin(to) && isAuthenticated()) {
        // this route is to login
        navigateTo({ name: RouteNames.DASHBOARD })
      } else {
        // otherwise just proceed normally
        navigateTo()
      }
    }
  }

  // const expectedRoutes = [RouteNameE.DASHBOARD]
  // if (!expectedRoutes.includes(to.name as RouteNameE)) {
  //   // TODO: remove dev/test redirects once other apps are redirecting to here properly
  //   // set specific identifier for development (allows going directly to localhost link)
  //   if (['local', 'pr', 'dev'].includes(useRuntimeConfig().public.appEnv)) {
  //     const identifier = 'BC0871427'
  //     return navigateTo({ name: RouteNameE.DASHBOARD, params: { identifier } })
  //   } else if (['test'].includes(useRuntimeConfig().public.appEnv)) {
  //     const identifier = 'BC1052139'
  //     return navigateTo({ name: RouteNameE.DASHBOARD, params: { identifier } })
  //   } else {
  //     useBcrosNavigate().goToBcrosDashboard()
  //   }
  // }
})

/**
 * Configures and returns Vue Router.
 */
// export function getVueRouter () {
//   const router = createRouter({
//     history: createWebHistory(import.meta.env.BASE_URL),
//     // set base URL for Vue Router
//     base: sessionStorage.getItem('VUE_ROUTER_BASE'),
//     routes,
//     // eslint-disable-next-line
//     scrollBehavior (to, from, savedPosition) {
//       // see https://router.vuejs.org/guide/advanced/scroll-behavior.html
//       return { x: 0, y: 0 }
//     }
//   })
//
//
//   router.beforeEach((to, from, next) => {
//     if (isLoginSuccess(to)) {
//       // this route is to verify login
//       next({
//         name: RouteNames.SIGN_IN,
//         query: { redirect: to.query.redirect }
//       })
//     } else {
//       if (requiresAuth(to) && !isAuthenticated()) {
//         // this route needs authentication, so re-route to login
//         next({
//           name: RouteNames.LOGIN,
//           query: { redirect: to.fullPath }
//         })
//       } else {
//         if (isLogin(to) && isAuthenticated()) {
//           // this route is to login
//           next({ name: RouteNames.DASHBOARD })
//         } else {
//           // otherwise just proceed normally
//           next()
//         }
//       }
//     }
//   })
//
//   router.afterEach((to) => {
//     // Override the browser tab name
//     nextTick(() => {
//       if (to.meta.title) {
//         document.title = to.meta.title
//       }
//     })
//   })
