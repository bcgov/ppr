// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import VueRouter from 'vue-router'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// local components
import { MhrRegistration } from '@/views'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import { Stepper, StickyContainer } from '@/components/common'
import { MhrRegistrationType } from '@/resources'
import { defaultFlagSet } from '@/utils'
import mockRouter from './MockRouter'
import { RouteNames } from '@/enums'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { mockedManufacturerAuthRoles } from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({
    name: RouteNames.YOUR_HOME
  })

  document.body.setAttribute('data-app', 'true')
  return mount((MhrRegistration as any), {
    localVue,
    store,
    propsData: {
      appReady: true
    },
    vuetify,
    router
  })
}

describe('Mhr Registration', () => {
  let wrapper: Wrapper<any>
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeEach(async () => {
    // Staff with MHR enabled
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setRegistrationType(MhrRegistrationType)

    wrapper = createComponent()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays the Mhr Registration View', async () => {
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
    expect(wrapper.find('#registration-header').text()).toBe('Manufactured Home Registration')
  })

  it('renders and displays the correct sub components', async () => {
    // Stepper
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    // Action button footers
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })
})

describe('Mhr Manufacturer Registration', () => {
  let wrapper: Wrapper<any>
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeEach(async () => {
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)

    wrapper = createComponent()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays the Mhr Registration View', async () => {
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
    expect(wrapper.find('#registration-header').text()).toBe('Manufactured Home Registration')
  })

  it('renders and displays the correct sub components', async () => {
    // Stepper
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    // Action button footers
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })
})
