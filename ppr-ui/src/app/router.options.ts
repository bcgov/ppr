import type { RouterConfig } from '@nuxt/schema'
import { RouteNames } from '@/enums'

import {
  AddCollateral,
  AddSecuredPartiesAndDebtors,
  DischargeRegistration,
  ConfirmDischarge,
  Dashboard,
  Exemptions,
  LengthTrust,
  ManagePartyCodes,
  MHRSearch,
  MhrRegistration,
  MhrInformation,
  MhrHistory,
  ConfirmMHRSearch,
  ReviewConfirm,
  RenewRegistration,
  ConfirmRenewal,
  Search,
  AmendRegistration,
  ConfirmAmendment,
  MhrUnitNote,
  UserAccess,
  SubmittingParty,
  YourHome,
  HomeOwners,
  HomeLocation,
  MhrReviewConfirm,
  QsSelectAccess,
  QsInformation,
  QsReviewConfirm,
  ExemptionDetails,
  ExemptionReview
} from '@/pages'

export default <RouterConfig> {
  // https://router.vuejs.org/api/interfaces/routeroptions.html#routes
  // alternatively, could put this inside the setup for each page
  routes: _routes => [
    {
      path: '/dashboard/:anchorId?',
      name: RouteNames.DASHBOARD,
      component: Dashboard,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/discharge/confirm-discharge',
      name: RouteNames.CONFIRM_DISCHARGE,
      component: ConfirmDischarge,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/discharge/review-discharge',
      name: RouteNames.REVIEW_DISCHARGE,
      component: DischargeRegistration,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/renew/renew-registration',
      name: RouteNames.RENEW_REGISTRATION,
      component: RenewRegistration,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/renew/confirm-renewal',
      name: RouteNames.CONFIRM_RENEWAL,
      component: ConfirmRenewal,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/amendment/amend-registration',
      name: RouteNames.AMEND_REGISTRATION,
      component: AmendRegistration,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/amendment/confirm-amendment',
      name: RouteNames.CONFIRM_AMENDMENT,
      component: ConfirmAmendment,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/new-registration/length-trust',
      name: RouteNames.LENGTH_TRUST,
      component: LengthTrust,
      meta: {
        step: 1,
        label: 'Length and Trust Indenture',
        requiresAuth: true,
      },
    },
    {
      path: '/new-registration/add-securedparties-debtors',
      name: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
      component: AddSecuredPartiesAndDebtors,
      meta: {
        step: 2,
        label: 'Add Secured Parties And Debtors',
        requiresAuth: true,
      },
    },
    {
      path: '/new-registration/add-collateral',
      name: RouteNames.ADD_COLLATERAL,
      component: AddCollateral,
      meta: {
        step: 3,
        label: 'Add Collateral',
        requiresAuth: true,
      },
    },
    {
      path: '/new-registration/review-confirm',
      name: RouteNames.REVIEW_CONFIRM,
      component: ReviewConfirm,
      meta: {
        step: 4,
        label: 'Review and Confirm',
        requiresAuth: true,
      },
    },
    {
      path: '/manage-party-codes',
      name: RouteNames.MANAGE_PARTY_CODES,
      component: ManagePartyCodes,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/mhr-registration',
      component: MhrRegistration,
      name: RouteNames.MHR_REGISTRATION,
      children: [
        {
          path: '/mhr-registration/your-home',
          name: RouteNames.YOUR_HOME,
          component: YourHome,
          meta: {
            step: 1,
            label: 'Describe your Home',
            requiresAuth: true,
          },
        },
        {
          path: '/mhr-registration/submitting-party',
          name: RouteNames.SUBMITTING_PARTY,
          component: SubmittingParty,
          meta: {
            step: 2,
            label: 'Submitting Party',
            requiresAuth: true,
          },
        },
        {
          path: '/mhr-registration/home-owners',
          name: RouteNames.HOME_OWNERS,
          component: HomeOwners,
          meta: {
            step: 3,
            label: 'List the Home Owners',
            requiresAuth: true,
          },
        },
        {
          path: '/mhr-registration/home-location',
          name: RouteNames.HOME_LOCATION,
          component: HomeLocation,
          meta: {
            step: 4,
            label: 'Detail the Home Location',
            requiresAuth: true,
          },
        },
        {
          path: '/mhr-registration/mhr-review-confirm',
          name: RouteNames.MHR_REVIEW_CONFIRM,
          component: MhrReviewConfirm,
          meta: {
            step: 5,
            label: 'Review and Confirm',
            requiresAuth: true,
          },
        },
      ]
    },
    {
      path: '/ppr/search/:searchId?',
      name: RouteNames.SEARCH,
      component: Search,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/mhr/search',
      name: RouteNames.MHRSEARCH,
      component: MHRSearch,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/mhr/search-confirm',
      name: RouteNames.MHRSEARCH_CONFIRM,
      component: ConfirmMHRSearch,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/mhr-information',
      name: RouteNames.MHR_INFORMATION,
      component: MhrInformation,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/mhr-information-note',
      name: RouteNames.MHR_INFORMATION_NOTE,
      component: MhrUnitNote,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/mhr-history',
      name: RouteNames.MHR_HISTORY,
      component: MhrHistory,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/user-access',
      component: UserAccess,
      name: RouteNames.QS_USER_ACCESS,
      children: [
        {
          path: '/user-access/qs-access-type',
          name: RouteNames.QS_ACCESS_TYPE,
          component: QsSelectAccess,
          meta: {
            requiresAuth: true,
          },
        },
        {
          path: '/user-access/qs-access-information',
          name: RouteNames.QS_ACCESS_INFORMATION,
          component: QsInformation,
          meta: {
            step: 1,
            label: 'Qualified Supplier Information',
            requiresAuth: true,
          },
        },
        {
          path: '/user-access/qs-access-review-confirm',
          name: RouteNames.QS_ACCESS_REVIEW_CONFIRM,
          component: QsReviewConfirm,
          meta: {
            step: 2,
            label: 'Review and Confirm',
            requiresAuth: true,
          },
        },
      ]
    },
    {
      path: '/residential-exemption',
      component: Exemptions,
      name: RouteNames.RESIDENTIAL_EXEMPTION,
      children: [
        {
          path: '/residential-exemption/exemption-details',
          name: RouteNames.EXEMPTION_DETAILS,
          component: ExemptionDetails,
          meta: {
            step: 1,
            label: 'Verify Home Details',
            requiresAuth: true,
          },
        },
        {
          path: '/residential-exemption/exemption-review',
          name: RouteNames.EXEMPTION_REVIEW,
          component: ExemptionReview,
          meta: {
            step: 2,
            label: 'Review and Confirm',
            requiresAuth: true,
          },
        },
      ]
    },
    {
      // default/fallback route
      // must be last
      path: '/:catchAll(.*)',
      redirect: '/dashboard',
    },
  ]
}
