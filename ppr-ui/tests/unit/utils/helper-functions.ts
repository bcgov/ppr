import type { VueWrapper } from '@vue/test-utils';
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { MhApiStatusTypes, MhrSubTypes, ProductCode, RouteNames } from '@/enums'
import type { RouterMock } from 'vue-router-mock';
import { createRouterMock } from 'vue-router-mock'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import {
  mockMhrTransferCurrentHomeOwner,
  mockTransportPermitNewLocation,
  mockTransportPermitPreviousLocation
} from '../test-data'
import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import {
  AddCollateral,
  AddSecuredPartiesAndDebtors,
  AmendRegistration,
  ConfirmAmendment,
  ConfirmDischarge,
  ConfirmMHRSearch,
  ConfirmRenewal,
  Dashboard,
  DischargeRegistration, ExemptionDetails, ExemptionReview, Exemptions,
  HomeLocation,
  HomeOwners,
  LengthTrust,
  Login,
  MhrHistory,
  MhrInformation,
  MhrRegistration,
  MhrReviewConfirm,
  MHRSearch,
  MhrUnitNote,
  QsInformation, QsReviewConfirm,
  QsSelectAccess,
  RenewRegistration,
  ReviewConfirm,
  Search,
  Signin,
  Signout,
  SubmittingParty,
  UserAccess,
  YourHome
} from '@/pages'

const vuetify = createVuetify({ components, directives })


const store = useStore()

/**
 * Creates and mounts a test component.
 * @returns a Wrapper<any> object with the given parameters.
 */
export async function createComponent (
  component: any,
  props: Record<string, any> = {},
  initialRoute: RouteNames | null = null,
  query: Record<string, any> = {},
  optionalPlugins: Array<any> = []
): Promise<any> {
  // Set up mock router
  const mockRouter: RouterMock = createRouterMock({
    routes: [
      {
        // router.beforeEach() routes here:
        path: '/login',
        name: RouteNames.LOGIN,
        component: Login,
        props: true,
        meta: {
          requiresAuth: false,
          title: 'BC Registries Account Login',
        },
      },
      {
        // router.beforeEach() routes here:
        path: '/signin',
        name: RouteNames.SIGN_IN,
        component: Signin,
        props: true,
        meta: {
          requiresAuth: false,
        },
      },
      {
        // SbcHeader.logout() redirects here:
        path: '/signout',
        name: RouteNames.SIGN_OUT,
        component: Signout,
        props: true,
        meta: {
          requiresAuth: false,
        },
      },
      {
        path: '/dashboard',
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
        path: '/ppr/search',
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
    ],
    initialLocation: {
      name: initialRoute || RouteNames.DASHBOARD,
      query
    }
  })

  // Set up mock authentication
  setupMockUser()

  // Create a shim component that will wrap the component we want to test, to satisfy Vuetify's layout requirements.
  const shimComponent = {
    template: `
      <v-app>
        <component-name v-bind="props"/>
      </v-app>`,
    components: {
      'component-name': component
    },
    data () {
      return { props }
    }
  }

  return mount(shimComponent, {
    global: {
      plugins: [mockRouter, ...optionalPlugins, vuetify]
    }
  }).getComponent(component)
}

/**
 * Returns the last event for a given name, to be used for testing event propagation in response to component changes.
 *
 * @param wrapper the wrapper for the component that is being tested.
 * @param name the name of the event that is to be returned.
 *
 * @returns the value of the last named event for the wrapper.
 */
export function getLastEvent (wrapper: VueWrapper<any>, name: string): any {
  const eventsList: Array<any> = wrapper.emitted(name)
  if (!eventsList) {
    return null
  }
  const events: Array<any> = eventsList[eventsList.length - 1]
  return events[0]
}

/**
 * Utility function that keeps tests looking cleaner (via string template).
 * @param dataTestId - Name of 'data-test-id' attribute in the component that needs to be tested.
 */
export function getTestId (dataTestId: string) {
  return `[data-test-id='${dataTestId}']`
}

/**
 * Setup mock current user, auth and keycloak token.
 * Required when using a mount (vs. shallowMount) when creating components to test.
 *
 * @returns void
 */
export function setupMockUser (): void {
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')
  sessionStorage.setItem(SessionStorageKeys.AuthApiUrl, 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')
  sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUbWdtZUk0MnVsdUZ0N3FQbmUtcTEzdDUwa0JDbjF3bHF6dHN0UGdUM1dFIn0.eyJleHAiOjE2NDQ1MzYxMzEsImlhdCI6MTY0NDUxODEzMSwiYXV0aF90aW1lIjoxNjQ0NTE2NTM0LCJqdGkiOiIxZjc5OTkyOC05ODQwLTRlNzktYTEwZS1jMmI5ZTJjZTE3ZWQiLCJpc3MiOiJodHRwczovL2Rldi5vaWRjLmdvdi5iYy5jYS9hdXRoL3JlYWxtcy9mY2Ywa3BxciIsImF1ZCI6WyJwcHItc2VydmljZXMiLCJhY2NvdW50LXNlcnZpY2VzIiwiYWNjb3VudCJdLCJzdWIiOiI3NWMzMzE5Ni0zOTk3LTRkOTctODBlNi01ZGQyYWE1YmU5N2IiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJwcHItd2ViIiwibm9uY2UiOiIwNDRjYzAyOC01NTZmLTRmNDgtYWM0NS1jNzU5OGEwMWQ0YTgiLCJzZXNzaW9uX3N0YXRlIjoiOGFiNjZmMDktZWQyYi00ZGQ4LWE1YmYtM2NjYWI2MThlMzVhIiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJwdWJsaWNfdXNlciIsInBwciIsImVkaXQiLCJhY2NvdW50X2hvbGRlciIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCIsImZpcnN0bmFtZSI6IkJDUkVHMiBTdmV0bGFuYSIsInJvbGVzIjpbInB1YmxpY191c2VyIiwicHByIiwiZWRpdCIsImFjY291bnRfaG9sZGVyIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdLCJuYW1lIjoiQkNSRUcyIFN2ZXRsYW5hIEZPVVJURUVOIiwiaWRwX3VzZXJpZCI6IkhERjNEWVFFUUhQVU1VT01QUUMyQkFGSVJETFZPV0s2IiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYmNzYy9oZGYzZHlxZXFocHVtdW9tcHFjMmJhZmlyZGx2b3drNiIsImxvZ2luU291cmNlIjoiQkNTQyIsImxhc3RuYW1lIjoiRk9VUlRFRU4iLCJ1c2VybmFtZSI6ImJjc2MvaGRmM2R5cWVxaHB1bXVvbXBxYzJiYWZpcmRsdm93azYifQ.UUamIDN1LWms2oK5YG9yEmfen6ISFoY9AGw7ZJrsmDiElt0XwI_lj6DPYdMieXgXQ4Ji7jRVSMNhX4LfxpC1JipepUbI3kBLf0lelTudhZyD9MOg-VYaLAAEwAY57Z8h7EOCQp0PLS8NAMwNs90t4sJ449uZ3HprEMfMvkaZ0X3Cv495U0m5Qr-GDT7PHeLqkh3297gvxx3PdIGZIWcIwz-lFo8jNYxpEtY1LivZXnCsfrLDEW-vVK5kmnB1boIJksiUq8ATjF6F26B7ytBhE89SvolmA5nMkLiB-yusbSMY0ccxRWpPmX4MJ2yKuM6Sr6L6Dxrw_FWBHU1ThnnxUw')
}

/**
 * Setup mock Staff User, auth and keycloak token.
 * Required when using a mount (vs. shallowMount) when creating components to test.
 *
 * @returns void
 */
export function setupMockStaffUser (): void {
  setupMockUser()
  store.setAuthRoles(['staff', 'ppr_staff'])
}

export function setupMockLawyerOrNotary (): void {
  setupMockUser()
  store.setAuthRoles([])
  store.setUserProductSubscriptionsCodes([ProductCode.LAWYERS_NOTARIES])
}

/**
 * Setup the active transport permit by storing mock transport permit data into the store.
 *
 * @async
 * @function setupActiveTransportPermit
 * @returns {Promise<void>}
 */
export async function setupActiveTransportPermit (): Promise<void> {
  // parse permit data
  store.setMhrInformation({
    permitDateTime: '2024-02-05T08:40:53-08:00',
    permitExpiryDateTime: '2024-03-06T09:00:00-07:53',
    permitRegistrationNumber: '00502383',
    permitLandStatusConfirmation: true,
    permitStatus: MhApiStatusTypes.ACTIVE,
  })

  await store.setMhrTransportPermit({ key: 'landStatusConfirmation', value: true })
  await store.setMhrTransportPermit({ key: 'newLocation', value: mockTransportPermitNewLocation })
  await store.setMhrTransportPermit({ key: 'ownLand', value: true })
  await store.setMhrTransportPermitPreviousLocation(mockTransportPermitPreviousLocation)
  await store.setTransportPermitChangeAllowed(true)
}

/**
 * Adds a unique ID to each individual owner within the provided owner groups for UI tracking purposes.
 *
 * @param {Array} ownersGroups - An array of owner groups, where each group contains multiple owners.
 * @returns {Array<any>} The modified array of owner groups with unique IDs assigned to each owner.
 */
export function addIDsForOwners (ownersGroups): Array<any> {
  // Create an ID to each individual owner for UI Tracking
  ownersGroups.forEach(ownerGroup => {
    for (const [index, owner] of ownerGroup.owners.entries()) {
      owner.ownerId = ownerGroup.groupId + (index + 1)
    }
  })

  return ownersGroups
}

/**
 * Sets up the current home owners by first storing the provided mock data,
 * and then adding unique IDs to each owner for UI tracking. This function
 * waits for the store operations to complete.
 *
 * @returns {Promise<void>} A promise that resolves when the setup is complete.
 */
export async function setupCurrentHomeOwners (): Promise<void> {
  await store.setMhrTransferCurrentHomeOwnerGroups([mockMhrTransferCurrentHomeOwner])
  const homeOwnerWithIdsArray = addIDsForOwners([mockMhrTransferCurrentHomeOwner])
  await store.setMhrTransferHomeOwnerGroups(homeOwnerWithIdsArray)
}

/**
 * Sets up the current multiple home owners groups.
 *
 * This function creates two groups of mock home owner data and stores them
 * in the application state. It temporarily adds IDs to each owner for
 * compatibility with the current API requirements until the API updates
 * to include these IDs.
 *
 * @returns {Promise<void>} A promise that resolves when the setup is complete.
 */
export async function setupCurrentMultipleHomeOwnersGroups (): Promise<void> {
  // setup two groups so they can be shown in the table
  const currentHomeOwnersGroups = [
    mockMhrTransferCurrentHomeOwner,
    {
      ...mockMhrTransferCurrentHomeOwner,
      groupId: 2
    }
  ]

  await store.setMhrTransferCurrentHomeOwnerGroups(currentHomeOwnersGroups)
  const homeOwnerWithIdsArray = addIDsForOwners(currentHomeOwnersGroups)
  await store.setMhrTransferHomeOwnerGroups(homeOwnerWithIdsArray)
}

/**
 * Triggers unsaved changes in the application state.
 *
 * This function sets the unsaved changes flag to true in the store to
 * make the Transfer Details section visible, and waits for the next
 * DOM update cycle.
 *
 * @returns {Promise<void>} A promise that resolves when the unsaved changes flag is set.
 */
export async function triggerUnsavedChange (): Promise<void> {
  // set unsaved changes to make Transfer Details visible
  await store.setUnsavedChanges(true)
  await nextTick()
}

/**
 * Maps specific MHR subtypes to their corresponding product codes.
 *
 * @param {MhrSubTypes} subtype - The MHR subtype to be mapped.
 * @returns {ProductCode | undefined} The corresponding product code, or undefined if the subtype does not have a mapping.
 */
export function mapMhrTypeToProductCode(subtype: MhrSubTypes): ProductCode | undefined {
  switch (subtype) {
    case MhrSubTypes.LAWYERS_NOTARIES:
      return ProductCode.LAWYERS_NOTARIES;
    case MhrSubTypes.MANUFACTURER:
      return ProductCode.MANUFACTURER;
    case MhrSubTypes.DEALERS:
      return ProductCode.DEALERS;
    default:
      return undefined;
  }
}
