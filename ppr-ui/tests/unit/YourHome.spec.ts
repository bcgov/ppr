import { YourHome } from '@/pages'
import {
  HomeCertification,
  HomeSections,
  ManufacturerMakeModel,
  RebuiltStatus,
  OtherInformation
} from '@/components/mhrRegistration'
import { MhrRegistrationType } from '@/resources'
import { RouteNames, ProductCode } from '@/enums'
import { createComponent, getTestId } from './utils'
import { mockedManufacturerAuthRoles } from './test-data'
import { HomeCertificationPrompt, ManufacturerMakeModelPrompt } from '@/resources/mhr-registration'
import { SimpleHelpToggle } from '@/components/common'
import { useStore } from '@/store/store'
const store = useStore()

describe('Your Home - Staff', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(MhrRegistrationType)

    wrapper = await createComponent(YourHome, { appReady: true }, RouteNames.YOUR_HOME)
  })

  it('renders and displays Your Home View', async () => {
    expect(wrapper.findComponent(YourHome).exists()).toBe(true)
  })

  it('renders and displays the correct headers and sub components', async () => {
    expect(wrapper.find('#mhr-make-model h2').text()).toBe('Manufacturer, Make, and Model')
    expect(wrapper.find(getTestId('make-model-prompt')).text()).toBe(ManufacturerMakeModelPrompt.staff)
    expect(wrapper.findComponent(ManufacturerMakeModel).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(false)
    expect(wrapper.find('#mhr-home-sections h2').text()).toBe('Home Sections')
    expect(wrapper.findComponent(HomeSections).exists()).toBe(true)
    expect(wrapper.find('#mhr-home-certification h2').text()).toBe('Home Certification')
    expect(wrapper.find(getTestId('home-certification-prompt')).text()).toBe(HomeCertificationPrompt.staff)
    expect(wrapper.findComponent(HomeCertification).exists()).toBe(true)
    expect(wrapper.find('#mhr-rebuilt-status h2').text()).toBe('Rebuilt Status')
    expect(wrapper.findComponent(RebuiltStatus).exists()).toBe(true)
    expect(wrapper.find('#mhr-other-information h2').text()).toBe('Other Information')
    expect(wrapper.findComponent(OtherInformation).exists()).toBe(true)
  })
})

describe('Your Home - Manufacturer', () => {
  let wrapper

  beforeAll(async () => {
    await store.setRegistrationType(MhrRegistrationType)
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.MANUFACTURER])
  })

  beforeEach(async () => {
    wrapper = await createComponent(YourHome, { appReady: true }, RouteNames.YOUR_HOME)
    await store.setAuthRoles(mockedManufacturerAuthRoles)
  })

  it('renders and displays Your Home View', async () => {
    expect(wrapper.findComponent(YourHome).exists()).toBe(true)
  })

  it('renders and displays the correct headers and sub components', async () => {
    expect(wrapper.find('#mhr-make-model h2').text()).toBe('Manufacturer, Make, and Model')
    expect(wrapper.find(getTestId('make-model-prompt')).text()).toContain(
      'Enter the Year of Manufacture (not the model year)'
    )
    expect(wrapper.findComponent(ManufacturerMakeModel).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    expect(wrapper.find('#mhr-home-sections h2').text()).toBe('Home Sections')
    expect(wrapper.findComponent(HomeSections).exists()).toBe(true)
    expect(wrapper.find('#mhr-home-certification h2').text()).toBe('Home Certification')
    expect(wrapper.find(getTestId('home-certification-prompt')).text()).toBe(HomeCertificationPrompt.manufacturer)
    expect(wrapper.findComponent(HomeCertification).exists()).toBe(true)
    expect(wrapper.findComponent(RebuiltStatus).exists()).toBe(false)
    expect(wrapper.findComponent(OtherInformation).exists()).toBe(false)
  })
})
