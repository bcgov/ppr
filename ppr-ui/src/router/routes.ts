import APP from '@/App.vue'
import {
  AddCollateral,
  AddSecuredPartiesAndDebtors,
  ConfirmDischarge,
  Dashboard,
  LengthTrust,
  ReviewConfirm,
  ReviewRegistration,
  RenewRegistration,
  ConfirmRenewal,
  Search,
  Signin,
  Signout,
  AmendRegistration,
  ConfirmAmendment,
  Login
} from '@/views'
import { RouteNames } from '@/enums'

export const routes = [
  {
    // router.beforeEach() routes here:
    path: '/login',
    name: RouteNames.LOGIN,
    component: Login,
    props: true,
    meta: {
      requiresAuth: false,
      title: 'BC Registries Account Login'
    }
  },
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
    path: '/discharge/confirm-discharge',
    name: RouteNames.CONFIRM_DISCHARGE,
    component: ConfirmDischarge,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/discharge/review-discharge',
    name: RouteNames.REVIEW_DISCHARGE,
    component: ReviewRegistration,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/renew/renew-registration',
    name: RouteNames.RENEW_REGISTRATION,
    component: RenewRegistration,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/renew/confirm-renewal',
    name: RouteNames.CONFIRM_RENEWAL,
    component: ConfirmRenewal,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/amendment/amend-registration',
    name: RouteNames.AMEND_REGISTRATION,
    component: AmendRegistration,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/amendment/confirm-admendment',
    name: RouteNames.CONFIRM_AMENDMENT,
    component: ConfirmAmendment,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/new-registration/length-trust',
    name: RouteNames.LENGTH_TRUST,
    component: LengthTrust,
    meta: {
      step: 1,
      label: 'Length and Trust Indenture',
      requiresAuth: true
    }
  },
  {
    path: '/new-registration/add-securedparties-debtors',
    name: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
    component: AddSecuredPartiesAndDebtors,
    meta: {
      step: 2,
      label: 'Add Secured Parties And Debtors',
      requiresAuth: true
    }
  },
  {
    path: '/new-registration/add-collateral',
    name: RouteNames.ADD_COLLATERAL,
    component: AddCollateral,
    meta: {
      step: 3,
      label: 'Add Collateral',
      requiresAuth: true
    }
  },
  {
    path: '/new-registration/review-confirm',
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
    redirect: '/login'
  }
]
