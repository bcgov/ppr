import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import {
  mockedSelectSecurityAgreement,
  mockedVehicleCollateralExisting,
  mockedGeneralCollateralExisting,
  mockedDebtorsExisting,
  mockedSecuredPartiesExisting
} from './test-data'
import { EditTrustIndenture } from '@/components/registration'
import { createComponent } from './utils'

const store = useStore()

// Input field selectors / buttons
const doneButton: string = '#done-btn-trust-indenture'
const cancelButton: string = '#cancel-btn-trust-indenture'
const trustCheckbox: string = '#trust-indenture-checkbox'

describe('EditTrustAmendment component tests', () => {
  let wrapper
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

    wrapper = await createComponent(EditTrustIndenture, { currentTrustIndenture: false })
  })

  it('renders with no trust indenture change', async () => {
    expect(wrapper.findComponent(EditTrustIndenture).exists()).toBe(true)
    expect(wrapper.find(trustCheckbox).exists()).toBe(true)
    expect(wrapper.find(cancelButton).exists()).toBe(true)
    expect(wrapper.find(doneButton).exists()).toBe(true)
    expect(wrapper.vm.existingTrustIndenture).toBe(false)
    expect(wrapper.vm.trustIndenture).toBe(false)
    expect(wrapper.vm.lengthTrust.trustIndenture).toBe(false)
    wrapper.find(trustCheckbox).setValue(true)
    await nextTick()
    expect(wrapper.vm.trustIndenture).toBe(true)
    wrapper.find(cancelButton).trigger('click')
    await nextTick()
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
    wrapper.find(trustCheckbox).setValue(true)
    await nextTick()
    expect(wrapper.vm.trustIndenture).toBe(true)
    wrapper.find(doneButton).trigger('click')
    await nextTick()
    expect(wrapper.emitted().editTrustIndenture).toBeTruthy()
    expect(wrapper.vm.lengthTrust.trustIndenture).toBe(true)
  })
})
