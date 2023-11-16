import { nextTick } from 'vue'
import { createComponent, getLastEvent, setupMockStaffUser } from './utils'
import { useStore } from '@/store/store'
import { RouteNames } from '@/enums'
import {
  MHRManufacturerButtonFooterConfig,
  MhrUserAccessButtonFooterConfig,
  RegistrationButtonFooterConfig
} from '@/resources/buttonFooterConfig'
import { ButtonFooter } from '@/components/common'
import { StaffPaymentDialog } from '@/components/dialogs'
import flushPromises from 'flush-promises'
import { mockedManufacturerAuthRoles, mockedModelAmendmdmentAdd } from './test-data'
import { ButtonConfigIF } from '@/interfaces'
import { MhrRegistrationType } from '@/resources'
import { Wrapper } from '@vue/test-utils'

const store = useStore()
// Input field selectors / buttons
const cancelBtn: string = '#reg-cancel-btn'
const saveBtn: string = '#reg-save-btn'
const saveResumeBtn: string = '#reg-save-resume-btn'
const backBtn: string = '#reg-back-btn'
const nextBtn: string = '#reg-next-btn'

describe('New Financing Statement Registration Buttons Step 1', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ButtonFooter, {
      currentStepName: RouteNames.LENGTH_TRUST,
      navConfig: RegistrationButtonFooterConfig
    }, RouteNames.LENGTH_TRUST)
  })

  it('renders with step 1 values', async () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(true)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(false)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
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
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ButtonFooter, {
      currentStepName: RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS,
      navConfig: RegistrationButtonFooterConfig
    }, RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)
  })

  it('renders with step 2 values', async () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(true)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(true)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
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
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ButtonFooter, {
      currentStepName: RouteNames.ADD_COLLATERAL,
      navConfig: RegistrationButtonFooterConfig
    }, RouteNames.ADD_COLLATERAL)
  })

  it('renders with step 3 values', async () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(true)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(true)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
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
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ButtonFooter, {
      currentStepName: RouteNames.REVIEW_CONFIRM,
      navConfig: RegistrationButtonFooterConfig
    }, RouteNames.REVIEW_CONFIRM)
  })

  it('renders with step 4 values', async () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(true)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(true)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
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
  let wrapper

  beforeEach(async () => {

    wrapper = await createComponent(ButtonFooter, {
      currentStepName: RouteNames.REVIEW_CONFIRM,
      navConfig: RegistrationButtonFooterConfig,
      certifyValid: true
    }, RouteNames.REVIEW_CONFIRM)
    await setupMockStaffUser()
    await flushPromises()

  })

  it('renders with step 4 values', async () => {
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.findComponent(StaffPaymentDialog).exists()).toBe(true)
  })

  it('doesnt show staff payment dialog on submit if not valid', async () => {
    wrapper.find(nextBtn).trigger('click')
    await nextTick()
    expect(wrapper.findComponent(StaffPaymentDialog).vm.$props.setDisplay).toBe(false)
    expect(getLastEvent(wrapper, 'registrationIncomplete')).toMatchObject({
      message: 'Registration incomplete: one or more steps is invalid.', statusCode: 400
    })
  })

  it('Shows staff payment dialog on submit', async () => {
    store.getStateModel.registration.lengthTrust.valid = true
    store.getStateModel.registration.parties.valid = true
    store.getStateModel.registration.collateral.valid = true
    await nextTick()
    wrapper.find(nextBtn).trigger('click')
    await nextTick()

    expect(wrapper.findComponent(StaffPaymentDialog).vm.$props.setDisplay).toBe(true)
  })

  it('disables button for bcol', async () => {
    await store.setAuthRoles(['staff', 'helpdesk'])
    await nextTick()
    expect(wrapper.vm.lastStepBcol).toBe(true)
    expect(wrapper.find(nextBtn).attributes().disabled).toBeDefined()
  })
})

describe('Button events', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ButtonFooter, {
      currentStepName: RouteNames.REVIEW_CONFIRM,
      navConfig: RegistrationButtonFooterConfig,
      certifyValid: false
    }, RouteNames.REVIEW_CONFIRM)
    await flushPromises()
  })

  it('emits registrationIncomplete', async () => {
    store.getStateModel.registration = mockedModelAmendmdmentAdd.registration
    store.getStateModel.registration.lengthTrust.valid = true
    store.getStateModel.registration.parties.valid = true
    store.getStateModel.registration.collateral.valid = true

    expect(getLastEvent(wrapper, 'registrationIncomplete')).toBeNull()
    await wrapper.vm.submitNext()
    await flushPromises()
    expect(getLastEvent(wrapper, 'registrationIncomplete')).not.toBeNull()
  })
})

describe('Mhr Manufacturer Registration step 1 - Your Home', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ButtonFooter, {
      currentStepName: RouteNames.YOUR_HOME,
      navConfig: MHRManufacturerButtonFooterConfig
    }, RouteNames.YOUR_HOME)
    await flushPromises()
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
  })
  afterAll(async () => {
    await store.setAuthRoles([])
    await store.setRegistrationType(null)
  })

  it('renders with correct footer configs', async () => {
    expect(wrapper.vm.currentStepName).toBe(RouteNames.YOUR_HOME)
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(false)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(true)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(true)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)

    const buttonConfig = wrapper.vm.buttonConfig as ButtonConfigIF
    expect(buttonConfig.nextRouteName).toBe(RouteNames.MHR_REVIEW_CONFIRM)
    expect(buttonConfig.nextText).toBe('Review and Confirm')
  })

  it('Step 1 buttons work properly', async () => {
    await wrapper.find(saveBtn).trigger('click')
    await nextTick()
    expect(wrapper.vm.currentStepName).toBe(RouteNames.YOUR_HOME)

    expect(store.getStateModel.unsavedChanges).toBe(false)
    await wrapper.find(cancelBtn).trigger('click')
    await nextTick()
    expect(wrapper.vm.showCancelDialog).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)

    await wrapper.find(saveResumeBtn).trigger('click')
    await nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)

    wrapper.find(nextBtn).trigger('click')
    await nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_REVIEW_CONFIRM)
  })
})

describe('Mhr Manufacturer Registration step 2 - Review and Confirm', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ButtonFooter, {
      currentStepName: RouteNames.MHR_REVIEW_CONFIRM,
      navConfig: MHRManufacturerButtonFooterConfig
    }, RouteNames.MHR_REVIEW_CONFIRM)
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
  })

  afterAll(async () => {
    await store.setAuthRoles([])
    await store.setRegistrationType(null)
  })

  it('renders with correct footer configs', async () => {
    expect(wrapper.vm.currentStepName).toBe(RouteNames.MHR_REVIEW_CONFIRM)
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(true)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(true)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(true)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)
    const buttonConfig = wrapper.vm.buttonConfig as ButtonConfigIF
    expect(buttonConfig.nextRouteName).toBe(RouteNames.DASHBOARD)
    expect(buttonConfig.backRouteName).toBe(RouteNames.YOUR_HOME)
    expect(buttonConfig.nextText).toBe('Register and Pay')
  })

  it('Step 2 buttons work properly', async () => {
    await wrapper.find(saveBtn).trigger('click')
    await nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.MHR_REVIEW_CONFIRM)

    expect(store.getStateModel.unsavedChanges).toBe(false)
    await wrapper.find(cancelBtn).trigger('click')
    await nextTick()
    expect(wrapper.vm.showCancelDialog).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)

    await wrapper.find(saveResumeBtn).trigger('click')
    await nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
})

describe('Mhr User Access', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ButtonFooter, {
      currentStepName: RouteNames.QS_ACCESS_TYPE,
      navConfig: MhrUserAccessButtonFooterConfig
    }, RouteNames.QS_ACCESS_TYPE)
    await store.setMhrSubProduct(null)

  })

  it('renders with correct footer configs', async () => {
    expect(wrapper.vm.currentStepName).toBe(RouteNames.QS_ACCESS_TYPE)
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.find(backBtn).exists()).toBe(false)
    expect(wrapper.find(nextBtn).exists()).toBe(true)
    expect(wrapper.find(saveBtn).exists()).toBe(false)
    expect(wrapper.find(saveResumeBtn).exists()).toBe(false)
    expect(wrapper.find(cancelBtn).exists()).toBe(true)

    const buttonConfig = wrapper.vm.buttonConfig as ButtonConfigIF
    expect(buttonConfig.nextRouteName).toBe(RouteNames.QS_ACCESS_INFORMATION)
    expect(buttonConfig.nextText).toBe('Complete Qualified Supplier Application')

    // Verify nav enabled by default
    expect(wrapper.vm.$props.disableNav).toBe(false)
  })
})
