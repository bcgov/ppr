import APP from '@/App.vue'
import {
  AddCollateral,
  AddSecuredPartiesAndDebtors,
  Dashboard,
  LengthTrust,
  ReviewConfirm,
  Search,
  Signin,
  Signout
} from '@/views'
import { RouteNames } from '@/enums'

export const routes = [
  {
    // router.beforeEach() routes here:
    path: '/signin',
    name: RouteNames.SIGN_IN,
    component: Signin,
    props: true,
    meta: {
      requiresAuth: false
    }
  },
  {
    // SbcHeader.logout() redirects here:
    path: '/signout',
    name: RouteNames.SIGN_OUT,
    component: Signout,
    props: true,
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
    path: '/length-trust',
    name: RouteNames.LENGTH_TRUST,
    component: LengthTrust,
    meta: {
      step: 1,
      label: 'Length and Trust Indenture',
      requiresAuth: true
    }
  },
  {
    path: '/add-securedparties-debtors',
    name: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
    component: AddSecuredPartiesAndDebtors,
    meta: {
      step: 2,
      label: 'Add Secured Parties And Debtors',
      requiresAuth: true
    }
  },
  {
    path: '/add-collateral',
    name: RouteNames.ADD_COLLATERAL,
    component: AddCollateral,
    meta: {
      step: 3,
      label: 'Add Collateral',
      requiresAuth: true
    }
  },
  {
    path: '/review-confirm',
    name: RouteNames.REVIEW_CONFIRM,
    component: ReviewConfirm,
    meta: {
      step: 4,
      label: 'Review and Confirm',
      requiresAuth: true
    }
  },
  {
    path: '/search',
    name: RouteNames.SEARCH,
    component: Search,
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
