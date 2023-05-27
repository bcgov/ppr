// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '@/store/store'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Local Components
import { Parties } from '@/components/parties'
import { Stepper, StickyContainer } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import { AddSecuredPartiesAndDebtors } from '@/views/newRegistration'
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

setActivePinia(createPinia())
const store = useStore()

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
  router.push({ name: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS })

  return mount((AddSecuredPartiesAndDebtors as any), {
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

describe('Add Parties new registration component', () => {
  let wrapper: any
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeEach(async () => {
    await store.setRegistrationType(null)
    await store.setRegistrationFlowType(null)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('redirects to dashboard when store is not set', () => {
    wrapper = createComponent()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('renders Add Parties View with child components when store is set', async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = createComponent()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    expect(wrapper.findComponent(AddSecuredPartiesAndDebtors).exists()).toBe(true)
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
    expect(wrapper.findComponent(ButtonFooter).vm.$props.currentStepName).toBe(
      RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS
    )
    expect(wrapper.findComponent(Parties).exists()).toBe(true)
    expect(wrapper.find(header).exists()).toBe(true)
    expect(wrapper.find(title).exists()).toBe(true)
    expect(wrapper.find(titleInfo).exists()).toBe(true)
  })

  it('updates fee summary with registration length changes', async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
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
    await store.setLengthTrust(newLengthTrust1)
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
    await store.setLengthTrust(newLengthTrust2)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: newLengthTrust2.lifeInfinite,
      lifeYears: newLengthTrust2.lifeYears
    })
  })

  it('displays correct info based on registration type', async () => {
    for (let i = 0; i < RegistrationTypes.length; i++) {
      // skip dividers + other
      if (
        !RegistrationTypes[i].registrationTypeUI ||
        RegistrationTypes[i].registrationTypeUI === UIRegistrationTypes.OTHER
      ) {
        continue
      }
      await store.setRegistrationType(RegistrationTypes[i])
      await store.setRegistrationFlowType(RegistrationFlowType.NEW)
      wrapper = createComponent()
      await flushPromises()
      expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationType).toBe(
        RegistrationTypes[i].registrationTypeUI
      )
      // header
      expect(wrapper.find(header).text()).toContain(RegistrationTypes[i].registrationTypeUI)
      // title
      expect(wrapper.find(title).text()).toContain('Add Secured Parties and Debtors')
      // message
      expect(wrapper.find(titleInfo).text()).toContain(
        'Add the people and businesses who have an interest in this registration.'
      )
      wrapper.destroy()
    }
  })
})
