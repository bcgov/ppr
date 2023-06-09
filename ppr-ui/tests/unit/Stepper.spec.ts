// Libraries
import Vue, { nextTick, toRefs } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { createLocalVue, shallowMount, Wrapper } from '@vue/test-utils'

// Components
import { Stepper } from '@/components/common'
import VueRouter from 'vue-router'
import { ProductCode, RouteNames } from '@/enums'

// Router
import mockRouter from './MockRouter'

// Auth Roles
import { mockedManufactuerAuthRoles } from './test-data'

// Others
import { MhrRegistrationType } from '@/resources'
import { getTestId } from './utils'
import { useMhrValidations } from '@/composables'
import { StepIF } from '@/interfaces'

Vue.use(Vuetify)
const vuetify = new Vuetify({})
const router = mockRouter.mock()

setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (mockRoute: RouteNames, propsData: any): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  localVue.use(VueRouter)
  document.body.setAttribute('data-app', 'true')
  if (router.currentRoute.name !== mockRoute) {
    router.replace({ name: mockRoute })
  }

  return shallowMount((Stepper as any), {
    localVue,
    router,
    store,
    propsData,
    vuetify
  })
}

describe('Stepper - MHR Staff Registration', () => {
  let expectedSteps: StepIF[]

  beforeAll(async () => {
    await store.setAuthRoles(['ppr-staff', 'staff'])
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.PPR])
    await store.setRegistrationType(MhrRegistrationType)
    expectedSteps = await store.getSteps
  })

  afterAll(async () => {
    await store.setAuthRoles([])
    await store.setUserProductSubscriptionsCodes([])
    await store.setRegistrationType(null)
  })

  it('renders correctly', async () => {
    const wrapper = createComponent(RouteNames.YOUR_HOME, { showStepErrorsFlag: false })
    // Verify that all steps are rendered correctly
    expect(wrapper.props().showStepErrorsFlag).toBe(false)
    const steps = wrapper.findAll('.step')
    expect(steps.length).toBe(expectedSteps.length)
  })

  it('verify steps', async () => {
    const wrapper = createComponent(RouteNames.YOUR_HOME, { showStepErrorsFlag: false })
    for (const step of expectedSteps) {
      const stepIcon = wrapper.find(`#${step.id}`)
      const stepText = wrapper.find(getTestId(step.id))
      // This is the icon for the step
      expect(stepIcon.text()).toContain(step.icon)
      expect(stepText.text()).toContain(step.text.replaceAll('<br />', ''))
    }
  })

  it('check stepper validation icon - validation flag off, step invalid', async () => {
    const wrapper = createComponent(RouteNames.YOUR_HOME, { showStepErrorsFlag: false })
    const validIcon = wrapper.find(getTestId(`step-valid-${expectedSteps[0].id}`))
    const invalidIcon = wrapper.find(getTestId(`step-invalid-${expectedSteps[0].id}`))

    expect(validIcon.isVisible()).toBe(false)
    expect(invalidIcon.isVisible()).toBe(false)
  })

  it('check stepper validation icon - validation flag on, step invalid', async () => {
    const wrapper = createComponent(RouteNames.YOUR_HOME, { showStepErrorsFlag: true })
    const validIcon = wrapper.find(getTestId(`step-valid-${expectedSteps[0].id}`))
    const invalidIcon = wrapper.find(getTestId(`step-invalid-${expectedSteps[0].id}`))

    expect(validIcon.isVisible()).toBe(false)
    expect(invalidIcon.isVisible()).toBe(true)
  })

  it('check stepper validation icon - step valid', async () => {
    // setup
    const {
      MhrCompVal,
      MhrSectVal,
      setValidation
    } = useMhrValidations(toRefs(store.getMhrRegistrationValidationModel))
    await setValidation(MhrSectVal.HOME_OWNERS_VALID, MhrCompVal.OWNERS_VALID, true)
    await nextTick()

    const wrapper = createComponent(RouteNames.YOUR_HOME, { showStepErrorsFlag: false })
    const validIcon = wrapper.find(getTestId(`step-valid-${expectedSteps[2].id}`)) // Your home valid step
    const invalidIcon = wrapper.find(getTestId(`step-invalid-${expectedSteps[2].id}`))

    expect(validIcon.isVisible()).toBe(true)
    expect(invalidIcon.isVisible()).toBe(false)

    // teardown
    await setValidation(MhrSectVal.HOME_OWNERS_VALID, MhrCompVal.OWNERS_VALID, false)
  })
})

describe('Stepper - MHR Manufactuer Registration', () => {
  let expectedSteps: StepIF[]
  beforeAll(async () => {
    await store.setAuthRoles(mockedManufactuerAuthRoles)
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR])
    await store.setRegistrationType(MhrRegistrationType)
    expectedSteps = await store.getSteps
  })

  afterAll(async () => {
    await store.setAuthRoles([])
    await store.setUserProductSubscriptionsCodes([])
    await store.setRegistrationType(null)
  })

  it('renders correctly', async () => {
    const wrapper = createComponent(RouteNames.YOUR_HOME, { showStepErrorsFlag: false })
    // Verify that all steps are rendered correctly
    expect(wrapper.props().showStepErrorsFlag).toBe(false)
    const steps = wrapper.findAll('.step')
    expect(steps.length).toBe(expectedSteps.length)
    await wrapper.setProps({ showStepErrorsFlag: true })
    expect(wrapper.props().showStepErrorsFlag).toBe(true)
  })

  it('verify steps', async () => {
    const wrapper = createComponent(RouteNames.YOUR_HOME, { showStepErrorsFlag: false })
    for (const step of expectedSteps) {
      const stepIcon = wrapper.find(`#${step.id}`)
      const stepText = wrapper.find(getTestId(step.id))
      // This is the icon for the step
      expect(stepIcon.text()).toContain(step.icon)
      expect(stepText.text()).toContain(step.text.replaceAll('<br />', ''))
    }
  })

  it('check current step', async () => {
    const wrapper = createComponent(expectedSteps[1].to, { showStepErrorsFlag: false })
    const currentStep = wrapper.find('.selected-btn')
    const btnForNotCurrentStep = wrapper.find(getTestId(expectedSteps[1].id))
    const btnForCurrentStep = wrapper.find(getTestId(`current-${expectedSteps[1].id}`))

    expect(currentStep.vm.$el.id).toBe(expectedSteps[1].id)
    expect(btnForNotCurrentStep.isVisible()).toBe(false)
    expect(btnForCurrentStep.isVisible()).toBe(true)
  })
})

// TODO: add tests for Stepper for PPR registration
