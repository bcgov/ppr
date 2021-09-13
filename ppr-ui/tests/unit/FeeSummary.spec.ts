// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { FeeSummary } from '@/composables/fees'
import { RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { UIRegistrationTypes } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

const newRegStandard = [
  UIRegistrationTypes.SECURITY_AGREEMENT,
  UIRegistrationTypes.REPAIRERS_LIEN,
  UIRegistrationTypes.MARRIAGE_MH,
  UIRegistrationTypes.SALE_OF_GOODS,
  UIRegistrationTypes.LAND_TAX_LIEN,
  UIRegistrationTypes.MANUFACTURED_HOME_LIEN,
  UIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN,
  UIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE,
  UIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN
]
const newRegMisc = [
  // miscelaneous registration cc
  UIRegistrationTypes.CARBON_TAX,
  UIRegistrationTypes.EXCISE_TAX,
  UIRegistrationTypes.FOREST,
  UIRegistrationTypes.INCOME_TAX,
  UIRegistrationTypes.INSURANCE_PREMIUM_TAX,
  UIRegistrationTypes.LOGGING_TAX,
  UIRegistrationTypes.MINERAL_LAND_TAX,
  UIRegistrationTypes.MOTOR_FUEL_TAX,
  UIRegistrationTypes.PROPERTY_TRANSFER_TAX,
  UIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX,
  UIRegistrationTypes.PROVINCIAL_SALES_TAX,
  UIRegistrationTypes.RURAL_PROPERTY_TAX,
  UIRegistrationTypes.SCHOOL_ACT,
  UIRegistrationTypes.OTHER,
  // miscelaneous registration other
  UIRegistrationTypes.LIEN_UNPAID_WAGES,
  UIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
  UIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
  UIRegistrationTypes.MAINTENANCE_LIEN,
  UIRegistrationTypes.PROCEEDS_CRIME_NOTICE
]
const newRegistrationTypes = [
  ...newRegStandard,
  ...newRegMisc
]

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  feeType: FeeSummaryTypes,
  registrationLength: RegistrationLengthI,
  registrationType: UIRegistrationTypes
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(FeeSummary, {
    localVue,
    propsData: {
      setFeeType: feeType,
      setRegistrationLength: registrationLength,
      setRegistrationType: registrationType
    },
    store,
    vuetify
  })
}

describe('FeeSummary component tests', () => {
  let wrapper: Wrapper<any>
  // registration length only effects the component when infinite/select years is selectable
  const registrationLength: RegistrationLengthI = {
    lifeInfinite: false,
    lifeYears: 0
  }
  beforeEach(async () => {
    // these props will be changed in each test
    wrapper = createComponent(
      FeeSummaryTypes.NEW,
      { ...registrationLength },
      newRegistrationTypes[0]
    )
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with correct values for new registrations', async () => {
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    for (let i = 0; i < newRegistrationTypes.length; i++) {
      await wrapper.setProps({
        setFeeType: FeeSummaryTypes.NEW,
        setRegistrationLength: { ...registrationLength },
        setRegistrationType: newRegistrationTypes[i]
      })
      expect(wrapper.vm.$data.feeType).toBe(FeeSummaryTypes.NEW)
      expect(wrapper.vm.$data.registrationLength).toEqual(registrationLength)
      expect(wrapper.vm.$data.registrationType).toBe(newRegistrationTypes[i])
      expect(wrapper.vm.$data.feeLabel).toBe(newRegistrationTypes[i])

      const noFeeStandard = [UIRegistrationTypes.LAND_TAX_LIEN, UIRegistrationTypes.MANUFACTURED_HOME_LIEN]
      if ([...newRegMisc, ...noFeeStandard].includes(newRegistrationTypes[i])) {
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(0)
        expect(wrapper.vm.$data.totalFees).toBe(0)
        expect(wrapper.vm.$data.totalAmount).toBe(0)
        expect(wrapper.vm.$data.isComplete).toBe(true)
        expect(wrapper.vm.$data.hintFee).toBe('Infinite Registration (default)')
      } else if (newRegistrationTypes[i] === UIRegistrationTypes.REPAIRERS_LIEN) {
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(5)
        expect(wrapper.vm.$data.totalAmount).toBe(6.5)
        expect(wrapper.vm.$data.isComplete).toBe(true)
        expect(wrapper.vm.$data.hintFee).toBe('180 Day Registration (default)')
      } else if (newRegistrationTypes[i] === UIRegistrationTypes.MARRIAGE_MH) {
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(10)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(10)
        expect(wrapper.vm.$data.totalAmount).toBe(11.5)
        expect(wrapper.vm.$data.isComplete).toBe(true)
        expect(wrapper.vm.$data.hintFee).toBe('Infinite Registration (default)')
      } else {
        // standard selectable years / selectable infinite
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(0)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(0)
        expect(wrapper.vm.$data.totalAmount).toBe(1.5)
        expect(wrapper.vm.$data.isComplete).toBe(false)
        expect(wrapper.vm.$data.hintFee).toBe('Select registration length')
        // select infinite
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: true,
            lifeYears: 0
          }
        })
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(500)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(500)
        expect(wrapper.vm.$data.totalAmount).toBe(501.5)
        expect(wrapper.vm.$data.isComplete).toBe(true)
        expect(wrapper.vm.$data.hintFee).toBe('Infinite Registration')
        // select 1 year
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 1
          }
        })
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(5)
        expect(wrapper.vm.$data.totalAmount).toBe(6.5)
        expect(wrapper.vm.$data.isComplete).toBe(true)
        expect(wrapper.vm.$data.hintFee).toBe('1 Year @ $5.00/year')
        // select multiple years
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 12
          }
        })
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(12)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(60)
        expect(wrapper.vm.$data.totalAmount).toBe(61.5)
        expect(wrapper.vm.$data.isComplete).toBe(true)
        expect(wrapper.vm.$data.hintFee).toBe('12 Years @ $5.00/year')
      }
    }
  })

  it('renders with correct values for total discharge', async () => {
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    for (let i = 0; i < newRegistrationTypes.length; i++) {
      await wrapper.setProps({
        setFeeType: FeeSummaryTypes.DISCHARGE,
        setRegistrationLength: null,
        setRegistrationType: newRegistrationTypes[i]
      })
      expect(wrapper.vm.$data.feeType).toBe(FeeSummaryTypes.DISCHARGE)
      expect(wrapper.vm.$data.registrationType).toBe(newRegistrationTypes[i])
      expect(wrapper.vm.$data.feeLabel).toBe('Total Discharge')
      expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(0)
      expect(wrapper.vm.$data.feeSummary.quantity).toBe(1)
      expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(0)
      expect(wrapper.vm.$data.totalFees).toBe(0)
      expect(wrapper.vm.$data.totalAmount).toBe(0)
      expect(wrapper.vm.$data.isComplete).toBe(true)
      expect(wrapper.vm.$data.hintFee).toBe('')
    }
  })

  it('renders with correct values for renewals', async () => {
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    for (let i = 0; i < newRegStandard.length; i++) {
      await wrapper.setProps({
        setFeeType: FeeSummaryTypes.RENEW,
        setRegistrationLength: { ...registrationLength },
        setRegistrationType: newRegStandard[i]
      })
      expect(wrapper.vm.$data.feeType).toBe(FeeSummaryTypes.RENEW)
      expect(wrapper.vm.$data.registrationLength).toEqual(registrationLength)
      expect(wrapper.vm.$data.registrationType).toBe(newRegStandard[i])
      expect(wrapper.vm.$data.feeLabel).toBe('Renewal')

      if (newRegistrationTypes[i] === UIRegistrationTypes.REPAIRERS_LIEN) {
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(5)
        expect(wrapper.vm.$data.totalAmount).toBe(6.5)
        expect(wrapper.vm.$data.isComplete).toBe(true)
      } else {
        // standard selectable years / selectable infinite
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(0)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(0)
        expect(wrapper.vm.$data.totalAmount).toBe(1.5)
        expect(wrapper.vm.$data.isComplete).toBe(false)
        // select infinite
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: true,
            lifeYears: 0
          }
        })
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(500)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(500)
        expect(wrapper.vm.$data.totalAmount).toBe(501.5)
        expect(wrapper.vm.$data.isComplete).toBe(true)
        // select 1 year
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 1
          }
        })
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(5)
        expect(wrapper.vm.$data.totalAmount).toBe(6.5)
        expect(wrapper.vm.$data.isComplete).toBe(true)
        // select multiple years
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 12
          }
        })
        expect(wrapper.vm.$data.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.$data.feeSummary.quantity).toBe(12)
        expect(wrapper.vm.$data.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.$data.totalFees).toBe(60)
        expect(wrapper.vm.$data.totalAmount).toBe(61.5)
        expect(wrapper.vm.$data.isComplete).toBe(true)
      }
    }
  })

})
