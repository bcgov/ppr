import { beforeEach, expect } from 'vitest'
import { nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import flushPromises from 'flush-promises'

import {
  AuthRoles,
  LocationChangeTypes,
  ProductCode,
  RouteNames,
} from '@/enums'
import {
  BaseDialog,
  ConfirmCompletion,
  DocumentId,
  FormCard,
  InputFieldDatePicker,
  LocationChange,
  LocationChangeReview,
  SimpleHelpToggle,
  StaffPayment,
  StickyContainer,
  TaxCertificate,
  UpdatedBadge,
} from '@/components/common'
import { HomeCivicAddress, HomeLandOwnership, HomeLocationReview, HomeLocationType } from '@/components/mhrRegistration'
import { MhrInformation, MhrTransportPermit } from '@/views'
import { useStore, useTransportPermits } from '@/store/store'
import { calendarDates, shortPacificDate, defaultFlagSet } from '@/utils'
import { incompleteRegistrationDialog } from '@/resources/dialogOptions'

import { createComponent, setupActiveTransportPermit, setupMockStaffUser } from './utils'
import { mockTransportPermitNewLocation, mockedMhRegistration } from './test-data'

const store = useStore()

describe('MhrTransportPermit', () => {
  let wrapper

  const activateLocationChange = async () => {
    const changeLocationBtn = wrapper.find('#home-location-change-btn')
    expect(changeLocationBtn.exists()).toBeTruthy()
    changeLocationBtn.trigger('click')
    await nextTick()
  }

  const selectTransportPermit = async () => {
    const locationChange = wrapper.findComponent(LocationChange)
    locationChange.vm.selectLocationType(LocationChangeTypes.TRANSPORT_PERMIT)
    await nextTick()
  }

  beforeEach(async () => {
    await setupMockStaffUser()
    wrapper = await createComponent(MhrTransportPermit)
  })

  afterEach(async () => {
    wrapper.vm.setLocationChange(false)
    await store.setAuthRoles(['staff', 'ppr'])
    await store.setMhrTransportPermitLocationChangeType(null)
    await store.setMhrInformationPermitData({
      permitKey: 'Status',
      permitData: false
    })
  })

  afterAll(async () => {
    useTransportPermits().resetTransportPermit(true)
  })

  it('does not render location change content when isChangeLocationActive is false', async () => {
    expect(wrapper.findComponent(MhrTransportPermit).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(false)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(false)
    expect(wrapper.findComponent(FormCard).exists()).toBe(false)
    expect(wrapper.find('#location-change-type-section').exists()).toBe(false)
    expect(wrapper.findComponent(LocationChange).exists()).toBe(false)
  })

  it('renders location change content when isChangeLocationActive is true', async () => {
    // Open Change Location Flow
    const changeLocationBtn = await wrapper.find('#home-location-change-btn')
    changeLocationBtn.trigger('click')
    await nextTick()

    expect(wrapper.findComponent(MhrTransportPermit).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(true)
    expect(wrapper.findComponent(FormCard).exists()).toBe(true)
    expect(wrapper.find('#location-change-type-section').exists()).toBe(true)
    expect(wrapper.findComponent(LocationChange).exists()).toBe(true)
  })

  it('enables change location by default', async () => {
    expect(wrapper.vm.disable).toBe(false)
    const changeLocationBtn = await wrapper.find('#home-location-change-btn')
    expect(changeLocationBtn.attributes().disabled).toBeUndefined()
  })

  it('disables change location when prop is set', async () => {
    wrapper = await createComponent(MhrTransportPermit, { disable: true })
    await nextTick()
    await flushPromises()

    expect(wrapper.vm.disable).toBe(true)
    const changeLocationBtn = await wrapper.find('#home-location-change-btn')
    expect(changeLocationBtn.attributes().disabled).toBeDefined()
  })

  it('should render two location change options for Qualified Supplier', async () => {
    // setup Qualified Supplier as Manufacturer
    await store.setAuthRoles([AuthRoles.MHR_TRANSFER_SALE])
    await store.setUserProductSubscriptionsCodes([ProductCode.MANUFACTURER])
    await activateLocationChange()
    await nextTick()

    const locationChangeDropdown = wrapper.findComponent(LocationChange).findComponent('.v-select')
    expect(locationChangeDropdown.vm.items.length).toBe(2)
  })

  it('should render different location change options', async () => {
    await activateLocationChange()

    const locationChange = wrapper.findComponent(LocationChange)
    const locationChangeDropdown = locationChange.findComponent('.v-select')

    expect(locationChangeDropdown.exists()).toBe(true)
    expect(locationChangeDropdown.vm.items.length).toBe(3)

    // select transport permit
    locationChange.vm.selectLocationType(LocationChangeTypes.TRANSPORT_PERMIT)
    await nextTick()
    expect(locationChange.find('#transport-permit-location-type').exists()).toBe(true)

    // select transport permit within same park
    locationChange.vm.selectLocationType(LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK)
    await nextTick()
    expect(locationChange.find('#transport-permit-location-type').exists()).toBe(false)
  })

  it('should render transport permit form and its components (staff)', async () => {
    await activateLocationChange()
    await selectTransportPermit()
    const locationChange = wrapper.findComponent(LocationChange)

    expect(locationChange.findComponent(HomeLocationType).exists()).toBe(true)
    expect(locationChange.findComponent(HomeCivicAddress).exists()).toBe(true)
    expect(locationChange.findComponent(HomeLandOwnership).exists()).toBe(true)
    expect(locationChange.findComponent(TaxCertificate).exists()).toBe(true)

    const homeLandOwnershipText = locationChange.findComponent(HomeLandOwnership).text()
    expect(homeLandOwnershipText).toContain('Is the manufactured home')
  })

  it('should render all validation errors', async () => {
    await activateLocationChange()

    // mount component and validate
    wrapper = mount(MhrTransportPermit, {
      props: {
        disable: false,
        validate: true
      }
    })
    await nextTick()

    // two errors: Document Id and Location Change Type dropdown
    expect(wrapper.findAll('.border-error-left').length).toBe(2)

    // select Transport Permit option from dropdown
    await selectTransportPermit()

    // should show errors for all components
    expect(wrapper.findAll('.border-error-left').length).toBe(5)

    // no badges should be displayed
    expect(wrapper.findAll('#updated-badge-component').length).toBe(0)
  })

  it('should render amend transport permit form and its components (staff)', async () => {
    defaultFlagSet['mhr-amend-transport-permit-enabled'] = true
    wrapper = await createComponent(MhrTransportPermit)

    await setupActiveTransportPermit()

    expect(wrapper.find('#home-location-change-btn').text()).toBe('Amend Transport Permit')

    await activateLocationChange()

    const locationChange = wrapper.findComponent(LocationChange)

    expect(locationChange.findComponent(FormCard).exists()).toBe(false)
    expect(locationChange.findComponent(HomeLocationType).exists()).toBe(true)
    expect(locationChange.findComponent(HomeCivicAddress).exists()).toBe(true)
    expect(locationChange.findComponent(HomeLandOwnership).exists()).toBe(true)
    expect(locationChange.findComponent(TaxCertificate).exists()).toBe(false)

    // no badges should be displayed
    expect(locationChange.findAll('#updated-badge-component').length).toBe(0)

    expect(wrapper.find('#transport-permit-home-location-type p').text()).toBe(
      'Amend the new location type of the home.'
    )
    expect(wrapper.find('#transport-permit-home-civic-address p').text()).toContain('Amend the Street Address')
  })

  it('should render amend transport permit badges', async () => {
    defaultFlagSet['mhr-amend-transport-permit-enabled'] = true
    wrapper = await createComponent(MhrTransportPermit)

    await setupActiveTransportPermit()
    await activateLocationChange()

    const locationChange = wrapper.findComponent(LocationChange)

    // check that amended badges and errors are not shown
    expect(locationChange.findByTestId('amended-badge').exists()).toBeFalsy()
    expect(locationChange.findAll('.border-error-left').length).toBe(0)

    // enter new values to trigger the badges

    const locationType = locationChange.findComponent(HomeLocationType)
    locationType.find('#home-park-option').setValue(true)
    await nextTick()
    expect(locationType.findByTestId('AMENDED-badge').exists()).toBeTruthy()

    const civicAddress = locationChange.findComponent(HomeCivicAddress)
    civicAddress.find('#city').setValue('New City')
    await nextTick()
    expect(civicAddress.findByTestId('AMENDED-badge').exists()).toBeTruthy()

    const landOwnership = locationChange.findComponent(HomeLandOwnership)
    landOwnership.find('#no-option').setValue(true)
    await nextTick()
    expect(landOwnership.findByTestId('AMENDED-badge').exists()).toBeTruthy()

    expect(locationChange.findAllComponents(UpdatedBadge).length).toBe(3)
  })

  it('should correctly show and hide Amend Transport Permit button with a feature flag', async () => {
    // disable amend FF
    defaultFlagSet['mhr-transport-permit-enabled'] = true
    defaultFlagSet['mhr-amend-transport-permit-enabled'] = false
    wrapper = await createComponent(MhrTransportPermit)

    // Transport Permit button should exist (FF is on)
    expect(wrapper.findByTestId('transport-permit-btn').exists()).toBeTruthy()

    await setupActiveTransportPermit()
    // Amend Transport Permit button should not exist (FF is off)
    expect(wrapper.findByTestId('amend-transport-permit-btn').exists()).toBeFalsy()

    // setup new component with amend FF enabled
    defaultFlagSet['mhr-amend-transport-permit-enabled'] = true
    wrapper = await createComponent(MhrTransportPermit)
    expect(wrapper.findByTestId('amend-transport-permit-btn').exists()).toBeTruthy()
    expect(wrapper.findByTestId('transport-permit-btn').exists()).toBeFalsy()
  })
})

describe('Mhr Information Transport Permit', async () => {
  let wrapper

  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeEach(async () => {
    defaultFlagSet['mhr-transport-permit-enabled'] = true

    wrapper = await createComponent(
      MhrInformation,
      { appReady: true, isMhrTransfer: false },
      RouteNames.MHR_INFORMATION
    )
    await store.setAuthRoles([AuthRoles.PPR_STAFF])
    wrapper.vm.dataLoaded = true
  })

  // TRANSPORT PERMIT TESTS

  it('should validate Mhr Info page when Transport Permit activated', async () => {
    // setup Transport Permit
    await nextTick()

    // open Transport Permit
    wrapper.findComponent(MhrTransportPermit).find('#home-location-change-btn').trigger('click')
    await nextTick()

    await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    expect(wrapper.findAll('.border-error-left').length).toBe(2)
    expect(wrapper.findComponent(MhrTransportPermit).findAll('#updated-badge-component').length).toBe(0)

    // reset transport permit change
    useTransportPermits().resetTransportPermit(true)
  })

  it('should show Registration Not Completed dialog when cancelling Transport Permit', async () => {
    // setup Transport Permit

    wrapper.vm.validate = false
    await nextTick()

    const TransportPermitComponent = wrapper.findComponent(MhrTransportPermit)
    expect(TransportPermitComponent.exists()).toBeTruthy()
    expect(TransportPermitComponent.findComponent(DocumentId).exists()).toBeFalsy()

    // open Transport Permit
    TransportPermitComponent.find('#home-location-change-btn').trigger('click')
    await nextTick()

    expect(TransportPermitComponent.findComponent(DocumentId).exists()).toBeTruthy()

    TransportPermitComponent.findComponent(DocumentId).find('#doc-id-field').setValue('123456789')
    await nextTick()

    expect(store.getStateModel.unsavedChanges).toBe(true)
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    expect(wrapper.vm.showIncompleteRegistrationDialog).toBe(true)
    await nextTick()

    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)

    const dialogTitle = wrapper.find('.dialog-title')
    expect(dialogTitle.exists()).toBe(true)
    expect(dialogTitle.text()).toBe(incompleteRegistrationDialog.title)

    // click to Return to Registration
    const acceptBtn = await wrapper.find('#accept-btn')

    await acceptBtn.trigger('click')
    await nextTick()

    expect(wrapper.vm.showIncompleteRegistrationDialog).toBe(false)

    // reset transport permit change
    useTransportPermits().resetTransportPermit(true)
  })

  it('should hide Transport Permit Tax certificate when an Active Home Outside BC', async () => {
    // setup Transport Permit
    await store.setMhrInformation(mockedMhRegistration)
    await store.setMhrLocation({ key: 'address', value: { region: 'AB' } })

    await nextTick()

    // open Transport Permit
    wrapper.findComponent(MhrTransportPermit).find('#home-location-change-btn').trigger('click')
    await nextTick()

    expect(useTransportPermits().isChangeLocationActive.value).toBe(true)

    const locationChange = wrapper.findComponent(LocationChange)
    locationChange.vm.selectLocationType(LocationChangeTypes.TRANSPORT_PERMIT)

    await nextTick()

    expect(locationChange.findComponent(HomeLocationType).exists()).toBe(true)
    expect(locationChange.findComponent(HomeCivicAddress).exists()).toBe(true)
    expect(locationChange.findComponent(HomeLandOwnership).exists()).toBe(true)
    expect(locationChange.findComponent(TaxCertificate).exists()).toBe(false)

    // reset staff role and transport permit
    await store.setAuthRoles([AuthRoles.MHR])
    useTransportPermits().setLocationChange(false)
  })

  it('should show Transport Permit Tax certificate when an Active Home within BC', async () => {
    // setup Transport Permit
    await store.setMhrInformation(mockedMhRegistration)
    await store.setMhrLocation({ key: 'address', value: { region: 'BC' } })

    await nextTick()

    // open Transport Permit
    wrapper.findComponent(MhrTransportPermit).find('#home-location-change-btn').trigger('click')
    await nextTick()

    expect(useTransportPermits().isChangeLocationActive.value).toBe(true)

    const locationChange = wrapper.findComponent(LocationChange)
    locationChange.vm.selectLocationType(LocationChangeTypes.TRANSPORT_PERMIT)

    await nextTick()

    expect(locationChange.findComponent(HomeLocationType).exists()).toBe(true)
    expect(locationChange.findComponent(HomeCivicAddress).exists()).toBe(true)
    expect(locationChange.findComponent(HomeLandOwnership).exists()).toBe(true)
    expect(locationChange.findComponent(TaxCertificate).exists()).toBe(true)
    expect(wrapper.findAll('#updated-badge-component').length).toBe(0)

    // reset staff role and transport permit
    await store.setAuthRoles([AuthRoles.MHR])
    useTransportPermits().setLocationChange(false)
  })

  it('should show Review and Confirm page for Transport Permit for Staff', async () => {
    // setup Transport Permit
    await nextTick()

    // open Transport Permit
    wrapper.findComponent(MhrTransportPermit).find('#home-location-change-btn').trigger('click')
    await nextTick()

    expect(useTransportPermits().isChangeLocationActive.value).toBe(true)

    store.setMhrTransportPermit({ key: 'documentId', value: '12345678' })
    wrapper.findComponent(MhrTransportPermit).findComponent(DocumentId).vm.isUniqueDocId = true
    wrapper.vm.setValidation('isDocumentIdValid', true)

    const locationChange = wrapper.findComponent(LocationChange)
    locationChange.vm.selectLocationType(LocationChangeTypes.TRANSPORT_PERMIT)

    await nextTick()

    expect(locationChange.findComponent(HomeLocationType).exists()).toBe(true)
    expect(locationChange.findComponent(HomeCivicAddress).exists()).toBe(true)
    expect(locationChange.findComponent(HomeLandOwnership).exists()).toBe(true)
    expect(locationChange.findComponent(TaxCertificate).exists()).toBe(true)

    expect(wrapper.findAll('.border-error-left').length).toBe(0)

    locationChange.findComponent(HomeLocationType).find('#lot-option').setValue(true)
    await nextTick()
    locationChange.findComponent(HomeLocationType).find('.v-text-field').find('input').setValue('ABC Dealer')

    // set civic address fields
    const civicAddressSection = locationChange.findComponent(HomeCivicAddress)
    store.setMhrTransportPermitNewCivicAddress({ key: 'country', value: 'CA' })
    await nextTick()
    store.setMhrTransportPermitNewCivicAddress({ key: 'region', value: 'BC' })
    civicAddressSection.find('#city').setValue('Vancouver')
    await nextTick()
    await nextTick()

    // set own land
    locationChange.findComponent(HomeLandOwnership).find('#yes-option').setValue(true)
    await nextTick()

    // set tax certificate expiry date (future date)
    locationChange
      .findComponent(TaxCertificate)
      .findComponent(InputFieldDatePicker)
      .vm.$emit('emitDate', calendarDates.tomorrow)
    wrapper.vm.validate = true
    await nextTick()

    expect(wrapper.findAll('.border-error-left').length).toBe(0)

    // go to review page
    wrapper.vm.isReviewMode = true
    await nextTick()

    expect(wrapper.find('h1').text()).toBe('Review and Confirm')
    expect(wrapper.findComponent(LocationChangeReview).exists()).toBeTruthy()
    expect(wrapper.find('.review-header').text()).toBe('Location Change')

    const locationChangeReviewText = wrapper.findComponent(LocationChangeReview).text()

    expect(locationChangeReviewText).toContain('12345678')
    expect(locationChangeReviewText).toContain('Transport Permit')
    expect(locationChangeReviewText).toContain('Vancouver BC')
    expect(locationChangeReviewText).toContain('Canada')
    expect(wrapper.findComponent(LocationChangeReview).findAll('#updated-badge-component').length).toBe(0)

    const homeLocationReviewText = wrapper.findComponent(LocationChangeReview).findComponent(HomeLocationReview).text()

    expect(homeLocationReviewText).toContain('The manufactured home is located on land')
    expect(homeLocationReviewText).toContain('Tax Certificate Expiry Date')
    expect(homeLocationReviewText).toContain(shortPacificDate(calendarDates.tomorrow))

    // reset staff role and transport permit
    await store.setAuthRoles([AuthRoles.MHR])
    useTransportPermits().setLocationChange(false)
  })

  it('should show Review and Confirm page for Transport Permit for QS', async () => {
    // setup Transport Permit
    await store.setAuthRoles([AuthRoles.MHR_TRANSFER_SALE])
    await store.setUserProductSubscriptionsCodes([ProductCode.MANUFACTURER])
    wrapper.vm.dataLoaded = true
    await nextTick()

    // open Transport Permit
    wrapper.findComponent(MhrTransportPermit).find('#home-location-change-btn').trigger('click')
    await nextTick()
    expect(useTransportPermits().isChangeLocationActive.value).toBe(true)

    expect(wrapper.findComponent(DocumentId).exists()).toBe(false)

    const locationChange = wrapper.findComponent(LocationChange)
    locationChange.vm.selectLocationType(LocationChangeTypes.TRANSPORT_PERMIT)
    await nextTick()

    locationChange.findComponent(HomeLocationType).find('#home-park-option').setValue(true)
    await nextTick()

    const homeLocationTextFields = locationChange.findComponent(HomeLocationType).findAll('.v-text-field')
    homeLocationTextFields.at(0).find('input').setValue('ABC Park Name') // park name
    homeLocationTextFields.at(1).find('input').setValue('165') // pad number

    // set civic address fields
    const civicAddressSection = locationChange.findComponent(HomeCivicAddress)
    store.setMhrTransportPermitNewCivicAddress({ key: 'country', value: 'CA' })
    await nextTick()
    store.setMhrTransportPermitNewCivicAddress({ key: 'region', value: 'BC' })
    civicAddressSection.find('#city').setValue('Victoria')
    await nextTick()
    await nextTick()

    // set own land
    locationChange.findComponent(HomeLandOwnership).find('#no-option').setValue(true)
    await nextTick()

    // set tax certificate expiry date (future date)
    locationChange.findComponent(TaxCertificate).findComponent(InputFieldDatePicker).vm.$emit('emitDate', '05-05-2024')
    wrapper.vm.validate = true
    await nextTick()

    expect(wrapper.findAll('.border-error-left').length).toBe(0)

    // go to review page
    wrapper.vm.isReviewMode = true
    await nextTick()

    expect(wrapper.find('h1').text()).toBe('Review and Confirm')
    expect(wrapper.find('.review-header').text()).toBe('Location Change')

    // Staff Payment component should not exist for QS role
    expect(wrapper.findComponent(StaffPayment).exists()).toBe(false)

    const locationChangeReviewText = wrapper.findComponent(LocationChangeReview).text()

    expect(locationChangeReviewText).not.toContain('Document ID') // Doc ID does not exist for QS
    expect(locationChangeReviewText).toContain('Transport Permit')
    expect(locationChangeReviewText).toContain('Manufactured home park')
    expect(locationChangeReviewText).toContain('Victoria BC')
    expect(locationChangeReviewText).toContain('Canada')
    expect(wrapper.findComponent(LocationChangeReview).findAll('#updated-badge-component').length).toBe(0)

    const homeLocationReviewText = wrapper.findComponent(LocationChangeReview).findComponent(HomeLocationReview).text()

    expect(homeLocationReviewText).toContain('The manufactured home is not located on land')
    expect(homeLocationReviewText).toContain('Tax Certificate Expiry Date')
    expect(homeLocationReviewText).toContain(shortPacificDate('05-05-2024'))

    const confirmCompletionReviewText = wrapper.findComponent(ConfirmCompletion).text()

    // confirm text is different than regular text for Transport Permit
    expect(confirmCompletionReviewText).toContain('I am duly authorized to submit this registration')

    // reset staff role and transport permit
    await store.setAuthRoles([AuthRoles.MHR])
    useTransportPermits().setLocationChange(false)
  })

  it('should validate amend transport permit components and top error message', async () => {
    // setup Transport Permit
    defaultFlagSet['mhr-amend-transport-permit-enabled'] = true
    wrapper.vm.dataLoaded = true

    await setupActiveTransportPermit()
    await nextTick()

    // set mhr registration location data for it to be prefilled when working with Amend Transport Permit
    const regLocation = store.getMhrRegistrationLocation
    store.setMhrLocationAllFields({ ...regLocation, ...mockTransportPermitNewLocation })
    await nextTick()

    // open Amend Transport Permit
    wrapper.find('#home-location-change-btn').trigger('click')
    await nextTick()

    const locationChange = wrapper.findComponent(LocationChange)

    // should not show component error nor global msg
    expect(locationChange.findAll('.border-error-left').length).toBe(0)
    expect(locationChange.findByTestId('amend-permit-changes-required-msg').exists()).toBeFalsy()
    expect(useTransportPermits().hasAmendmentChanges.value).toBe(false)

    // trigger page errors by going to review
    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // should show 3 component errors, global error msg and no amend badges
    expect(locationChange.findAll('.border-error-left').length).toBe(3)
    expect(locationChange.findByTestId('amend-permit-changes-required-msg').exists()).toBeTruthy()
    expect(locationChange.findAll('#updated-badge-component').length).toBe(0)
    expect(useTransportPermits().hasAmendmentChanges.value).toBe(false)

    // make Amendment change to hide all errors
    locationChange.findComponent(HomeLandOwnership).find('#no-option').setValue(true)
    await nextTick()

    // amend changes has been made
    expect(useTransportPermits().hasAmendmentChanges.value).toBe(true)

    // should be no errors (as one value was amended) and one amend badge
    expect(locationChange.findAll('.border-error-left').length).toBe(0)
    expect(locationChange.findAll('#updated-badge-component').length).toBe(1)

    // reset the changes
    locationChange.findComponent(HomeLandOwnership).find('#yes-option').setValue(true)
    await nextTick()

    // errors should be shown again
    expect(locationChange.findAll('.border-error-left').length).toBe(3)
    expect(locationChange.findAll('#updated-badge-component').length).toBe(0)
    expect(locationChange.findByTestId('amend-permit-changes-required-msg').exists()).toBeTruthy()

    // change another value to remove errors and show amend badge
    locationChange.findComponent(HomeLocationType).find('.v-text-field').find('input').setValue('Park Villa')
    await nextTick()

    expect(locationChange.findAll('.border-error-left').length).toBe(0)
    expect(locationChange.findAll('#updated-badge-component').length).toBe(1)
    expect(locationChange.findByTestId('amend-permit-changes-required-msg').exists()).toBeFalsy()

    // reset feature flags
    defaultFlagSet['mhr-amend-transport-permit-enabled'] = false
    useTransportPermits().setLocationChange(false)
  })

  it('should have amended badges on Review and Confirm page for Transport Permit', async () => {
    // setup Transport Permit
    defaultFlagSet['mhr-amend-transport-permit-enabled'] = true

    wrapper = await createComponent(
      MhrInformation,
      { appReady: true, isMhrTransfer: false },
      RouteNames.MHR_INFORMATION
    )
    wrapper.vm.dataLoaded = true

    await setupActiveTransportPermit()
    await nextTick()

    // set mhr registration location data for it to be prefilled when working with Amend Transport Permit
    const regLocation = store.getMhrRegistrationLocation
    store.setMhrLocationAllFields({ ...regLocation, ...mockTransportPermitNewLocation })
    await nextTick()

    // open Amend Transport Permit
    wrapper.find('#home-location-change-btn').trigger('click')
    await nextTick()

    const locationChange = wrapper.findComponent(LocationChange)
    expect(locationChange.findAll('#updated-badge-component').length).toBe(0)

    // make amendment changes
    locationChange.findComponent(HomeLocationType).find('.v-text-field').find('input').setValue('Park Villa') // park name
    locationChange.findComponent(HomeLandOwnership).find('#no-option').setValue(true) // own land radio

    await nextTick()
    expect(locationChange.findAll('#updated-badge-component').length).toBe(2)

    // overwrite validations to be able to go to Review and Confirm page
    wrapper.vm.setValidation('isDocumentIdValid', true)
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)

    // go to next pge
    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.find('h1').text()).toBe('Review and Confirm')

    const locationChangeReview = wrapper.findComponent(LocationChangeReview)

    // should show two amended badges for the two values that were updated
    expect(locationChangeReview.findAll('#updated-badge-component').length).toBe(2)
    // transport permit store should have amendment prop
    expect(store.getMhrTransportPermit.amendment).toBe(true)
  })
})
