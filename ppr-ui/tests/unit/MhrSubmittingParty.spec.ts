import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { MhrSubmittingParty } from '@/components/mhrRegistration/SubmittingParty'

Vue.use(Vuetify)
const store = getVuexStore()
const vuetify = new Vuetify({})

/**
 * Creates and mounts a component, so that it can be tested.
 * @returns a Wrapper object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  return mount(MhrSubmittingParty, {
    localVue,
    store,
    vuetify
  })
}

// Error message class selector
const ERROR_MSG = '.error--text .v-messages__message'

describe('mhr submitting party', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', async () => {
    const submittingPartySection = wrapper.findComponent(MhrSubmittingParty)
    expect(submittingPartySection.exists()).toBe(true)

    submittingPartySection.find('#person-option').exists()
    submittingPartySection.find('#business-option').exists()
    submittingPartySection.find('#first-name').exists()
    submittingPartySection.find('#middle-name').exists()
    submittingPartySection.find('#last-name').exists()
    submittingPartySection.find('#business-name').exists()
    submittingPartySection.find('#submitting-party-email').exists()
    submittingPartySection.find('#submitting-party-phone').exists()
    submittingPartySection.find('#submitting-party-phone-ext').exists()
    submittingPartySection.find('#submitting-party-address').exists()
  })

  it("has the right validations for a person's name", async () => {
    const submittingPartySection = wrapper.findComponent(MhrSubmittingParty)
    expect(submittingPartySection.exists()).toBe(true)

    await submittingPartySection.find('#person-option').trigger('click')

    const firstName = submittingPartySection.find('#first-name')
    firstName.setValue('!?@#$%')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Invalid characters')
    await firstName.setValue(' abc ')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')
    await firstName.setValue('abc'.repeat(6))
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Maximum')
    await firstName.setValue('Gary')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).length).toBe(0)

    const middleName = submittingPartySection.find('#middle-name')
    middleName.setValue('!?@#$%')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Invalid characters')
    middleName.setValue(' abc ')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')
    middleName.setValue('abc'.repeat(6))
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Maximum')
    middleName.setValue('fatboy')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).length).toBe(0)

    const lastName = submittingPartySection.find('#last-name')
    lastName.setValue('!?@#$%')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Invalid characters')
    lastName.setValue(' abc ')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')
    lastName.setValue('abcde'.repeat(6))
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Maximum')
    lastName.setValue('fatboy')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).length).toBe(0)
  })

  it('has the right validations for business and other info', async () => {
    const submittingPartySection = wrapper.findComponent(MhrSubmittingParty)
    expect(submittingPartySection.exists()).toBe(true)

    await submittingPartySection.find('#business-option').trigger('click')
    await Vue.nextTick()

    const businessName = submittingPartySection.find('#business-name')
    businessName.setValue(' abc ')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')
    businessName.setValue('garyblabla123'.repeat(7))
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Maximum')
    businessName.setValue('gary fatboy')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).length).toBe(0)

    const email = submittingPartySection.find('#submitting-party-email')
    email.setValue(' abc ')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')
    await email.setValue('garyfatboy@gmail.com')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).length).toBe(0)

    const phoneNum = submittingPartySection.find('#submitting-party-phone')
    phoneNum.setValue('abc')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Minimum 10 characters')
    phoneNum.setValue('7781234567')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).length).toBe(0)

    const phoneExt = submittingPartySection.find('#submitting-party-phone')
    phoneExt.setValue('abc')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).at(0).text()).toContain('Minimum 10 characters')
    phoneExt.setValue('123 456 7890')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(submittingPartySection.findAll(ERROR_MSG).length).toBe(0)
  })
})
