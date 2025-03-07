import { nextTick } from 'vue'
import {
  mockedFinancingStatementAll,
  mockedDebtorNames,
  mockedAmendmentResponse,
  mockedAmendmentCertified,
  mockedDraftAmendmentStatement,
  mockedVehicleCollateral1,
  mockedGeneralCollateral1,
  mockedPartyCodeSearchResults
} from './test-data'

import { ConfirmAmendment } from '@/pages'
import { CertifyInformation, FolioNumberSummary, StickyContainer } from '@/components/common'
import { BaseDialog, StaffPaymentDialog } from '@/components/dialogs'
import { AmendmentDescription, RegistrationLengthTrustAmendment } from '@/components/registration'
import { GenColSummary } from '@/components/collateral/general'

import { ActionTypes, RegistrationFlowType, RouteNames } from '@/enums'
import type { StateModelIF } from '@/interfaces'
import flushPromises from 'flush-promises'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { RegisteringPartyChange } from '@/components/parties/party'
import { usePprRegistration } from '@/composables'
import { useStore } from '@/store/store'
import { createComponent } from './utils'
import { vi } from 'vitest'

const store = useStore()
const { initPprUpdateFilling } = usePprRegistration()

vi.mock('@/utils/ppr-api-helper', () => ({
  getFinancingStatement: vi.fn(() =>
    Promise.resolve({ ...mockedFinancingStatementAll }))
}))
vi.mock('@/utils/registration-helper', () => ({
  saveAmendmentStatementDraft: vi.fn(() =>
    Promise.resolve({ ...mockedDraftAmendmentStatement }))
}))
vi.mock('@/utils/registration-helper', () => ({
  saveAmendmentStatement: vi.fn(() =>
    Promise.resolve({ ...mockedAmendmentResponse }))
}))

describe('Confirm Amendment registration component', () => {
  let wrapper

  beforeAll(async () => {
    // Mimics loading the data in the store in the previous step.
    const financingStatement = mockedFinancingStatementAll
    financingStatement.baseRegistrationNumber = '123456B'
    initPprUpdateFilling(financingStatement, RegistrationFlowType.AMENDMENT)
  })

  beforeEach(async () => {
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])

    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: '',
      action: ActionTypes.EDITED
    })
    await store.setOriginalLengthTrust({
      valid: true,
      trustIndenture: true,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.setAmendmentDescription('test')
    await store.setGeneralCollateral([{ descriptionAdd: 'test', descriptionDelete: 'othertest' }])

    wrapper = await createComponent(
      ConfirmAmendment,
      { appReady: true },
      RouteNames.CONFIRM_AMENDMENT,
      { 'reg-num': '123456B' }
    )
    await flushPromises()
  })

  it('renders Review Confirm View with child components', () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_AMENDMENT)
    expect(wrapper.vm.appReady).toBe(true)
    const state = store.getStateModel as StateModelIF

    expect(wrapper.findComponent(ConfirmAmendment).exists()).toBe(true)
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(true)

    // check registering party
    expect(state.registration.parties.registeringParty).toBe(null)
    expect(wrapper.findComponent(RegisteringPartyChange).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationLengthTrustAmendment).exists()).toBe(true)
    expect(wrapper.findComponent(AmendmentDescription).exists()).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Back')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Register Amendment and Pay')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.AMEND)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe('')
    // // dialog
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.findComponent(StaffPaymentDialog).exists()).toBe(true)
  })

  it('allows back to amend page', async () => {
    expect(wrapper.findComponent(ConfirmAmendment).exists()).toBe(true)
    await wrapper.findComponent(StickyContainer).vm.$emit('back', true)
    await nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
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
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_AMENDMENT)
    // if dialog emits proceed true it goes to dashboard
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', false)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
})

describe('Confirm Amendment registration save registration', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])

    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: '',
      action: ActionTypes.EDITED
    })
    await store.setOriginalLengthTrust({
      valid: true,
      trustIndenture: true,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.setAddCollateral({
      vehicleCollateral: mockedVehicleCollateral1,
      generalCollateral: mockedGeneralCollateral1,
      valid: true
    })
    await store.setAmendmentDescription('test')
    await store.setCertifyInformation(mockedAmendmentCertified)

    wrapper = await createComponent(
      ConfirmAmendment,
      { appReady: true },
      RouteNames.CONFIRM_AMENDMENT,
      { 'reg-num': '123456B' }
    )
    await flushPromises()
  })

  it('allows submit of amendment', async () => {
    // Set up for valid amendment request
    await store.setRegistrationNumber('023001B')
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    await nextTick()

    const state = store.getStateModel as StateModelIF
    const parties = state.registration.parties
    parties.registeringParty = mockedPartyCodeSearchResults[0]
    await store.setAddSecuredPartiesAndDebtors(parties)

    expect(wrapper.vm.collateralValid).toBe(true)
    expect(wrapper.vm.partiesValid).toBe(true)
    expect(wrapper.vm.courtOrderValid).toBe(true)

    await wrapper.vm.submitAmendment()
    await nextTick()

    // new amend registration is in store regTableData
    expect(store.getRegTableNewItem.addedReg)
      .toBe(mockedAmendmentResponse.amendmentRegistrationNumber)
    expect(store.getRegTableNewItem.addedRegParent)
      .toBe(mockedAmendmentResponse.baseRegistrationNumber)
  })
})

describe('Confirm Amendment for staff', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    await store.setAuthRoles(['staff', 'ppr_staff'])

    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: '',
      action: ActionTypes.EDITED
    })
    await store.setOriginalLengthTrust({
      valid: true,
      trustIndenture: true,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.setAddCollateral({
      vehicleCollateral: mockedVehicleCollateral1,
      generalCollateral: mockedGeneralCollateral1,
      valid: true
    })
    await store.setAmendmentDescription('test')
    await store.setCertifyInformation(mockedAmendmentCertified)

    wrapper = await createComponent(
      ConfirmAmendment,
      { appReady: true },
      RouteNames.CONFIRM_AMENDMENT,
      { 'reg-num': '123456B' }
    )
    await flushPromises()
  })

  it('shows staff payment', async () => {
    // Set up for valid amendment request
    await store.setRegistrationNumber('023001B')
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    expect(wrapper.vm.collateralValid).toBe(true)
    expect(wrapper.vm.partiesValid).toBe(true)
    expect(wrapper.vm.courtOrderValid).toBe(true)
    // need to wait 2 secs so throttle is done
    setTimeout(async () => {
      await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
      await flushPromises()
      expect(wrapper.findComponent(StaffPaymentDialog).vm.$props.setDisplay).toBe(true)
    }, 2000)
  })
})
