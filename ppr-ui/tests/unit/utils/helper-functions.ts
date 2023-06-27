import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import mockRouter from '../MockRouter'
import { useStore } from '@/store/store'
import { createPinia, setActivePinia } from 'pinia'

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

/**
 * Returns the last event for a given name, to be used for testing event propagation in response to component changes.
 *
 * @param wrapper the wrapper for the component that is being tested.
 * @param name the name of the event that is to be returned.
 *
 * @returns the value of the last named event for the wrapper.
 */
export function getLastEvent (wrapper: Wrapper<any>, name: string): any {
  const eventsList: Array<any> = wrapper.emitted(name)
  if (!eventsList) {
    return null
  }
  const events: Array<any> = eventsList[eventsList.length - 1]
  return events[0]
}

/**
 * Utility function that mocks the `IntersectionObserver` API. Necessary for components that rely
 * on it, otherwise the tests will crash. Recommended to execute inside `beforeEach`.
 * @param intersectionObserverMock - Parameter that is sent to the `Object.defineProperty`
 * overwrite method. `jest.fn()` mock functions can be passed here if the goal is to not only
 * mock the intersection observer, but its methods.
 */
export function setupIntersectionObserverMock ({
  root = null,
  rootMargin = '',
  thresholds = [],
  disconnect = () => null,
  observe = () => null,
  takeRecords = () => [],
  unobserve = () => null
} = {}): void {
  class MockIntersectionObserver implements IntersectionObserver {
    readonly root: Element | null = root
    readonly rootMargin: string = rootMargin
    readonly thresholds: ReadonlyArray < number > = thresholds
    disconnect: () => void = disconnect
    observe: (target: Element) => void = observe
    takeRecords: () => IntersectionObserverEntry[] = takeRecords
    unobserve: (target: Element) => void = unobserve
  }

  Object.defineProperty(
    window,
    'IntersectionObserver', {
      writable: true,
      configurable: true,
      value: MockIntersectionObserver
    }
  )
}

/**
 * Utility function that keeps tests looking cleaner (via string template).
 * @param dataTestId - Name of 'data-test-id' attribute in the component that needs to be tested.
 */
export function getTestId (dataTestId: string) {
  return `[data-test-id='${dataTestId}']`
}

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
export function createComponent (component: any, props: any): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  // Prevent the warning "[Vuetify] Unable to locate target [data-app]"
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()

  return mount((component as any), {
    localVue,
    propsData: props,
    router,
    store,
    vuetify
  })
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
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')
}
