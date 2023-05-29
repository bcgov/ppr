// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { FeeSummary } from '@/composables/fees'
import { FeeSummaryI, RegistrationLengthI } from '@/composables/fees/interfaces' // eslint-disable-line no-unused-vars
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { ApiTransferTypes, UIRegistrationTypes, UITransferTypes } from '@/enums'
import { StateModelIF } from '@/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces' // eslint-disable-line no-unused-vars

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

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
  UIRegistrationTypes.SPECULATION_VACANCY_TAX,
  UIRegistrationTypes.TOBACCO_TAX,
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
const renewRegistrationTypes = [
  UIRegistrationTypes.SECURITY_AGREEMENT,
  UIRegistrationTypes.REPAIRERS_LIEN,
  UIRegistrationTypes.SALE_OF_GOODS,
  UIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN,
  UIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE,
  UIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN
]

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  feeType: FeeSummaryTypes,
  registrationLength: RegistrationLengthI,
  registrationType: UIRegistrationTypes,
  feeOverride: FeeSummaryI = null
): Wrapper<any> {
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((FeeSummary as any), {
    localVue,
    propsData: {
      setFeeType: feeType,
      setRegistrationLength: registrationLength,
      setRegistrationType: registrationType,
      setFeeOverride: feeOverride
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
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 3,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.setStaffPayment({ isPriority: false } as StaffPaymentIF)
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
        setRegistrationType: newRegistrationTypes[i],
        setFeeOverride: null
      })
      expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.NEW)
      expect(wrapper.vm.registrationLength).toEqual(registrationLength)
      expect(wrapper.vm.registrationType).toBe(newRegistrationTypes[i])
      expect(wrapper.vm.feeLabel).toBe(newRegistrationTypes[i])

      const noFeeStandard = [UIRegistrationTypes.LAND_TAX_LIEN, UIRegistrationTypes.MANUFACTURED_HOME_LIEN]
      if ([...newRegMisc, ...noFeeStandard].includes(newRegistrationTypes[i])) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(0)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration (default)')
        // check renders the same for non billable
        await wrapper.setProps({ setFeeOverride: { feeAmount: 0, serviceFee: 4 } })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(0)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration (default)')
      } else if (newRegistrationTypes[i] === UIRegistrationTypes.REPAIRERS_LIEN) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(5)
        expect(wrapper.vm.totalAmount).toBe(6.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('180 Day Registration (default)')
        // check for non billable user
        await wrapper.setProps({ setFeeOverride: { feeAmount: 0, serviceFee: 4 } })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(4)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(4)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('180 Day Registration (default)')
      } else if (newRegistrationTypes[i] === UIRegistrationTypes.MARRIAGE_MH) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(10)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(10)
        expect(wrapper.vm.totalAmount).toBe(11.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration (default)')
        // check for non billable user
        await wrapper.setProps({ setFeeOverride: { feeAmount: 0, serviceFee: 1 } })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration (default)')
      } else {
        // standard selectable years / selectable infinite
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(0)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1.5)
        expect(wrapper.vm.isComplete).toBe(false)
        expect(wrapper.vm.hintFee).toBe('Select registration length')
        // select infinite
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: true,
            lifeYears: 0
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(500)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(500)
        expect(wrapper.vm.totalAmount).toBe(501.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration')
        // select 1 year
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 1
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(5)
        expect(wrapper.vm.totalAmount).toBe(6.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('1 Year @ $5.00/year')
        // select multiple years
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 12
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(12)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(60)
        expect(wrapper.vm.totalAmount).toBe(61.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('12 Years @ $5.00/year')

        // check for non billable user
        await wrapper.setProps({
          setFeeType: FeeSummaryTypes.NEW,
          setRegistrationLength: { ...registrationLength },
          setRegistrationType: newRegistrationTypes[i],
          setFeeOverride: { feeAmount: 0, serviceFee: 2.5 }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(0)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(2.5)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(2.5)
        expect(wrapper.vm.isComplete).toBe(false)
        expect(wrapper.vm.hintFee).toBe('Select registration length')
        // select infinite
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: true,
            lifeYears: 0
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(2.5)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(2.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration')
        // select 1 year
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 1
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(2.5)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(2.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('1 Year @ $0.00/year')
        // select multiple years
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 5
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(5)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(2.5)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(2.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('5 Years @ $0.00/year')
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
      expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.DISCHARGE)
      expect(wrapper.vm.registrationType).toBe(newRegistrationTypes[i])
      expect(wrapper.vm.feeLabel).toBe('Total Discharge')
      expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
      expect(wrapper.vm.feeSummary.quantity).toBe(1)
      expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
      expect(wrapper.vm.totalFees).toBe(0)
      expect(wrapper.vm.totalAmount).toBe(0)
      expect(wrapper.vm.isComplete).toBe(true)
      expect(wrapper.vm.hintFee).toBe('')
      // check renders the same for non billable
      await wrapper.setProps({ setFeeOverride: { feeAmount: 0, serviceFee: 1 } })
      expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.DISCHARGE)
      expect(wrapper.vm.registrationType).toBe(newRegistrationTypes[i])
      expect(wrapper.vm.feeLabel).toBe('Total Discharge')
      expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
      expect(wrapper.vm.feeSummary.quantity).toBe(1)
      expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
      expect(wrapper.vm.totalFees).toBe(0)
      expect(wrapper.vm.totalAmount).toBe(0)
      expect(wrapper.vm.isComplete).toBe(true)
      expect(wrapper.vm.hintFee).toBe('')
    }
  })

  it('renders with correct values for renewals', async () => {
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    for (let i = 0; i < renewRegistrationTypes.length; i++) {
      await wrapper.setProps({
        setFeeType: FeeSummaryTypes.RENEW,
        setRegistrationLength: { ...registrationLength },
        setRegistrationType: renewRegistrationTypes[i],
        setFeeOverride: null
      })
      expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.RENEW)
      expect(wrapper.vm.registrationLength).toEqual(registrationLength)
      expect(wrapper.vm.registrationType).toBe(renewRegistrationTypes[i])
      expect(wrapper.vm.feeLabel).toBe('Registration Renewal')

      if (newRegistrationTypes[i] === UIRegistrationTypes.REPAIRERS_LIEN) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(5)
        expect(wrapper.vm.totalAmount).toBe(6.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('180 Day Registration (default)')
        // check values for non billable
        await wrapper.setProps({ setFeeOverride: { feeAmount: 0, serviceFee: 1 } })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('180 Day Registration (default)')
      } else {
        // standard selectable years / selectable infinite
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(0)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1.5)
        expect(wrapper.vm.isComplete).toBe(false)
        expect(wrapper.vm.hintFee).toBe('Select registration renewal length')
        // select infinite
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: true,
            lifeYears: 0
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(500)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(500)
        expect(wrapper.vm.totalAmount).toBe(501.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration')
        // select 1 year
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 1
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(5)
        expect(wrapper.vm.totalAmount).toBe(6.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('1 Year @ $5.00/year')
        // select multiple years
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 12
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(12)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(60)
        expect(wrapper.vm.totalAmount).toBe(61.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('12 Years @ $5.00/year')

        // check values for non billable
        await wrapper.setProps({
          setFeeType: FeeSummaryTypes.RENEW,
          setRegistrationLength: { ...registrationLength },
          setRegistrationType: renewRegistrationTypes[i],
          setFeeOverride: { feeAmount: 0, serviceFee: 1 }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(0)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1)
        expect(wrapper.vm.isComplete).toBe(false)
        expect(wrapper.vm.hintFee).toBe('Select registration renewal length')
        // select infinite
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: true,
            lifeYears: 0
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration')
        // select 1 year
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 1
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('1 Year @ $0.00/year')
        // select multiple years
        await wrapper.setProps({
          setRegistrationLength: {
            lifeInfinite: false,
            lifeYears: 12
          }
        })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(12)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('12 Years @ $0.00/year')
      }
    }
  })

  it('renders with correct values for amendment fee', async () => {
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    for (let i = 0; i < newRegStandard.length; i++) {
      await wrapper.setProps({
        setFeeType: FeeSummaryTypes.AMEND,
        setRegistrationLength: null,
        setRegistrationType: newRegStandard[i],
        setFeeOverride: null
      })
      expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.AMEND)
      expect(wrapper.vm.registrationType).toBe(newRegStandard[i])
      expect(wrapper.vm.feeLabel).toBe('Registration Amendment')
      if (UIRegistrationTypes.LAND_TAX_LIEN !== newRegStandard[i]) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(10)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(10)
        expect(wrapper.vm.totalAmount).toBe(11.5)
        // check values for non billable
        await wrapper.setProps({ setFeeOverride: { feeAmount: 0, serviceFee: 1 } })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1)
      } else {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(0)
        // check values for non billable
        await wrapper.setProps({ setFeeOverride: { feeAmount: 0, serviceFee: 1 } })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(0)
      }
      expect(wrapper.vm.isComplete).toBe(true)
      expect(wrapper.vm.hintFee).toBe('')
    }
  })

  it('renders with correct values for amendment no fee', async () => {
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    for (let i = 0; i < newRegMisc.length; i++) {
      await wrapper.setProps({
        setFeeType: FeeSummaryTypes.AMEND,
        setRegistrationLength: null,
        setRegistrationType: newRegMisc[i],
        setFeeOverride: null
      })
      expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.AMEND)
      expect(wrapper.vm.registrationType).toBe(newRegMisc[i])
      expect(wrapper.vm.feeLabel).toBe('Registration Amendment')
      expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
      expect(wrapper.vm.feeSummary.quantity).toBe(1)
      expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
      expect(wrapper.vm.totalFees).toBe(0)
      expect(wrapper.vm.totalAmount).toBe(0)
      expect(wrapper.vm.isComplete).toBe(true)
      expect(wrapper.vm.hintFee).toBe('')
      // check values for non billable
      await wrapper.setProps({ setFeeOverride: { feeAmount: 0, serviceFee: 1 } })
      expect(wrapper.vm.feeLabel).toBe('Registration Amendment')
      expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
      expect(wrapper.vm.feeSummary.quantity).toBe(1)
      expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
      expect(wrapper.vm.totalFees).toBe(0)
      expect(wrapper.vm.totalAmount).toBe(0)
      expect(wrapper.vm.isComplete).toBe(true)
      expect(wrapper.vm.hintFee).toBe('')
    }
  })

  it('renders with correct values for a MHR Search', async () => {
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHSEARCH,
      setFeeQuantity: 1,
      setRegistrationLength: null,
      setRegistrationType: null
    })
    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHSEARCH)
    expect(wrapper.vm.registrationType).toBe(null)
    expect(wrapper.vm.feeLabel).toBe('Manufactured Home search')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(7)
    expect(wrapper.vm.feeSummary.quantity).toBe(1)
    expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
    expect(wrapper.vm.totalFees).toBe(7)
    expect(wrapper.vm.totalAmount).toBe(8.5)
    expect(wrapper.vm.isComplete).toBe(true)
    expect(wrapper.vm.hintFee).toBe('')
  })

  it('renders with correct values for a MHR Search and Combined Search', async () => {
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHSEARCH,
      setFeeQuantity: 1,
      setRegistrationLength: null,
      setRegistrationType: null,
      additionalFees: {
        feeType: FeeSummaryTypes.MHR_COMBINED_SEARCH,
        quantity: 1
      }
    })
    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHSEARCH)
    expect(wrapper.vm.registrationType).toBe(null)
    expect(wrapper.vm.feeLabel).toBe('Manufactured Home search')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(7)
    expect(wrapper.vm.feeSummary.quantity).toBe(1)
    expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)

    expect(wrapper.vm.additionalFeeLabel).toBe('Combined Home and Lien search')
    expect(wrapper.vm.additionalFeeSummary.feeAmount).toBe(12)
    expect(wrapper.vm.additionalFeeSummary.quantity).toBe(1)
    expect(wrapper.vm.additionalFeeSummary.serviceFee).toBe(1.5)

    expect(wrapper.vm.totalFees).toBe(7)
    expect(wrapper.vm.totalAdditionalFees).toBe(12)

    expect(wrapper.vm.totalAmount).toBe(20.5)
    expect(wrapper.vm.isComplete).toBe(true)
    expect(wrapper.vm.hintFee).toBe('')
  })

  it('renders with correct values for a MHR Search and Combined Search with multiples', async () => {
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHSEARCH,
      setFeeQuantity: 2,
      setRegistrationLength: null,
      setRegistrationType: null,
      additionalFees: {
        feeType: FeeSummaryTypes.MHR_COMBINED_SEARCH,
        quantity: 3
      }
    })
    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHSEARCH)
    expect(wrapper.vm.registrationType).toBe(null)
    expect(wrapper.vm.feeLabel).toBe('Manufactured Home search')
    expect(wrapper.find('#quantity-label').text()).toBe('2 @ $7.00 each')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(7)
    expect(wrapper.vm.feeSummary.quantity).toBe(2)
    expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)

    expect(wrapper.vm.additionalFeeLabel).toBe('Combined Home and Lien search')
    expect(wrapper.find('#additional-quantity-label').text()).toBe('3 @ $12.00 each')
    expect(wrapper.vm.additionalFeeSummary.feeAmount).toBe(12)
    expect(wrapper.vm.additionalFeeSummary.quantity).toBe(3)
    expect(wrapper.vm.additionalFeeSummary.serviceFee).toBe(1.5)

    expect(wrapper.vm.totalFees).toBe(14)
    expect(wrapper.vm.totalAdditionalFees).toBe(36)

    expect(wrapper.vm.totalAmount).toBe(51.5)
    expect(wrapper.vm.isComplete).toBe(true)
    expect(wrapper.vm.hintFee).toBe('')
  })

  it('renders with correct values for a MHR Search as Staff', async () => {
    const state = store.getStateModel as StateModelIF
    await store.setAuthRoles(['staff'])
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHSEARCH,
      setFeeQuantity: 1,
      setRegistrationLength: null,
      setRegistrationType: null
    })
    await nextTick()

    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHSEARCH)
    expect(wrapper.vm.feeLabel).toBe('Manufactured Home search')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
    expect(wrapper.vm.feeSummary.quantity).toBe(1)
    expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
    expect(wrapper.vm.totalFees).toBe(0)
    expect(wrapper.vm.totalAmount).toBe(0)
    expect(wrapper.vm.isComplete).toBe(true)
    expect(wrapper.vm.hintFee).toBe('')
  })

  it('renders with correct values for a MHR Search as Staff on behalf of a client', async () => {
    await store.setAuthRoles(['staff'])
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHSEARCH,
      setFeeQuantity: 1,
      setRegistrationLength: null,
      setRegistrationType: null,
      setStaffReg: true,
      setStaffClientPayment: true
    })
    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHSEARCH)
    expect(wrapper.vm.registrationType).toBe(null)
    expect(wrapper.vm.feeLabel).toBe('Manufactured Home search')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(10)
    expect(wrapper.vm.feeSummary.quantity).toBe(1)
    expect(wrapper.find('#processing-fee-summary').exists()).toBe(false)
    expect(wrapper.vm.totalFees).toBe(10)
    expect(wrapper.vm.totalAmount).toBe(10)
    expect(wrapper.vm.isComplete).toBe(true)
    expect(wrapper.vm.hintFee).toBe('')
  })

  it('renders priority fee for a MHR Search as Staff on behalf of a client', async () => {
    await store.setAuthRoles(['staff'])
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHSEARCH,
      setFeeQuantity: 1,
      setRegistrationLength: null,
      setRegistrationType: null,
      setStaffReg: true,
      setStaffClientPayment: true
    })
    await store.setStaffPayment({ isPriority: true })
    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHSEARCH)
    expect(wrapper.vm.registrationType).toBe(null)
    expect(wrapper.vm.feeLabel).toBe('Manufactured Home search')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(10)
    expect(wrapper.vm.feeSummary.quantity).toBe(1)
    expect(wrapper.find('#processing-fee-summary').exists()).toBe(false)
    expect(wrapper.vm.totalFees).toBe(10)
    expect(wrapper.vm.totalAmount).toBe(110)
    expect(wrapper.vm.isComplete).toBe(true)
    expect(wrapper.vm.hintFee).toBe('')
    expect(wrapper.find('#priority-fee').exists()).toBe(true)
    expect(wrapper.find('#priority-fee').text()).toContain('Priority Fee')
    expect(wrapper.find('#priority-fee').text()).toContain('$ 100.00')
  })

  it('renders certify search fee for a MHR Search as Staff on behalf of a client', async () => {
    const state = store.getStateModel as StateModelIF
    await store.setAuthRoles(['staff'])
    state.search.searchCertified = true
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHSEARCH,
      setFeeQuantity: 1,
      setRegistrationLength: null,
      setRegistrationType: null,
      setStaffReg: true,
      setStaffClientPayment: true
    })
    await store.setStaffPayment()
    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHSEARCH)
    expect(wrapper.vm.registrationType).toBe(null)
    expect(wrapper.vm.feeLabel).toBe('Manufactured Home search')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(10)
    expect(wrapper.vm.feeSummary.quantity).toBe(1)
    expect(wrapper.find('#processing-fee-summary').exists()).toBe(false)
    expect(wrapper.vm.totalFees).toBe(10)
    expect(wrapper.vm.totalAmount).toBe(35)
    expect(wrapper.vm.isComplete).toBe(true)
    expect(wrapper.vm.hintFee).toBe('')
    expect(wrapper.find('#priority-fee').exists()).toBe(false)
    expect(wrapper.find('#certify-fee').exists()).toBe(true)
    expect(wrapper.find('#certify-fee').text()).toContain('Certified search')
    expect(wrapper.find('#certify-fee').text()).toContain('$ 25.00')
  })

  it('renders certify search and priority fee for a MHR Search as Staff on behalf of a client', async () => {
    const state = store.getStateModel as StateModelIF
    await store.setAuthRoles(['staff'])
    state.search.searchCertified = true
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHSEARCH,
      setFeeQuantity: 1,
      setRegistrationLength: null,
      setRegistrationType: null,
      setStaffReg: true,
      setStaffClientPayment: true
    })
    await store.setStaffPayment({ isPriority: true })
    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHSEARCH)
    expect(wrapper.vm.registrationType).toBe(null)
    expect(wrapper.vm.feeLabel).toBe('Manufactured Home search')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(10)
    expect(wrapper.vm.feeSummary.quantity).toBe(1)
    expect(wrapper.find('#processing-fee-summary').exists()).toBe(false)
    expect(wrapper.vm.totalFees).toBe(10)
    expect(wrapper.vm.totalAmount).toBe(135)
    expect(wrapper.vm.isComplete).toBe(true)
    expect(wrapper.vm.hintFee).toBe('')
    expect(wrapper.find('#priority-fee').exists()).toBe(true)
    expect(wrapper.find('#priority-fee').text()).toContain('Priority Fee')
    expect(wrapper.find('#priority-fee').text()).toContain('$ 100.00')
    expect(wrapper.find('#certify-fee').exists()).toBe(true)
    expect(wrapper.find('#certify-fee').text()).toContain('Certified search')
    expect(wrapper.find('#certify-fee').text()).toContain('$ 25.00')
  })

  it('renders fee for Staff Sale or Gift Transfer', async () => {
    const state = store.getStateModel as StateModelIF
    await store.setAuthRoles(['staff'])
    state.search.searchCertified = false

    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHR_TRANSFER,
      setRegistrationLength: null,
      setRegistrationType: null,
      setStaffClientPayment: true
    })

    // Fee summary not updated until Transfer Type is selected
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    expect(wrapper.vm.feeLabel).toBe('Ownership Transfer or Change')
    expect(wrapper.find('#transfer-type-text').text()).toContain('Select Transfer Type')

    await wrapper.setProps({
      transferType: UITransferTypes.SALE_OR_GIFT
    })

    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHR_TRANSFER)
    expect(wrapper.vm.registrationType).toBe(null)
    expect(wrapper.vm.feeLabel).toBe('Ownership Transfer or Change')
    expect(wrapper.find('#transfer-type-text').text()).toContain('Transfer Due to Sale or Gift')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(50)
    expect(wrapper.vm.feeSummary.quantity).toBe(1)
    expect(wrapper.find('#processing-fee-summary').exists()).toBe(false)
    expect(wrapper.vm.totalFees).toBe(50)
    expect(wrapper.vm.totalAmount).toBe(50)
    expect(wrapper.vm.isComplete).toBe(true)
  })

  it('renders fee for SJT Transfer', async () => {
    const state = store.getStateModel as StateModelIF
    await store.setAuthRoles(['staff'])
    state.search.searchCertified = false

    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHR_TRANSFER,
      setRegistrationLength: null,
      setRegistrationType: null,
      setStaffClientPayment: true
    })

    // Fee summary not updated until Transfer Type is selected
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    expect(wrapper.vm.feeLabel).toBe('Ownership Transfer or Change')
    expect(wrapper.find('#transfer-type-text').text()).toContain('Select Transfer Type')

    await wrapper.setProps({
      transferType: UITransferTypes.SURVIVING_JOINT_TENANT
    })

    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHR_TRANSFER)
    expect(wrapper.vm.registrationType).toBe(null)
    expect(wrapper.vm.feeLabel).toBe('Ownership Transfer or Change')
    expect(wrapper.find('#transfer-type-text').text()).toContain('Transfer to Surviving Joint Tenant(s)')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(50)
    expect(wrapper.vm.feeSummary.quantity).toBe(1)
    expect(wrapper.find('#processing-fee-summary').exists()).toBe(false)
    expect(wrapper.vm.totalFees).toBe(50)
    expect(wrapper.vm.totalAmount).toBe(50)
    expect(wrapper.vm.isComplete).toBe(true)
  })

  it('renders fee for TRANS WILL Transfer', async () => {
    const state = store.getStateModel as StateModelIF
    await store.setAuthRoles(['staff'])
    state.search.searchCertified = false

    await wrapper.setProps({
      setFeeType: FeeSummaryTypes.MHR_TRANSFER,
      setRegistrationLength: null,
      setRegistrationType: null,
      setStaffClientPayment: true
    })

    // Fee summary not updated until Transfer Type is selected
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    expect(wrapper.vm.feeLabel).toBe('Ownership Transfer or Change')
    expect(wrapper.find('#transfer-type-text').text()).toContain('Select Transfer Type')

    await wrapper.setProps({
      transferType: UITransferTypes.TO_EXECUTOR_PROBATE_WILL
    })

    expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.MHR_TRANSFER)
    expect(wrapper.vm.registrationType).toBe(null)
    expect(wrapper.vm.feeLabel).toBe('Ownership Transfer or Change')
    expect(wrapper.find('#transfer-type-text').text()).toContain('Transfer to Executor - Grant of Probate with Will')
    expect(wrapper.vm.feeSummary.feeAmount).toBe(50)
    expect(wrapper.vm.feeSummary.quantity).toBe(1)
    expect(wrapper.find('#processing-fee-summary').exists()).toBe(false)
    expect(wrapper.vm.totalFees).toBe(50)
    expect(wrapper.vm.totalAmount).toBe(50)
    expect(wrapper.vm.isComplete).toBe(true)
  })
})
