import { nextTick } from 'vue'
import { createComponent } from './utils'
import { AmendRegistration } from '@/views'
import { ActionTypes, RouteNames } from '@/enums'
import { useStore } from '@/store/store'
import {
  mockedDebtorNames,
  mockedDraftAmendmentStatement,
  mockedFinancingStatementAll,
  mockedFinancingStatementRepairers
} from './test-data'
import { vi } from 'vitest'
import {
  AmendmentDescription,
  RegistrationLengthTrustAmendment,
  RegistrationLengthTrustSummary
} from '@/components/registration'
import { DebtorSummary, RegisteringPartySummary, SecuredPartySummary } from '@/components/parties/summaries'
import { SecuredParties } from '@/components/parties/party'
import { Debtors } from '@/components/parties/debtor'
import { Collateral } from '@/components/collateral'
import { StickyContainer } from '@/components/common'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import flushPromises from 'flush-promises'

const store = useStore()

vi.mock('@/utils/ppr-api-helper', () => ({
  getFinancingStatement: vi.fn(() =>
    Promise.resolve({ ...mockedFinancingStatementAll }))
}))
vi.mock('@/utils/registration-helper', () => ({
  saveAmendmentStatementDraft: vi.fn(() =>
    Promise.resolve({ ...mockedDraftAmendmentStatement }))
}))

describe('Amendment registration component', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    wrapper = await createComponent(
      AmendRegistration,
      { appReady: true },
      RouteNames.AMEND_REGISTRATION,
      { 'reg-num': '123456B' }
    )
    await flushPromises()
  })

  it('renders Amend Registration View with child components', async () => {
    expect(wrapper.findComponent(AmendRegistration).exists()).toBe(true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)

    const state = store.getStateModel
    // check length trust summary
    expect(state.registration.lengthTrust.lifeInfinite).toBe(mockedFinancingStatementAll.lifeInfinite)
    expect(state.registration.lengthTrust.lifeYears).toBe(5)
    expect(state.registration.lengthTrust.trustIndenture).toBe(mockedFinancingStatementAll.trustIndenture)
    expect(wrapper.findComponent(RegistrationLengthTrustAmendment).exists()).toBe(true)
    // check amendment description
    expect(state.registration.amendmentDescription).toBe('')
    expect(wrapper.findComponent(AmendmentDescription).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(null)
    expect(state.originalRegistration.parties.registeringParty).toEqual(mockedFinancingStatementAll.registeringParty)
    expect(wrapper.findComponent(RegisteringPartySummary).exists()).toBe(true)
    // check secured parties
    expect(state.registration.parties.securedParties).toEqual(mockedFinancingStatementAll.securedParties)
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    // check debtors
    expect(state.registration.parties.debtors).toEqual(mockedFinancingStatementAll.debtors)
    expect(wrapper.findComponent(Debtors).exists()).toBe(true)
    // check vehicle collateral
    expect(state.registration.collateral.vehicleCollateral).toEqual(mockedFinancingStatementAll.vehicleCollateral)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.AMEND)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Save and Resume Later')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Review and Complete')
  })

  it('processes cancel button action', async () => {
    await store.setUnsavedChanges(false)
    await nextTick()
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('doesnt proceed if validation errors', async () => {
    wrapper.vm.setValidDebtor(false)
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.showInvalid).toBe(true)
  })

  it('goes to the confirmation page', async () => {
    wrapper.vm.courtOrderValid = true
    await store.setAmendmentDescription('test12')
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_AMENDMENT)
  })

  it('does not go to the confirmation page if component open', async () => {
    wrapper.vm.debtorOpen = true
    await nextTick()
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
  })

  it('saves the draft and redirects to dashboard', async () => {
    wrapper.findComponent(StickyContainer).vm.$emit('back', true)
    await nextTick()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('checks for length trust indenture & court order validity -if valid', async () => {
    await store.setLengthTrust({
      valid: true,
      trustIndenture: true,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: '',
      action: ActionTypes.EDITED
    })
    wrapper.vm.courtOrderValid = true
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_AMENDMENT)
  })
})

describe('Amendment for repairers lien component', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(
      AmendRegistration,
      { appReady: true },
      RouteNames.AMEND_REGISTRATION,
      { 'reg-num': '123456B' }
    )
    await flushPromises()
  })

  it('renders Amend Registration View with child components', async () => {
    wrapper.vm.setStore({ ...mockedFinancingStatementRepairers })
    await nextTick()

    expect(wrapper.findComponent(AmendRegistration).exists()).toBe(true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    const state = store.getStateModel
    // check length trust summary
    expect(state.registration.lengthTrust.lifeInfinite).toBe(mockedFinancingStatementAll.lifeInfinite)
    expect(state.registration.lengthTrust.lifeYears).toBe(1)
    expect(state.registration.lengthTrust.trustIndenture).toBe(mockedFinancingStatementAll.trustIndenture)
    expect(wrapper.findComponent(RegistrationLengthTrustAmendment).exists()).toBe(false)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    // check amendment description
    expect(state.registration.amendmentDescription).toBe('')
    expect(wrapper.findComponent(AmendmentDescription).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(null)
    expect(state.originalRegistration.parties.registeringParty).toEqual(mockedFinancingStatementAll.registeringParty)
    expect(wrapper.findComponent(RegisteringPartySummary).exists()).toBe(true)
    // check secured parties
    expect(state.registration.parties.securedParties).toEqual(mockedFinancingStatementAll.securedParties)
    expect(wrapper.findComponent(SecuredPartySummary).exists()).toBe(true)
    // check debtors
    expect(state.registration.parties.debtors).toEqual(mockedFinancingStatementAll.debtors)
    expect(wrapper.findComponent(DebtorSummary).exists()).toBe(true)
    // check vehicle collateral
    expect(state.registration.collateral.vehicleCollateral).toEqual(mockedFinancingStatementAll.vehicleCollateral)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.AMEND)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Save and Resume Later')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Review and Complete')
  })
})
