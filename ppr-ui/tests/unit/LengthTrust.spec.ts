// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// Components
import { LengthTrust } from '@/views'
import { ButtonFooter, Stepper, StickyContainer } from '@/components/common'
import { RegistrationLengthTrust } from '@/components/registration'

// Other
import { RegistrationFlowType, RouteNames } from '@/enums'
import mockRouter from './MockRouter'
import { mockedSelectSecurityAgreement } from './test-data'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const cancelBtn: string = '#reg-cancel-btn'
const saveBtn: string = '#reg-save-btn'
const saveResumeBtn: string = '#reg-save-resume-btn'
const backBtn: string = '#reg-back-btn'
const nextBtn: string = '#reg-next-btn'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  // Prevent the warning "[Vuetify] Unable to locate target [data-app]"
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({ name: RouteNames.LENGTH_TRUST })

  return mount(LengthTrust, {
    localVue,
    propsData: {
      appReady: true,
      isJestRunning: true
    },
    router,
    store,
    vuetify
  })
}

describe('Length and Trust Indenture new registration component', () => {
  let wrapper: any
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', null)
    await store.dispatch('setRegistrationFlowType', null)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('redirects to dashboard when store is not set', () => {
    wrapper = createComponent()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('renders Length Trust View with child components when store is set', async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    wrapper = createComponent()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.LENGTH_TRUST)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    expect(wrapper.findComponent(LengthTrust).exists()).toBe(true)
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(false)
    // check props?
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    // check props?
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
  })
  // test off button emits
  // test off registration type differences
  // test off registration length changing
})
