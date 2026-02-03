import { nextTick } from 'vue'
import flushPromises from 'flush-promises'
import { DischargeRegistration } from '@/pages'
import Collateral from '@/components/collateral/Collateral.vue'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { CautionBox, StickyContainer } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import {
  DebtorSummary,
  RegisteringPartySummary,
  SecuredPartySummary
} from '@/components/parties/summaries'
import { RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { mockedDebtorNames, mockedFinancingStatementAll } from './test-data'
import { useStore } from '@/store/store'
import { createComponent } from './utils'
import { vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'


vi.mock('@/utils/ppr-api-helper', () => ({
  getFinancingStatement: vi.fn(() =>
    Promise.resolve({ ...mockedFinancingStatementAll }))
}))

describe('ReviewConfirm new registration component', () => {
  let wrapper, pinia, store

  beforeEach(async () => {
    // 1) Fresh pinia for each test
    pinia = createPinia()
    setActivePinia(pinia)

    // 2) Now get the store from this active pinia
    store = useStore()

    // 3) Mutate the SAME store that the component will see
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])

    wrapper = await createComponent(
      DischargeRegistration,
      { appReady: true },
      RouteNames.REVIEW_DISCHARGE, {
        'reg-num': '123456B'
      },
      [pinia]
    )
    await flushPromises()
  })

  it('renders Review Registration View with child components', async () => {
    expect(wrapper.findComponent(DischargeRegistration).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).vm.setMsg).toContain(
      'provide the verification statement to all Secured Parties')
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    // wait because store getting set still
    await nextTick()
    const state = store.getStateModel
    // check length trust summary
    expect(state.registration.lengthTrust.lifeInfinite).toBe(mockedFinancingStatementAll.lifeInfinite)
    expect(state.registration.lengthTrust.lifeYears).toBe(mockedFinancingStatementAll.lifeYears)
    expect(state.registration.lengthTrust.trustIndenture).toBe(mockedFinancingStatementAll.trustIndenture)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toStrictEqual({})
    expect(state.originalRegistration.parties.registeringParty)
      .toStrictEqual(mockedFinancingStatementAll.registeringParty)
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
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Confirm and Complete')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.DISCHARGE)
  })

  it('processes cancel button action', async () => {
    wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    wrapper.findComponent(BaseDialog).vm.$emit('proceed', false)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('processes submit button action', async () => {
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_DISCHARGE)
  })
})
