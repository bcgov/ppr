// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import { TiptapVuetifyPlugin } from 'tiptap-vuetify'

// Local Components
import { Collateral } from '@/components/collateral'
import { Stepper, StickyContainer } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import AddCollateral from '@/views/newRegistration/AddCollateral.vue'
// Local types/helpers
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { RegistrationFlowType, RouteNames, StatementTypes, UIRegistrationTypes } from '@/enums'
import { RegistrationTypes } from '@/resources'
import { LengthTrustIF } from '@/interfaces'
// unit test helpers/data
import mockRouter from './MockRouter'
import { mockedSelectSecurityAgreement } from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
Vue.use(TiptapVuetifyPlugin, {
  // the next line is important! You need to provide the Vuetify Object to this place.
  vuetify, // same as "vuetify: vuetify"
  // optional, default to 'md' (default vuetify icons before v2.0.0)
  iconsGroup: 'mdi'
})
const store = getVuexStore()

// Input field selectors / buttons
const header = '#registration-header'
const title: string = '.sub-header'
const titleInfo: string = '.sub-header-info'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  // Prevent the warning "[Vuetify] Unable to locate target [data-app]"
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({ name: RouteNames.ADD_COLLATERAL })

  return mount((AddCollateral as any), {
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

describe('Add Collateral new registration component', () => {
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

  it('renders Add Collateral View with child components when store is set', async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    wrapper = createComponent()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.ADD_COLLATERAL)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    expect(wrapper.findComponent(AddCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.NEW)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: false,
      lifeYears: 0
    })
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationType).toBe(
      UIRegistrationTypes.SECURITY_AGREEMENT
    )
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(false)
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.findComponent(ButtonFooter).vm.$props.currentStatementType).toBe(StatementTypes.FINANCING_STATEMENT)
    expect(wrapper.findComponent(ButtonFooter).vm.$props.currentStepName).toBe(RouteNames.ADD_COLLATERAL)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.find(header).exists()).toBe(true)
    expect(wrapper.find(title).exists()).toBe(true)
    expect(wrapper.find(titleInfo).exists()).toBe(true)
  })

  it('updates fee summary with registration length changes', async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    wrapper = createComponent()
    await flushPromises()
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: false,
      lifeYears: 0
    })
    const newLengthTrust1: LengthTrustIF = {
      valid: true,
      trustIndenture: false,
      lifeInfinite: true,
      lifeYears: 0
    }
    await store.dispatch('setLengthTrust', newLengthTrust1)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: newLengthTrust1.lifeInfinite,
      lifeYears: newLengthTrust1.lifeYears
    })
    const newLengthTrust2: LengthTrustIF = {
      valid: true,
      trustIndenture: false,
      lifeInfinite: true,
      lifeYears: 0
    }
    await store.dispatch('setLengthTrust', newLengthTrust2)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: newLengthTrust2.lifeInfinite,
      lifeYears: newLengthTrust2.lifeYears
    })
  })

  it('displays correct info based on registration type', async () => {
    jest.setTimeout(30000)
    for (let i = 0; i < RegistrationTypes.length; i++) {
      // skip dividers + other
      if (
        !RegistrationTypes[i].registrationTypeUI ||
        RegistrationTypes[i].registrationTypeUI === UIRegistrationTypes.OTHER
      ) {
        continue
      }
      await store.dispatch('setRegistrationType', RegistrationTypes[i])
      await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
      wrapper = createComponent()
      await flushPromises()
      expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationType).toBe(
        RegistrationTypes[i].registrationTypeUI
      )
      // header
      expect(wrapper.find(header).text()).toContain(RegistrationTypes[i].registrationTypeUI)
      // title
      expect(wrapper.find(title).text()).toContain('Add Collateral')
      // message
      expect(wrapper.find(titleInfo).text()).toContain(
        `Add the collateral for this ${RegistrationTypes[i].registrationTypeUI} registration.`
      )
      wrapper.destroy()
    }
  })
})
