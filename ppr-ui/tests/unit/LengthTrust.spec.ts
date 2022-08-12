// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Local Components
import { LengthTrust } from '@/views'
import { ButtonFooter, Stepper, StickyContainer } from '@/components/common'
import { RegistrationLengthTrust } from '@/components/registration'
// Local types/helpers
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { APIRegistrationTypes, RegistrationFlowType, RouteNames, StatementTypes, UIRegistrationTypes } from '@/enums'
import { RegistrationTypes } from '@/resources'
import { LengthTrustIF } from '@/interfaces'
// unit test helpers/data
import mockRouter from './MockRouter'
import { mockedSelectSecurityAgreement } from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const header = '#registration-header'
const title = '.sub-header'
const titleInfo = '.sub-header-info'

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
    wrapper?.destroy() // eslint-disable-line no-unused-expressions
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
    expect(wrapper.findComponent(ButtonFooter).vm.$props.currentStepName).toBe(RouteNames.LENGTH_TRUST)
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
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
      if (RegistrationTypes[i].registrationTypeAPI === APIRegistrationTypes.SECURITY_AGREEMENT) {
        expect(wrapper.find(title).text()).toContain('Registration Length and Trust Indenture')
      } else if (RegistrationTypes[i].registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN) {
        expect(wrapper.find(title).text()).toContain('Terms of Repairers Lien')
      } else {
        expect(wrapper.find(title).text()).toContain('Registration Length')
      }
      // message
      const infiniteDefaultFree = [
        APIRegistrationTypes.LAND_TAX_LIEN,
        APIRegistrationTypes.MANUFACTURED_HOME_LIEN,
        APIRegistrationTypes.INSURANCE_PREMIUM_TAX,
        APIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX,
        APIRegistrationTypes.FOREST,
        APIRegistrationTypes.LOGGING_TAX,
        APIRegistrationTypes.CARBON_TAX,
        APIRegistrationTypes.RURAL_PROPERTY_TAX,
        APIRegistrationTypes.PROVINCIAL_SALES_TAX,
        APIRegistrationTypes.INCOME_TAX,
        APIRegistrationTypes.MOTOR_FUEL_TAX,
        APIRegistrationTypes.EXCISE_TAX,
        APIRegistrationTypes.LIEN_UNPAID_WAGES,
        APIRegistrationTypes.PROCEEDS_CRIME_NOTICE,
        APIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
        APIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
        APIRegistrationTypes.MAINTENANCE_LIEN,
        APIRegistrationTypes.OTHER,
        APIRegistrationTypes.SCHOOL_ACT,
        APIRegistrationTypes.PROPERTY_TRANSFER_TAX,
        APIRegistrationTypes.MINERAL_LAND_TAX,
        APIRegistrationTypes.TOBACCO_TAX,
        APIRegistrationTypes.SPECULATION_VACANCY_TAX
      ]
      if (RegistrationTypes[i].registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN) {
        expect(wrapper.find(titleInfo).text()).toContain('Enter the amount of the Lien and the date the vehicle')
      } else if (RegistrationTypes[i].registrationTypeAPI === APIRegistrationTypes.MARRIAGE_MH) {
        expect(wrapper.find(titleInfo).text()).toContain('infinite. There is a $10.00 fee for this registration.')
      } else if (infiniteDefaultFree.includes(RegistrationTypes[i].registrationTypeAPI)) {
        expect(wrapper.find(titleInfo).text()).toContain('infinite. There is no fee for this registration.')
      } else {
        expect(wrapper.find(titleInfo).text()).toContain(
          'Enter the length of time you want the ' + RegistrationTypes[i].registrationTypeUI
        )
      }

      wrapper.destroy()
    }
  })
})
