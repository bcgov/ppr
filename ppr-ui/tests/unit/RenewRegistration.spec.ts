import { nextTick } from 'vue'
import { RenewRegistration } from '@/pages'
import { Collateral } from '@/components/collateral'
import { RegistrationLengthTrust } from '@/components/registration'
import { StickyContainer } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import {
  DebtorSummary,
  RegisteringPartySummary,
  SecuredPartySummary
} from '@/components/parties/summaries'
import { RouteNames } from '@/enums'
import { mockedDebtorNames, mockedFinancingStatementAll } from './test-data'
import flushPromises from 'flush-promises'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { createComponent } from './utils'
import { useStore } from '@/store/store'
import { vi } from 'vitest'

const store = useStore()

describe('Renew registration component', () => {
  let wrapper: any

  beforeEach(async () => {
    vi.mock('@/utils/ppr-api-helper', () => ({
      getFinancingStatement: vi.fn(() =>
        Promise.resolve({ ...mockedFinancingStatementAll })),
    }))
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    wrapper = await createComponent(
      RenewRegistration,
      { appReady: true },
      RouteNames.RENEW_REGISTRATION,
      { 'reg-num': '123456B' }
    )
    await flushPromises()
  })

  it('renders Renew Registration View with child components', async () => {
    expect(wrapper.findComponent(RenewRegistration).exists()).toBe(true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.RENEW_REGISTRATION)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    // wait because store getting set still
    await nextTick()
    const state = store.getStateModel
    // check length trust summary
    expect(state.registration.lengthTrust.lifeInfinite).toBe(mockedFinancingStatementAll.lifeInfinite)
    // should start off null
    expect(state.registration.lengthTrust.lifeYears).toBe(null)
    expect(state.registration.lengthTrust.trustIndenture).toBe(mockedFinancingStatementAll.trustIndenture)
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(null)
    expect(state.originalRegistration.parties.registeringParty).toStrictEqual(mockedFinancingStatementAll.registeringParty)
    expect(wrapper.findComponent(RegisteringPartySummary).exists()).toBe(true)
    // check secured parties
    expect(state.registration.parties.securedParties).toStrictEqual(mockedFinancingStatementAll.securedParties)
    expect(wrapper.findComponent(SecuredPartySummary).exists()).toBe(true)
    // check debtors
    expect(state.registration.parties.debtors).toStrictEqual(mockedFinancingStatementAll.debtors)
    expect(wrapper.findComponent(DebtorSummary).exists()).toBe(true)
    // check vehicle collateral
    expect(state.registration.collateral.vehicleCollateral).toStrictEqual(mockedFinancingStatementAll.vehicleCollateral)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.RENEW)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: mockedFinancingStatementAll.lifeInfinite,
      // set life years to 0 so user has to choose
      lifeYears: 0
    })
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Review and Complete')
  })

  it('processes cancel button action', async () => {
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.RENEW_REGISTRATION)
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    wrapper.findComponent(BaseDialog).vm.$emit('proceed', false)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('processes submit button action', async () => {
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 1,
      showInvalid: false
    })
    wrapper.vm.registrationValid = true
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await wrapper.vm.$router.push({ name: RouteNames.CONFIRM_RENEWAL })
    await flushPromises()
    await nextTick()

    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_RENEWAL)
  })

  it('doesnt proceed if validation errors', async () => {
    wrapper.vm.registrationValid = false
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.showInvalid).toBe(true)
  })
})
