import {
  mockedDebtorNames,
  mockedDischargeResponse,
  mockedFinancingStatementAll,
  mockedPartyCodeSearchResults
} from './test-data'
import { useStore } from '@/store/store'
import { usePprRegistration } from '@/composables'
import { RegistrationFlowType, RouteNames } from '@/enums'
import { createComponent } from './utils'
import flushPromises from 'flush-promises'
import { ConfirmDischarge } from '@/views'
import {
  CautionBox,
  CertifyInformation,
  DischargeConfirmSummary,
  FolioNumberSummary,
  StickyContainer
} from '@/components/common'
import { RegisteringPartyChange } from '@/components/parties/party'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { BaseDialog } from '@/components/dialogs'
import { vi } from 'vitest'

const store = useStore()
const { initPprUpdateFilling } = usePprRegistration()

vi.mock('@/utils/ppr-api-helper', () => ({
  getFinancingStatement: vi.fn(() =>
    Promise.resolve({ ...mockedFinancingStatementAll }))
}))
vi.mock('@/utils/registration-helper', () => ({
  saveDischarge: vi.fn(() =>
    Promise.resolve({ ...mockedDischargeResponse }))
}))

describe('ConfirmDischarge registration view', () => {
  let wrapper
  const regNum = '123456B'

  beforeAll(async () => {
    // Mimicks loading the data in the store in the previous step.
    const financingStatement = mockedFinancingStatementAll
    financingStatement.baseRegistrationNumber = regNum
    initPprUpdateFilling(financingStatement, RegistrationFlowType.DISCHARGE)
  })

  beforeEach(async () => {
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])

    wrapper = await createComponent(
      ConfirmDischarge,
      { appReady: true },
      RouteNames.CONFIRM_DISCHARGE,
      { 'reg-num': regNum }
    )
    await flushPromises()
  })

  it('renders Confirm Registration View with child components', () => {
    expect(wrapper.findComponent(ConfirmDischarge).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).vm.setMsg).toContain(
      'provide the verification statement to all Secured Parties')
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_DISCHARGE)
    expect(wrapper.vm.appReady).toBe(true)
    const state = store.getStateModel
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(null)
    expect(wrapper.findComponent(RegisteringPartyChange).exists()).toBe(true)
    // check confirm discharge section
    expect(wrapper.findComponent(DischargeConfirmSummary).exists()).toBe(true)
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setRegNum).toContain(regNum)
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setRegType).toContain(
      state.registration.registrationType.registrationTypeUI
    )
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setCollateralSummary).toBe(
      'General Collateral and 2 Vehicles'
    )
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setShowErrors).toBe(false)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Back')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Register Total Discharge')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.DISCHARGE)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe('')
    // folio
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    // dialog
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    // certify
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
  })

  it('processes back button action', async () => {
    await wrapper.findComponent(StickyContainer).vm.$emit('back', true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
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
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_DISCHARGE)
    // if dialog emits proceed true it goes to dashboard
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', false)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('updates validity from checkboxes', async () => {
    expect(wrapper.vm.validConfirm).toBe(false)
    await wrapper.findComponent(DischargeConfirmSummary).vm.$emit('valid', true)
    expect(wrapper.vm.validConfirm).toBe(true)
  })

  it('updates validity from certify', async () => {
    expect(wrapper.vm.validCertify).toBe(false)
    await wrapper.findComponent(CertifyInformation).vm.$emit('certifyValid', true)
    expect(wrapper.vm.validCertify).toBe(true)
  })

  it('shows validation errors when needed when submitting', async () => {
    await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setShowErrors).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe(
      '< Please complete required information'
    )
    // msgs go away when validation changes
    await wrapper.findComponent(DischargeConfirmSummary).vm.$emit('valid', true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe('')
  })

  it('shows errors when folio is invalid', async () => {
    await wrapper.findComponent(FolioNumberSummary).vm.$emit('folioValid', false)
    // need to wait 2 secs so throttle is done
    setTimeout(async () => {
      await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
      // turn show errors on when invalid
      expect(wrapper.vm.showErrors).toBe(true)
    }, 2000)
  })

  it('processes submit button action', async () => {
    // Set up for valid discharge request
    await store.setRegistrationNumber('023001B')
    await store.setFolioOrReferenceNumber('A-00000402')
    const state = store.getStateModel
    const parties = state.registration.parties
    parties.registeringParty = mockedPartyCodeSearchResults[0]
    await store.setAddSecuredPartiesAndDebtors(parties)

    await wrapper.findComponent(DischargeConfirmSummary).vm.$emit('valid', true)
    await wrapper.findComponent(CertifyInformation).vm.$emit('certifyValid', true)
    // need to wait 2 secs so throttle is done
    setTimeout(async () => {
      await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
      await flushPromises()
      expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
      // new dishcarge registration is in store regTableData
      expect(wrapper.vm.$store.state.stateModel.regTableData.addedReg).toBe(
        mockedDischargeResponse.dischargeRegistrationNumber
      )
      expect(wrapper.vm.$store.state.stateModel.regTableData.addedRegParent).toBe(
        mockedDischargeResponse.baseRegistrationNumber
      )
    }, 2000)
  })
})
