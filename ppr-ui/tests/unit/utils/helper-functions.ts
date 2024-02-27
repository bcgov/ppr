import { mount, VueWrapper } from '@vue/test-utils'
import { useStore } from '@/store/store'
import { MhApiStatusTypes, ProductCode, RouteNames } from '@/enums'
import { createRouterMock, injectRouterMock, RouterMock } from 'vue-router-mock'
import { routes } from '@/router'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { mockTransportPermitNewLocation } from '../test-data'

const store = useStore()

/**
 * Creates and mounts a test component.
 * @returns a Wrapper<any> object with the given parameters.
 */
export async function createComponent (
  component: any,
  props: Record<string, any> = {},
  initialRoute: RouteNames | null = null,
  query: Record<string, any> = {}
): Promise<any> {
  // Set up mock router
  const mockRouter: RouterMock = createRouterMock({
    routes: routes,
    initialLocation: {
      name: initialRoute || RouteNames.DASHBOARD,
      query
    }
  })
  injectRouterMock(mockRouter)

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
      plugins: [mockRouter]
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
}
