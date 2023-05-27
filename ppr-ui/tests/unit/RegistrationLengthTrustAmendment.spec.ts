// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  LengthTrustIF
} from '@/interfaces'
import {
  mockedRepairersLien,
  mockedSelectSecurityAgreement,
  mockedVehicleCollateralExisting,
  mockedGeneralCollateralExisting,
  mockedDebtorsExisting,
  mockedSecuredPartiesExisting
} from './test-data'

// Components
import { RegistrationLengthTrustAmendment, EditTrustIndenture } from '@/components/registration'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Input field selectors / buttons
const undoButton: string = '#trust-indenture-undo-btn'
const amendButton: string = '#trust-indenture-amend-btn'
const doneButton: string = '#done-btn-trust-indenture'
const cancelButton: string = '#cancel-btn-trust-indenture'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  isSummary: boolean
): Wrapper<any> {
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((RegistrationLengthTrustAmendment as any), {
    localVue,
    propsData: { isSummary },
    store,
    vuetify
  })
}

describe('RegistrationLengthTrustAmendment non-Security Agreement tests', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.setRegistrationType(mockedRepairersLien())
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationNumber('0023001B')
    await store.setVehicleCollateral(mockedVehicleCollateralExisting)
    await store.setGeneralCollateral(mockedGeneralCollateralExisting)
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: null,
      securedParties: mockedSecuredPartiesExisting,
      debtors: mockedDebtorsExisting
    })
    await store.setRegistrationExpiryDate('2021-07-28T07:00:00+00:00')
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with no trust indenture', async () => {
    await store.setOriginalLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '2022-10-02T06:59:59+00:00',
      lienAmount: '10000.00'
    })
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '2022-10-02T06:59:59+00:00',
      lienAmount: '10000.00'
    })
    expect(wrapper.findComponent(RegistrationLengthTrustAmendment).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.vm.summaryView).toBe(false)
    expect(wrapper.vm.showEditTrustIndenture).toBe(false)
    expect(wrapper.vm.editInProgress).toBe(false)
    expect(wrapper.vm.computedExpiryDateFormatted).toBeDefined()
  })
})

describe('RegistrationLengthTrustAmendment Security Agreement tests', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationNumber('0023001B')
    await store.setVehicleCollateral(mockedVehicleCollateralExisting)
    await store.setGeneralCollateral(mockedGeneralCollateralExisting)
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: null,
      securedParties: mockedSecuredPartiesExisting,
      debtors: mockedDebtorsExisting
    })
    await store.setRegistrationExpiryDate('2021-07-28T07:00:00+00:00')

    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with trust indenture true', async () => {
    await store.setOriginalLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.setLengthTrust({
      valid: true,
      trustIndenture: true,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    expect(wrapper.findComponent(RegistrationLengthTrustAmendment).exists()).toBe(true)
    expect(wrapper.vm.summaryView).toBe(false)
    expect(wrapper.vm.showTrustIndenture).toBe(true)
    expect(wrapper.vm.trustIndenture).toBe(true)
    expect(wrapper.vm.showEditTrustIndenture).toBe(false)
    expect(wrapper.vm.editInProgress).toBe(false)
    expect(wrapper.vm.computedExpiryDateFormatted).toBeDefined()
    expect(wrapper.find(undoButton).exists()).toBe(true)
    wrapper.find(undoButton).trigger('click')
    await nextTick()
    expect(wrapper.find(amendButton).exists()).toBe(true)
  })

  it('renders with trust indenture false', async () => {
    await store.setOriginalLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    expect(wrapper.findComponent(RegistrationLengthTrustAmendment).exists()).toBe(true)
    expect(wrapper.vm.summaryView).toBe(false)
    expect(wrapper.vm.showTrustIndenture).toBe(true)
    expect(wrapper.vm.trustIndenture).toBe(false)
    expect(wrapper.vm.showEditTrustIndenture).toBe(false)
    expect(wrapper.vm.editInProgress).toBe(false)
    expect(wrapper.vm.computedExpiryDateFormatted).toBeDefined()
    expect(wrapper.find(amendButton).exists()).toBe(true)
    wrapper.find(amendButton).trigger('click')
    await nextTick()
    expect(wrapper.findComponent(EditTrustIndenture).exists()).toBeTruthy()
    expect(wrapper.findComponent(EditTrustIndenture).isVisible()).toBe(true)
    expect(wrapper.vm.showEditTrustIndenture).toBe(true)
    expect(wrapper.vm.editInProgress).toBe(true)
    expect(wrapper.find(cancelButton).exists()).toBe(true)
    wrapper.find(cancelButton).trigger('click')
    await Vue.nextTick()
    expect(wrapper.findComponent(EditTrustIndenture).exists()).toBeFalsy()
    expect(wrapper.vm.showEditTrustIndenture).toBe(false)
    expect(wrapper.vm.editInProgress).toBe(false)
    wrapper.find(amendButton).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.showEditTrustIndenture).toBe(true)
    expect(wrapper.vm.editInProgress).toBe(true)
    expect(wrapper.find(doneButton).exists()).toBe(true)
    wrapper.find(doneButton).trigger('click')
    await Vue.nextTick()
    expect(wrapper.findComponent(EditTrustIndenture).exists()).toBeFalsy()
    expect(wrapper.vm.showEditTrustIndenture).toBe(false)
    expect(wrapper.vm.editInProgress).toBe(false)
    expect(wrapper.find('.border-error-left').exists()).toBe(false)
  })
  it('shows error bar', async () => {
    await wrapper.setProps({ setShowErrorBar: true })
    wrapper.vm.editInProgress = true
    await Vue.nextTick()
    expect(wrapper.find('.border-error-left').exists()).toBe(true)
  })
})

describe('RegistrationLengthTrustAmendment summary view tests', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationNumber('0023001B')
    await store.setVehicleCollateral(mockedVehicleCollateralExisting)
    await store.setGeneralCollateral(mockedGeneralCollateralExisting)
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: null,
      securedParties: mockedSecuredPartiesExisting,
      debtors: mockedDebtorsExisting
    })
    await store.setRegistrationExpiryDate('2021-07-28T07:00:00+00:00')
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
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
    wrapper = createComponent(true)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with trust indenture changed to false', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrustAmendment).exists()).toBe(true)
    expect(wrapper.vm.summaryView).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(true)
    expect(wrapper.vm.showEditTrustIndenture).toBe(false)
    expect(wrapper.vm.editInProgress).toBe(false)
    expect(wrapper.vm.trustIndentureModified).toBe(true)
    expect(wrapper.vm.trustIndentureSummary).toBe('No')
  })
})
