import { beforeEach } from 'vitest'
import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import { StepIF } from '@/interfaces'
import { ProductCode, RouteNames } from '@/enums'
import { MhrRegistrationType } from '@/resources'
import { createComponent, getTestId } from './utils'
import { Stepper } from '@/components/common'
import { mockedManufacturerAuthRoles } from './test-data'

const store = useStore()

describe('Stepper - MHR Staff Registration', () => {
  let wrapper
  let expectedSteps: StepIF[]

  beforeAll(async () => {
    await store.setAuthRoles(['ppr-staff', 'staff'])
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.PPR])
    await store.setRegistrationType(MhrRegistrationType)
    expectedSteps = await store.getMhrSteps
  })

  beforeEach(async () => {
    wrapper = await createComponent(Stepper, {
      stepConfig: expectedSteps,
      showStepErrors: false
    }, RouteNames.YOUR_HOME)
    await nextTick()
  })

  it('renders correctly', async () => {
    // Verify that all steps are rendered correctly
    expect(wrapper.vm.$props.showStepErrors).toBe(false)
    const steps = wrapper.findAll('.step')
    expect(steps.length).toBe(5)
    expect(steps.length).toBe(expectedSteps.length)
  })

  it('verify steps', async () => {
    expectedSteps.forEach((step, index) => {
      const steps = wrapper.findAll('.step')
      console.log(steps.at(index).text())
      expect(steps.at(index).text()).toContain(step.text.replaceAll('<br />', ''))
    })
  })

  it('check stepper validation icon - validation flag off, step invalid', async () => {
    const validIcon = wrapper.find(getTestId(`step-valid-${expectedSteps[0].id}`))
    const invalidIcon = wrapper.find(getTestId(`step-invalid-${expectedSteps[0].id}`))

    expect(validIcon.isVisible()).toBe(false)
    expect(invalidIcon.isVisible()).toBe(false)
  })

  it('check stepper validation icon - validation flag on, step invalid', async () => {
    wrapper = await createComponent(Stepper, {
      stepConfig: expectedSteps,
      showStepErrors: true
    }, RouteNames.YOUR_HOME)

    const validIcon = wrapper.find(getTestId(`step-valid-${expectedSteps[0].id}`))
    const invalidIcon = wrapper.find(getTestId(`step-invalid-${expectedSteps[0].id}`))

    expect(validIcon.isVisible()).toBe(false)
    expect(invalidIcon.isVisible()).toBe(true)
  })

  it('check stepper validation icon - step valid', async () => {
    expectedSteps[2].valid = true
    wrapper = await createComponent(Stepper, {
      stepConfig: expectedSteps,
      showStepErrors: false
    }, RouteNames.YOUR_HOME)
    await nextTick()

    const validIcon = wrapper.find(getTestId(`step-valid-${expectedSteps[2].id}`)) // Your home valid step
    const invalidIcon = wrapper.find(getTestId(`step-invalid-${expectedSteps[2].id}`))

    expect(validIcon.isVisible()).toBe(true)
    expect(invalidIcon.isVisible()).toBe(false)
  })
})

describe('Stepper - MHR Manufacturer Registration', () => {
  let wrapper
  let expectedSteps: StepIF[]

  beforeAll(async () => {
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.MANUFACTURER])
    expectedSteps = await store.getMhrSteps
  })

  beforeEach(async () => {
    wrapper = await createComponent(
      Stepper,
      {
      stepConfig: expectedSteps,
      showStepErrors: false
      },
      RouteNames.YOUR_HOME
    )
    await nextTick()
  })

  it('renders correctly', async () => {
    // Verify that all steps are rendered correctly
    expect(wrapper.props().showStepErrors).toBe(false)
    const steps = wrapper.findAll('.step')
    expect(steps.length).toBe(2)
    expect(steps.length).toBe(expectedSteps.length)

    wrapper = await createComponent(
      Stepper,
      {
        stepConfig: expectedSteps,
        showStepErrors: true
      },
      RouteNames.YOUR_HOME
    )
    await nextTick()
    expect(wrapper.props().showStepErrors).toBe(true)
  })

  it('verify steps', async () => {
    expectedSteps.forEach((step, index) => {
      const steps = wrapper.findAll('.step')
      console.log(steps.at(index).text())
      expect(steps.at(index).text()).toContain(step.text.replaceAll('<br />', ''))
    })
  })

  it('check current step', async () => {
    wrapper = await createComponent(
      Stepper,
      {
        stepConfig: expectedSteps,
        showStepErrors: false
      },
      expectedSteps[1].to
    )
    await nextTick()

    expect(wrapper.vm.$route.name).toBe(expectedSteps[1].to)
    const btnForNotCurrentStep = wrapper.find(getTestId(expectedSteps[1].id))
    const btnForCurrentStep = wrapper.find(getTestId(`current-${expectedSteps[1].id}`))


    expect(btnForNotCurrentStep.isVisible()).toBe(false)
    expect(btnForCurrentStep.isVisible()).toBe(true)
  })
})
