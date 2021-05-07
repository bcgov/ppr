// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router' // eslint-disable-line no-unused-vars
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, shallowMount, Wrapper } from '@vue/test-utils'

// Components
import { ButtonFooter } from '@/components/common'
import { Dashboard, LengthTrust, AddSecuredPartiesAndDebtors, AddCollateral, ReviewConfirm } from '@/views'

// Other
import mockRouter from './MockRouter'
import { RouteNames, StatementTypes } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons
const cancelBtn: string = '#reg-cancel-btn'
const saveBtn: string = '#reg-save-btn'
const saveResumeBtn: string = '#reg-save-resume-btn'
const backBtn: string = '#reg-back-btn'
const nextBtn: string = '#reg-next-btn'

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

const router = mockRouter.mock()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  currentStatementType: String,
  testRouter: VueRouter,
  currentStepName: String
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  // await router.push({ name: 'length-trust' })
  document.body.setAttribute('data-app', 'true')
  return mount(ButtonFooter, {
    localVue,
    propsData: { currentStatementType, router, currentStepName },
    store,
    router,
    vuetify
  })
}

describe('New Financing Statement Registration Buttons Step 1', () => {
  let wrapper: Wrapper<any>
  let wrapper2: any // eslint-disable-line no-unused-vars
  const currentStatementType: String = String(StatementTypes.FINANCING_STATEMENT)
  const currentStepName: String = String(RouteNames.LENGTH_TRUST)

  beforeEach(async () => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    wrapper2 = shallowMount(LengthTrust, { localVue, store, router, vuetify })
    wrapper = createComponent(currentStatementType, router, currentStepName)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with step 1 values', async () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(true)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(false)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
    expect(wrapper.vm.statementType).toBe(StatementTypes.FINANCING_STATEMENT)
    expect(wrapper.vm.stepName).toBe(RouteNames.LENGTH_TRUST)
    expect(wrapper.vm.buttonConfig.showCancel).toBe(true)
    expect(wrapper.vm.buttonConfig.showSave).toBe(true)
    expect(wrapper.vm.buttonConfig.showSaveResume).toBe(true)
    expect(wrapper.vm.buttonConfig.showNext).toBe(true)
    expect(wrapper.vm.buttonConfig.showBack).toBe(false)
    expect(wrapper.vm.buttonConfig.backRouteName).toBe('')
    expect(wrapper.vm.buttonConfig.nextRouteName).toBe(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)
    expect(wrapper.vm.buttonConfig.nextText).toBe('Add Secured Parties and Debtors')
  })
  it('Step 1 cancel button event', async () => {
    wrapper.find(cancelBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Step 1 next button event', async () => {
    wrapper.find(nextBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Step 1 submitCancel', async () => {
    wrapper.vm.submitCancel()
    await Vue.nextTick()
  })
  it('Step 1 submitNext', async () => {
    wrapper.vm.submitNext()
    await Vue.nextTick()
  })
})
describe('New Financing Statement Registration Buttons Step 2', () => {
  let wrapper: Wrapper<any>
  let wrapper2: any // eslint-disable-line no-unused-vars
  const currentStatementType: String = String(StatementTypes.FINANCING_STATEMENT)
  const currentStepName: String = String(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)

  beforeEach(async () => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    wrapper2 = shallowMount(AddSecuredPartiesAndDebtors, { localVue, store, router, vuetify })
    wrapper = createComponent(currentStatementType, router, currentStepName)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with step 2 values', async () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(true)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(true)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
    expect(wrapper.vm.statementType).toBe(StatementTypes.FINANCING_STATEMENT)
    expect(wrapper.vm.stepName).toBe(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)
    expect(wrapper.vm.buttonConfig.showCancel).toBe(true)
    expect(wrapper.vm.buttonConfig.showSave).toBe(true)
    expect(wrapper.vm.buttonConfig.showSaveResume).toBe(true)
    expect(wrapper.vm.buttonConfig.showNext).toBe(true)
    expect(wrapper.vm.buttonConfig.showBack).toBe(true)
    expect(wrapper.vm.buttonConfig.backRouteName).toBe(RouteNames.LENGTH_TRUST)
    expect(wrapper.vm.buttonConfig.nextRouteName).toBe(RouteNames.ADD_COLLATERAL)
    expect(wrapper.vm.buttonConfig.nextText).toBe('Add Collateral')
  })
  it('Step 2 cancel button event', async () => {
    wrapper.find(cancelBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Step 2 back button event', async () => {
    wrapper.find(backBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Step 2 next button event', async () => {
    wrapper.find(nextBtn).trigger('click')
    await Vue.nextTick()
  })

  it('Step 2 submitCancel', async () => {
    wrapper.vm.submitCancel()
    await Vue.nextTick()
  })
  it('Step 2 submitBack', async () => {
    wrapper.vm.submitBack()
    await Vue.nextTick()
  })
  it('Step 2 submitNext', async () => {
    wrapper.vm.submitNext()
    await Vue.nextTick()
  })
})

describe('New Financing Statement Registration Buttons Step 3', () => {
  let wrapper: Wrapper<any>
  let wrapper2: any // eslint-disable-line no-unused-vars
  const currentStatementType: String = String(StatementTypes.FINANCING_STATEMENT)
  const currentStepName: String = String(RouteNames.ADD_COLLATERAL)

  beforeEach(async () => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    wrapper2 = shallowMount(AddCollateral, { localVue, store, router, vuetify })
    wrapper = createComponent(currentStatementType, router, currentStepName)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with step 3 values', async () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(true)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(true)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
    expect(wrapper.vm.statementType).toBe(StatementTypes.FINANCING_STATEMENT)
    expect(wrapper.vm.stepName).toBe(RouteNames.ADD_COLLATERAL)
    expect(wrapper.vm.buttonConfig.showCancel).toBe(true)
    expect(wrapper.vm.buttonConfig.showSave).toBe(true)
    expect(wrapper.vm.buttonConfig.showSaveResume).toBe(true)
    expect(wrapper.vm.buttonConfig.showNext).toBe(true)
    expect(wrapper.vm.buttonConfig.showBack).toBe(true)
    expect(wrapper.vm.buttonConfig.backRouteName).toBe(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)
    expect(wrapper.vm.buttonConfig.nextRouteName).toBe(RouteNames.REVIEW_CONFIRM)
    expect(wrapper.vm.buttonConfig.nextText).toBe('Review and Confirm')
  })
  it('Step 3 cancel button event', async () => {
    wrapper.find(cancelBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Step 3 back button event', async () => {
    wrapper.find(backBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Step 3 next button event', async () => {
    wrapper.find(nextBtn).trigger('click')
    await Vue.nextTick()
  })

  it('Step 3 submitCancel', async () => {
    wrapper.vm.submitCancel()
    await Vue.nextTick()
  })
  it('Step 3 submitBack', async () => {
    wrapper.vm.submitBack()
    await Vue.nextTick()
  })
  it('Step 3 submitNext', async () => {
    wrapper.vm.submitNext()
    await Vue.nextTick()
  })
})

describe('New Financing Statement Registration Buttons Step 4', () => {
  let wrapper: Wrapper<any>
  let wrapper2: any // eslint-disable-line no-unused-vars
  const currentStatementType: String = String(StatementTypes.FINANCING_STATEMENT)
  const currentStepName: String = String(RouteNames.REVIEW_CONFIRM)

  beforeEach(async () => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    wrapper2 = shallowMount(ReviewConfirm, { localVue, store, router, vuetify })
    wrapper = createComponent(currentStatementType, router, currentStepName)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with step 4 values', async () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(true)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(true)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
    expect(wrapper.vm.statementType).toBe(StatementTypes.FINANCING_STATEMENT)
    expect(wrapper.vm.stepName).toBe(RouteNames.REVIEW_CONFIRM)
    expect(wrapper.vm.buttonConfig.showCancel).toBe(true)
    expect(wrapper.vm.buttonConfig.showSave).toBe(true)
    expect(wrapper.vm.buttonConfig.showSaveResume).toBe(true)
    expect(wrapper.vm.buttonConfig.showNext).toBe(true)
    expect(wrapper.vm.buttonConfig.showBack).toBe(true)
    expect(wrapper.vm.buttonConfig.backRouteName).toBe(RouteNames.ADD_COLLATERAL)
    expect(wrapper.vm.buttonConfig.nextRouteName).toBe(RouteNames.DASHBOARD)
    expect(wrapper.vm.buttonConfig.nextText).toBe('Register and Pay')
  })
  it('Step 4 cancel button event', async () => {
    wrapper.find(cancelBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Step 4 back button event', async () => {
    wrapper.find(backBtn).trigger('click')
    await Vue.nextTick()
  })
  it('Step 4 next button event', async () => {
    wrapper.find(nextBtn).trigger('click')
    await Vue.nextTick()
  })

  it('Step 4 submitCancel', async () => {
    wrapper.vm.submitCancel()
    await Vue.nextTick()
  })
  it('Step 4 submitBack', async () => {
    wrapper.vm.submitBack()
    await Vue.nextTick()
  })
  it('Step 4 submitNext', async () => {
    wrapper.vm.submitNext()
    await Vue.nextTick()
  })
})
