import Vue from 'vue'
import VueRouter, { Route } from 'vue-router'
import { routes } from './routes'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { RouteNames } from '@/enums'

/**
 * Configures and returns Vue Router.
 */
export function getVueRouter () {
  Vue.use(VueRouter)

  const router = new VueRouter({
    mode: 'history',
    // set base URL for Vue Router
    base: sessionStorage.getItem('VUE_ROUTER_BASE'),
    routes,
    scrollBehavior (to, from, savedPosition) {
      // see https://router.vuejs.org/guide/advanced/scroll-behavior.html
      const scrollToTableRoutes = [
        RouteNames.ADD_COLLATERAL,
        RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
        RouteNames.LENGTH_TRUST,
        RouteNames.REVIEW_CONFIRM,
        RouteNames.REVIEW_DISCHARGE,
        RouteNames.CONFIRM_DISCHARGE,
        RouteNames.RENEW_REGISTRATION,
        RouteNames.CONFIRM_RENEWAL,
        RouteNames.AMEND_REGISTRATION,
        RouteNames.CONFIRM_AMENDMENT
      ]
      const fromRouteName = from.name as RouteNames
      if (to.name === RouteNames.DASHBOARD && scrollToTableRoutes.includes(fromRouteName)) {
        return { x: 0, y: 1000 }
      }
      return { x: 0, y: 0 }
    }
  })

  router.beforeEach((to, from, next) => {
    if (isLoginSuccess(to)) {
      // this route is to verify login
      next({
        name: RouteNames.SIGN_IN,
        query: { redirect: to.query.redirect }
      })
    } else {
      if (requiresAuth(to) && !isAuthenticated()) {
        // this route needs authentication, so re-route to login
        next({
          name: RouteNames.LOGIN,
          query: { redirect: to.fullPath }
        })
      } else {
        if (isLogin(to) && isAuthenticated()) {
          // this route is to login
          next({ name: RouteNames.DASHBOARD })
        } else {
          // otherwise just proceed normally
          next()
        }
      }
    }
  })

  router.afterEach((to, from) => {
    // Overrid the browser tab name
    Vue.nextTick(() => {
      if (to.meta.title) {
        document.title = to.meta.title
      }
    })
  })

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
    return Boolean(route.name === RouteNames.SIGN_IN)
  }

  /** Returns True if route is Signout, else False. */
  function isSignoutRoute (route: Route): boolean {
    return Boolean(route.name === RouteNames.SIGN_OUT)
  }

  /** Returns True if route is Login success, else False. */
  function isLogin (route: Route): boolean {
    return Boolean(route.name === RouteNames.LOGIN)
  }

  /** Returns True if route is Login success, else False. */
  function isLoginSuccess (route: Route): boolean {
    return Boolean(route.name === RouteNames.LOGIN && route.hash)
  }

  return router
}
