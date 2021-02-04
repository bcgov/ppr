import { Dashboard, Signin, Signout } from '@/views'
import { RouteNames } from '@/enums'

export const routes = [
  {
    // router.beforeEach() routes here:
    path: '/signin',
    name: RouteNames.SIGN_IN,
    component: Signin,
    meta: {
      requiresAuth: false
    }
  },
  {
    // SbcHeader.logout() redirects here:
    path: '/signout',
    name: RouteNames.SIGN_OUT,
    component: Signout,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/dashboard',
    name: RouteNames.DASHBOARD,
    component: Dashboard,
    meta: {
      requiresAuth: true
    }
  },
  {
    // default/fallback route
    // must be last
    path: '*',
    redirect: '/dashboard'
  }
]
