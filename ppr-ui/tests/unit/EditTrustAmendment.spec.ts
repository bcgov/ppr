// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  LengthTrustIF
} from '@/interfaces'
import {
  mockedSelectSecurityAgreement,
  mockedVehicleCollateralExisting,
  mockedGeneralCollateralExisting,
  mockedDebtorsExisting,
  mockedSecuredPartiesExisting
} from './test-data'

// Components
import { EditTrustIndenture } from '@/components/registration'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const doneButton: string = '#done-btn-trust-indenture'
const cancelButton: string = '#cancel-btn-trust-indenture'
const trustCheckbox: string = '#trust-indenture-checkbox'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  currentTrustIndenture: boolean
): Wrapper<any> {
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((EditTrustIndenture as any), {
    localVue,
    propsData: { currentTrustIndenture },
    store,
    vuetify
  })
}

describe('EditTrustAmendment component tests', () => {
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
    await store.dispatch('setOriginalLengthTrust', {
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.dispatch('setLengthTrust', {
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })

    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with no trust indenture change', async () => {
    expect(wrapper.findComponent(EditTrustIndenture).exists()).toBe(true)
    expect(wrapper.find(trustCheckbox).exists()).toBe(true)
    expect(wrapper.find(cancelButton).exists()).toBe(true)
    expect(wrapper.find(doneButton).exists()).toBe(true)
    expect(wrapper.vm.existingTrustIndenture).toBe(false)
    expect(wrapper.vm.trustIndenture).toBe(false)
    expect(wrapper.vm.lengthTrust.trustIndenture).toBe(false)
    wrapper.find(trustCheckbox).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.trustIndenture).toBe(true)
    wrapper.find(cancelButton).trigger('click')
    await Vue.nextTick()
    expect(wrapper.emitted().resetEvent).toBeTruthy()
    expect(wrapper.vm.lengthTrust.trustIndenture).toBe(false)
  })

  it('renders with trust indenture changed', async () => {
    expect(wrapper.findComponent(EditTrustIndenture).exists()).toBe(true)
    expect(wrapper.find(trustCheckbox).exists()).toBe(true)
    expect(wrapper.find(cancelButton).exists()).toBe(true)
    expect(wrapper.find(doneButton).exists()).toBe(true)
    expect(wrapper.vm.existingTrustIndenture).toBe(false)
    expect(wrapper.vm.trustIndenture).toBe(false)
    expect(wrapper.vm.lengthTrust.trustIndenture).toBe(false)
    wrapper.find(trustCheckbox).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.trustIndenture).toBe(true)
    wrapper.find(doneButton).trigger('click')
    await Vue.nextTick()
    expect(wrapper.emitted().editTrustIndenture).toBeTruthy()
    expect(wrapper.vm.lengthTrust.trustIndenture).toBe(true)
  })
})
