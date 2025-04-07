import type { Route } from 'vue-router'
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
 
function isSigninRoute (route: Route): boolean {
  return Boolean(route.name === 'signin')
}

/** Returns True if route is Signout, else False. */
 
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

export default defineNuxtRouteMiddleware( (to) => {
  if (isLoginSuccess(to)) {
    // this route is to verify login
    return navigateTo({ name: RouteNames.SIGN_IN, query: { redirect: to.query.redirect } })
  }

  if (requiresAuth(to) && !isAuthenticated()) {
    // this route needs authentication, so re-route to login
    return navigateTo({ name: RouteNames.LOGIN, query: { redirect: to.path } })
  }

  if (isLogin(to) && isAuthenticated()) {
    return navigateTo({ name: RouteNames.DASHBOARD })
  }
})
