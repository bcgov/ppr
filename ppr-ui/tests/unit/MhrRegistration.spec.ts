// Libraries
import { useStore } from '../../src/store/store'

// local components
import { MhrRegistration } from '@/views'
import { ButtonFooter } from '@/components/common'
import { Stepper, StickyContainer } from '@/components/common'
import { MhrCorrectionStaff, MhrRegistrationType } from '@/resources'
import { defaultFlagSet } from '@/utils'
import { RouteNames } from '@/enums'
import { mockedManufacturerAuthRoles, mockedMhrRegistration } from './test-data'
import { createComponent } from './utils'
import { useNewMhrRegistration } from '@/composables'

const store = useStore()

describe('Mhr Registration', () => {
  let wrapper: any

  beforeEach(async () => {
    // Staff with MHR enabled
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setRegistrationType(MhrRegistrationType)
    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.YOUR_HOME)
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
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })
})

describe('Mhr Manufacturer Registration', () => {
  let wrapper: any

  beforeEach(async () => {
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)

    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.YOUR_HOME)
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
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })
})

describe('Mhr Correction', () => {
  let wrapper: any
  const { initDraftOrCurrentMhr } = useNewMhrRegistration()

  beforeEach(async () => {
    // Staff with MHR enabled
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setRegistrationType(MhrCorrectionStaff)
    await initDraftOrCurrentMhr(mockedMhrRegistration)
    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.SUBMITTING_PARTY)
  })

  it('renders and displays the Mhr Registration View', async () => {
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
    expect(wrapper.find('#registration-correction-header').text()).toBe('Registry Correction - Staff Error or Omission')
  })

  it('renders and displays the correct sub components', async () => {
    // Stepper
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    // Action button footers
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })
})
