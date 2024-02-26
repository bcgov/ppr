import { createComponent, setupMockStaffUser } from './utils'
import { MhrTransportPermit } from '@/views'
import { beforeEach, expect } from 'vitest'
import { DocumentId, FormCard, SimpleHelpToggle, UpdatedBadge } from '@/components/common'
import { nextTick } from 'vue'
import flushPromises from 'flush-promises'
import { TaxCertificate } from '@/components/mhrTransfers'
import { LocationChange } from '@/components/mhrTransportPermit'
import { AuthRoles, HomeLocationTypes, LocationChangeTypes, MhApiStatusTypes, ProductCode } from '@/enums'
import { useStore } from '@/store/store'
import { HomeLocationType, HomeCivicAddress, HomeLandOwnership } from '@/components/mhrRegistration'
import { mount } from '@vue/test-utils'
import { MhrRegistrationHomeLocationIF } from '@/interfaces'

const store = useStore()

const setupActiveTransportPermit = async () => {
  const newLocation: MhrRegistrationHomeLocationIF = {
    address: {
      city: "KELOWNA",
      country: "CA",
      postalCode: "",
      region: "BC",
      street: "123-720 COMMONWEALTH RD",
      streetAdditional: ''
    },
    landDistrict: "District 9",
    leaveProvince: false,
    locationType: HomeLocationTypes.OTHER_LAND,
    lot: "ABC",
    permitWithinSamePark: false,
    plan: "B",
    taxCertificate: true,
    taxExpiryDate: "2024-02-06T08:01:00+00:00"
  }

  await store.setMhrInformationPermitData({
    permitKey: 'Status',
    permitData: MhApiStatusTypes.ACTIVE
  })

  await store.setMhrTransportPermit({ key: 'landStatusConfirmation', value: true })
  await store.setMhrTransportPermit({ key: 'newLocation', value: newLocation })
  await nextTick()
}

describe('MhrTransportPermit', () => {
  let wrapper

  const activateLocationChange = async () => {
    const changeLocationBtn = await wrapper.find('#home-location-change-btn')
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
    expect(homeLandOwnershipText).toContain('Will the manufactured home')
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

    expect(wrapper.find('#transport-permit-home-location-type p').text()).toBe('Amend the new location type of the home.')
    expect(wrapper.find('#transport-permit-home-civic-address p').text()).toContain('Amend the Street Address')
  })

  it('should render amend transport permit badges', async () => {

    await setupActiveTransportPermit()
    await activateLocationChange()

    const locationChange = wrapper.findComponent(LocationChange)

    // check that amended badges are not shown
    expect(locationChange.findByTestId('amended-badge').exists()).toBeFalsy()

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
})
