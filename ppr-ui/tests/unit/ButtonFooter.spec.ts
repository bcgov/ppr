// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router' // eslint-disable-line no-unused-vars
import { mount, createLocalVue, shallowMount, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import sinon from 'sinon'

// Components
import { ButtonFooter } from '@/components/common'
import { StaffPaymentDialog } from '@/components/dialogs'
import { LengthTrust, AddSecuredPartiesAndDebtors, AddCollateral, ReviewConfirm } from '@/views/newRegistration'
import { getLastEvent } from './utils'

// Other
import mockRouter from './MockRouter'
import { RouteNames, StatementTypes } from '@/enums'
import { axios } from '@/utils/axios-ppr'
import { mockedModelAmendmdmentAdd } from './test-data'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()
// Events

// Input field selectors / buttons
const cancelBtn: string = '#reg-cancel-btn'
const saveBtn: string = '#reg-save-btn'
const saveResumeBtn: string = '#reg-save-resume-btn'
const backBtn: string = '#reg-back-btn'
const nextBtn: string = '#reg-next-btn'

const router = mockRouter.mock()
/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  currentStatementType: String,
  currentStepName: String
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)

  document.body.setAttribute('data-app', 'true')
  return mount((ButtonFooter as any), {
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
    wrapper2 = shallowMount((LengthTrust as any), { localVue, store, router, vuetify })
    wrapper = createComponent(currentStatementType, currentStepName)
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
    expect(wrapper.props().currentStepName).toBe(RouteNames.LENGTH_TRUST)
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
    expect(store.getStateModel.unsavedChanges).toBe(false)
    await wrapper.find(cancelBtn).trigger('click')
    expect(wrapper.vm.showCancelDialog).toBe(false)
  })
  it('Step 1 next button event', async () => {
    wrapper.find(nextBtn).trigger('click')
    await nextTick()
  })
  it('Step 1 submitCancel', async () => {
    wrapper.vm.cancel()
    await nextTick()
  })
  it('Step 1 submitNext', async () => {
    wrapper.vm.submitNext()
    await nextTick()
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
    wrapper2 = shallowMount((AddSecuredPartiesAndDebtors as any), { localVue, store, router, vuetify })
    wrapper = createComponent(currentStatementType, currentStepName)
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
    expect(wrapper.props().currentStepName).toBe(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)
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
    expect(store.getStateModel.unsavedChanges).toBe(false)
    await wrapper.find(cancelBtn).trigger('click')
    expect(wrapper.vm.showCancelDialog).toBe(false)
  })

  it('Step 2 back button event', async () => {
    wrapper.find(backBtn).trigger('click')
    await nextTick()
  })
  it('Step 2 next button event', async () => {
    wrapper.find(nextBtn).trigger('click')
    await nextTick()
  })

  it('Step 2 submitCancel', async () => {
    wrapper.vm.cancel()
    await nextTick()
  })
  it('Step 2 submitBack', async () => {
    wrapper.vm.submitBack()
    await nextTick()
  })
  it('Step 2 submitNext', async () => {
    wrapper.vm.submitNext()
    await nextTick()
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
    wrapper2 = shallowMount((AddCollateral as any), { localVue, store, router, vuetify })
    wrapper = createComponent(currentStatementType, currentStepName)
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
    expect(wrapper.props().currentStepName).toBe(RouteNames.ADD_COLLATERAL)
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
    expect(store.getStateModel.unsavedChanges).toBe(false)
    await wrapper.find(cancelBtn).trigger('click')
    expect(wrapper.vm.showCancelDialog).toBe(false)
  })
  it('Step 3 back button event', async () => {
    wrapper.find(backBtn).trigger('click')
    await nextTick()
  })
  it('Step 3 next button event', async () => {
    wrapper.find(nextBtn).trigger('click')
    await nextTick()
  })

  it('Step 3 submitCancel', async () => {
    wrapper.vm.cancel()
    await nextTick()
  })
  it('Step 3 submitBack', async () => {
    wrapper.vm.submitBack()
    await nextTick()
  })
  it('Step 3 submitNext', async () => {
    wrapper.vm.submitNext()
    await nextTick()
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
    wrapper2 = shallowMount((ReviewConfirm as any), { localVue, store, router, vuetify })
    wrapper = createComponent(currentStatementType, currentStepName)
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
    expect(wrapper.props().currentStepName).toBe(RouteNames.REVIEW_CONFIRM)
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
    expect(store.getStateModel.unsavedChanges).toBe(false)
    await wrapper.find(cancelBtn).trigger('click')
    expect(wrapper.vm.showCancelDialog).toBe(false)
  })
  it('Step 4 back button event', async () => {
    wrapper.find(backBtn).trigger('click')
    await nextTick()
  })
  it('Step 4 next button event', async () => {
    wrapper.find(nextBtn).trigger('click')
    await nextTick()
  })

  it('Step 4 submitCancel', async () => {
    wrapper.vm.cancel()
    await nextTick()
  })
  it('Step 4 submitBack', async () => {
    wrapper.vm.submitBack()
    await nextTick()
  })
  it('Step 4 submitNext', async () => {
    wrapper.vm.submitNext()
    await nextTick()
  })
})

describe('Step 4 for SBC staff', () => {
  let wrapper: Wrapper<any>
  let wrapper2: any // eslint-disable-line no-unused-vars
  const currentStatementType: String = String(StatementTypes.FINANCING_STATEMENT)
  const currentStepName: String = String(RouteNames.REVIEW_CONFIRM)

  beforeEach(async () => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    await store.setAuthRoles(['staff', 'ppr_staff'])
    wrapper2 = shallowMount((ReviewConfirm as any), { localVue, store, router, vuetify })
    wrapper = createComponent(currentStatementType, currentStepName)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with step 4 values', async () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.findComponent(StaffPaymentDialog).exists()).toBe(true)
  })

  it('doesnt show staff payment dialog on submit if not valid', async () => {
    wrapper.find(nextBtn).trigger('click')
    await nextTick()
    expect(wrapper.findComponent(StaffPaymentDialog).vm.$props.setDisplay).toBe(false)
    expect(getLastEvent(wrapper, 'registration-incomplete')).toMatchObject({
      message: 'Registration incomplete: one or more steps is invalid.', statusCode: 400
    })
  })

  it('Shows staff payment dialog on submit', async () => {
    store.getStateModel.registration.lengthTrust.valid = true
    store.getStateModel.registration.parties.valid = true
    store.getStateModel.registration.collateral.valid = true
    wrapper.vm.$props.certifyValid = true
    await nextTick()
    wrapper.find(nextBtn).trigger('click')
    await nextTick()

    expect(wrapper.findComponent(StaffPaymentDialog).vm.$props.setDisplay).toBe(true)
  })

  it('disables button for bcol', async () => {
    await store.setAuthRoles(['staff', 'helpdesk'])
    await nextTick()
    expect(wrapper.find(nextBtn).attributes('disabled')).toBe('disabled')
  })
})

describe('Button events', () => {
  let wrapper: Wrapper<any>
  let sandbox

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const post = sandbox.stub(axios, 'post')
    post.returns(new Promise(resolve => resolve({ data: null })))
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const currentStatementType: String = String(StatementTypes.FINANCING_STATEMENT)
    const currentStepName: String = String(RouteNames.REVIEW_CONFIRM)
    wrapper = createComponent(currentStatementType, currentStepName)
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
    sandbox.restore()
  })

  it('emits error', async () => {
    store.getStateModel.registration = mockedModelAmendmdmentAdd.registration
    store.getStateModel.registration.lengthTrust.valid = true
    store.getStateModel.registration.parties.valid = true
    store.getStateModel.registration.collateral.valid = true
    wrapper.vm.$props.certifyValid = true
    expect(getLastEvent(wrapper, 'error')).toBeNull()
    await wrapper.vm.submitNext()
    await flushPromises()
    expect(getLastEvent(wrapper, 'error')).not.toBeNull()
  })
})
