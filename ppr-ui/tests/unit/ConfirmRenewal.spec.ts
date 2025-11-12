import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import {
  mockedFinancingStatementAll,
  mockedDebtorNames,
  mockedRenewalResponse,
  mockedFinancingStatementRepairers,
  mockedPartyCodeSearchResults
} from './test-data'
import { ConfirmRenewal } from '@/pages'
import { FolioNumberSummary, StickyContainer, CertifyInformation, CourtOrder } from '@/components/common'
import { BaseDialog, StaffPaymentDialog } from '@/components/dialogs'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { RegistrationFlowType, RouteNames } from '@/enums'
import type { StateModelIF } from '@/interfaces'
import flushPromises from 'flush-promises'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { RegisteringPartyChange } from '@/components/parties/party'
import { usePprRegistration } from '@/composables'
import { createComponent } from './utils'
import { vi } from 'vitest'
import { createPinia } from 'pinia'

const store = useStore()
const { initPprUpdateFilling } = usePprRegistration()

vi.mock('@/utils/ppr-api-helper', () => ({
  getFinancingStatement: vi.fn(() =>
    Promise.resolve({ ...mockedFinancingStatementAll }))
}))
vi.mock('@/utils/registration-helper', () => ({
  saveRenewal: vi.fn(() =>
    Promise.resolve({ ...mockedRenewalResponse }))
}))
vi.mock('@/utils/auth-helper', () => ({
  getRegisteringPartyFromAuth: vi.fn(() =>
    Promise.resolve({})),
  getStaffRegisteringParty: vi.fn(() =>
    Promise.resolve({}))
}))

describe('Confirm Renewal new registration component', () => {
  let wrapper
  beforeAll(async () => {
    // Mimics loading the data in the store in the previous step.
    const financingStatement = mockedFinancingStatementAll
    financingStatement.baseRegistrationNumber = '123456B'
    initPprUpdateFilling(financingStatement, RegistrationFlowType.RENEWAL)
  })

  beforeEach(async () => {
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    wrapper = await createComponent(
      ConfirmRenewal,
      { appReady: true },
      RouteNames.CONFIRM_RENEWAL,
      { 'reg-num': '123456B' },
      [createPinia()]
    )
    await flushPromises()
  })

  it('renders Review Confirm View with child components', () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_RENEWAL)
    expect(wrapper.vm.appReady).toBe(true)
    const state = store.getStateModel as StateModelIF

    expect(wrapper.findComponent(ConfirmRenewal).exists()).toBe(true)
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toStrictEqual({})
    expect(wrapper.findComponent(RegisteringPartyChange).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Back')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Register Renewal and Pay')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.RENEW)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe('')
    // dialog
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.findComponent(StaffPaymentDialog).exists()).toBe(true)
    // certify
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
    expect(wrapper.findComponent(CourtOrder).exists()).toBe(false)
  })

  it('allows back to previous page', async () => {
    expect(wrapper.findComponent(ConfirmRenewal).exists()).toBe(true)
    await wrapper.findComponent(StickyContainer).vm.$emit('back', true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.RENEW_REGISTRATION)
  })

  it('processes cancel button action', async () => {
    // setup
    await store.setUnsavedChanges(true)
    // dialog doesn't start visible
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    // pressing cancel triggers dialog
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(true)
    // if dialog emits proceed false it closes + stays on page
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_RENEWAL)
    // if dialog emits proceed true it goes to dashboard
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', false)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('allows submit of renewal', async () => {
    // Set up for valid discharge request
    await store.setRegistrationNumber('023001B')
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    const state = store.getStateModel as StateModelIF
    const parties = state.registration.parties
    parties.registeringParty = mockedPartyCodeSearchResults[0]
    await store.setAddSecuredPartiesAndDebtors(parties)

    await wrapper.findComponent(CertifyInformation).vm.$emit('certifyValid', true)
    await nextTick()
    await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await nextTick()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
    // new renew registration is in store regTableData
    expect(store.getStateModel.registrationTable.newItem.addedReg).toBe(
      mockedRenewalResponse.renewalRegistrationNumber
    )
    expect(store.getStateModel.registrationTable.newItem.addedRegParent).toBe(
      mockedRenewalResponse.baseRegistrationNumber
    )
  })
})
