// Libraries
import { useStore } from '../../src/store/store'

// local components
import { MhrRegistration } from '@/pages'
import { ButtonFooter , Stepper, StickyContainer } from '@/components/common'
import { MhrCorrectionStaff, MhrReRegistrationType, MhrRegistrationType } from '@/resources'
import { AuthRoles, HomeTenancyTypes, MhApiStatusTypes, RouteNames } from '@/enums'
import { mockMhrReRegistration, mockedManufacturerAuthRoles, mockedMhrRegistration, mockedPerson } from './test-data'
import { createComponent, getTestId } from './utils'
import { useMhrReRegistration, useNewMhrRegistration } from '@/composables'
import { nextTick } from 'vue'
import CautionBox from '@/components/common/CautionBox.vue'
import HomeOwnersTable from '@/components/mhrRegistration/HomeOwners/HomeOwnersTable.vue'
import SubmittingParty from '@/pages/newMhrRegistration/SubmittingParty.vue'
import HomeLocation from '@/pages/newMhrRegistration/HomeLocation.vue'
import HomeOwners from '@/pages/newMhrRegistration/HomeOwners.vue'
import type { MhrRegistrationHomeOwnerGroupIF } from '@/interfaces'
import { PreviousHomeOwners } from '@/components/mhrRegistration'
import ConnectFeeWidget from '@/components/connect/fee/ConnectFeeWidget.vue'
import { createPinia, setActivePinia } from 'pinia'
import flushPromises from 'flush-promises'

describe('Mhr Registration', () => {
  let wrapper, store, pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    // Staff with MHR enabled
    await store.setRegistrationType(MhrRegistrationType)
    await nextTick()
    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.YOUR_HOME, null, [pinia])
    await store.setRegistrationType(MhrRegistrationType)
    await nextTick()
  })

  it.only('renders and displays the Mhr Registration View', async () => {
    await store.setRegistrationType(MhrRegistrationType)
    await nextTick()
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
    expect(wrapper.find('#registration-header').text()).toBe('Manufactured Home Registration')
  })

  it('renders and displays the correct sub components', async () => {
    await store.setRegistrationType(MhrRegistrationType)
    await nextTick()
    // Stepper
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    // Action button footers
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(ConnectFeeWidget).exists()).toBe(true)
  })
})

describe('Mhr Manufacturer Registration', () => {
  let wrapper, store, pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    // Mock the getFooterButtonConfig getter
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)

    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.YOUR_HOME, null, [pinia])
  })

  it('renders and displays the Mhr Registration View', async () => {
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
    expect(wrapper.find('#registration-header').text()).toBe('Manufactured Home Registration')
  })

  it('renders and displays the correct sub components', async () => {
    // Stepper
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    // Action button footers
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(ConnectFeeWidget).exists()).toBe(true)
  })
})

describe('Mhr Correction', () => {
  let wrapper, store, pinia
  const { initDraftOrCurrentMhr } = useNewMhrRegistration()

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    // Staff with MHR enabled
    await store.setRegistrationType(MhrCorrectionStaff)
    await initDraftOrCurrentMhr(mockedMhrRegistration)
    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.SUBMITTING_PARTY, null, [pinia])
  })

  it('renders and displays the Mhr Registration View', async () => {
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
  })

  it('renders and displays the correct sub components', async () => {
    // Stepper
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    // Action button footers
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(ConnectFeeWidget).exists()).toBe(true)
  })
})

describe('Mhr Re-Registration', () => {
  let wrapper, store, pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    // Staff with MHR enabled
    await store.setAuthRoles([AuthRoles.PPR_STAFF])
    store.setRegistrationType(MhrReRegistrationType)
    store.setMhrStatusType(MhApiStatusTypes.EXEMPT)

    await store.setMhrInformation({
      permitDateTime: mockMhrReRegistration.permitDateTime,
      permitExpiryDateTime: mockMhrReRegistration.permitExpiryDateTime,
      permitRegistrationNumber: mockMhrReRegistration.permitRegistrationNumber,
      permitStatus: mockMhrReRegistration.permitStatus
    })
    await nextTick()

    const homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson] }] as MhrRegistrationHomeOwnerGroupIF[]
    useMhrReRegistration().setupPreviousOwners(homeOwnerGroup)
    useNewMhrRegistration().initDraftOrCurrentMhr(mockMhrReRegistration as any, false)
    await nextTick()

    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.SUBMITTING_PARTY, null, [pinia])
    await flushPromises()
    await nextTick()
  })

  it('renders and displays the Mhr Re-Registration View', async () => {
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.SUBMITTING_PARTY)

    expect(wrapper.findComponent(SubmittingParty).findComponent(CautionBox).exists()).toBe(false)

    // Go to Home Owners step
    wrapper.findComponent(Stepper).findAll('.step').at(2).trigger('click')
    await nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.HOME_OWNERS)
    const homeOwnersTable = wrapper.findComponent(HomeOwnersTable)
    expect(homeOwnersTable.find(getTestId('no-data-msg')).exists()).toBe(true) // should not have owners for Re-Reg
    expect(wrapper.findComponent(HomeOwners).findComponent(CautionBox).exists()).toBe(false)

    // Previous Home Owners
    const prevOwnersCard = wrapper.findComponent(PreviousHomeOwners)
    expect(prevOwnersCard.exists()).toBe(true)
    expect(prevOwnersCard.find(getTestId('card-header-label')).text()).toBe('Previous Home Owners')
    expect(prevOwnersCard.find(getTestId('card-toggle-label')).text()).toBe('Hide Previous Owners')
    expect(prevOwnersCard.find(getTestId('home-owner-tenancy-type')).text()).toContain(HomeTenancyTypes.SOLE)
    expect(prevOwnersCard.findComponent(HomeOwnersTable).exists()).toBe(true)

    const homeOwnersTableText = prevOwnersCard.findComponent(HomeOwnersTable).text()
    expect(homeOwnersTableText).toContain(mockedPerson.individualName.first)
    expect(homeOwnersTableText).toContain(mockedPerson.phoneNumber)
    expect(homeOwnersTableText).toContain(mockedPerson.address.street)

    // Go to Home Location step
    wrapper.findComponent(Stepper).findAll('.step').at(3).trigger('click')
    await nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.HOME_LOCATION)

    const homeLocationStepWrapper = wrapper.findComponent(HomeLocation)
    expect(homeLocationStepWrapper.findComponent(CautionBox).exists()).toBe(true)
  })
})
