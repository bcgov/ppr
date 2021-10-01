// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
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
const store = getVuexStore()

/**
 * Returns the last event for a given name, to be used for testing event propagation in response to component changes.
 *
 * @param wrapper the wrapper for the component that is being tested.
 * @param name the name of the event that is to be returned.
 *
 * @returns the value of the last named event for the wrapper.
 */
function getLastEvent (wrapper: Wrapper<any>, name: string): any {
  const eventsList: Array<any> = wrapper.emitted(name)
  if (!eventsList) {
    return null
  }
  const events: Array<any> = eventsList[eventsList.length - 1]
  return events[0]
}

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationLengthTrustAmendment, {
    localVue,
    store,
    vuetify
  })
}

describe('RegistrationLengthTrustAmendment non-Security Agreement tests', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedRepairersLien())
    await store.dispatch('setFolioOrReferenceNumber', 'A-00000402')
    await store.dispatch('setRegistrationNumber', '0023001B')
    await store.dispatch('setVehicleCollateral', mockedVehicleCollateralExisting)
    await store.dispatch('setGeneralCollateral', mockedGeneralCollateralExisting)
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      registeringParty: null,
      securedParties: mockedSecuredPartiesExisting,
      debtors: mockedDebtorsExisting
    })
    await store.dispatch('setRegistrationExpiryDate', '2021-07-28T07:00:00+00:00')
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with no trust indenture', async () => {
    await store.dispatch('setOriginalLengthTrust', {
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '2022-10-02T06:59:59+00:00',
      lienAmount: '10000.00'
    })
    await store.dispatch('setLengthTrust', {
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
    expect(wrapper.vm.showEditTrustIndenture).toBe(false)
    expect(wrapper.vm.editInProgress).toBe(false)
    expect(wrapper.vm.computedExpiryDateFormatted).toBeDefined()
  })
})

describe('RegistrationLengthTrustAmendment Security Agreement tests', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setFolioOrReferenceNumber', 'A-00000402')
    await store.dispatch('setRegistrationNumber', '0023001B')
    await store.dispatch('setVehicleCollateral', mockedVehicleCollateralExisting)
    await store.dispatch('setGeneralCollateral', mockedGeneralCollateralExisting)
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      registeringParty: null,
      securedParties: mockedSecuredPartiesExisting,
      debtors: mockedDebtorsExisting
    })
    await store.dispatch('setRegistrationExpiryDate', '2021-07-28T07:00:00+00:00')

    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with trust indenture true', async () => {
    await store.dispatch('setOriginalLengthTrust', {
      valid: true,
      trustIndenture: true,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.dispatch('setLengthTrust', {
      valid: true,
      trustIndenture: true,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    expect(wrapper.findComponent(RegistrationLengthTrustAmendment).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(true)
    expect(wrapper.vm.trustIndenture).toBe(true)
    expect(wrapper.vm.showEditTrustIndenture).toBe(false)
    expect(wrapper.vm.editInProgress).toBe(false)
    expect(wrapper.vm.computedExpiryDateFormatted).toBeDefined()
  })
})
