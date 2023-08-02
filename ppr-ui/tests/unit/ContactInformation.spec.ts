import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { Wrapper } from '@vue/test-utils'

import { ContactInformation } from '@/components/common'
import { createComponent } from './utils'
import { submittingPartyRegistrationContent } from '@/resources'
import { PartySearch } from '@/components/parties/party'
import { BaseAddress } from '@/composables/address'

Vue.use(Vuetify)

// Error message class selector
const ERROR_MSG = '.error--text .v-messages__message'

// Border-error class selector
const BORDER_ERROR = '.border-error-left'

const props = {
  contactInfo: null,
  content: submittingPartyRegistrationContent
}

describe('Contact Information', () => {
  let wrapper: Wrapper<any, Element>

  beforeEach(async () => {
    wrapper = await createComponent(ContactInformation, props)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', async () => {
    expect(wrapper.findComponent(PartySearch).exists()).toBe(true)
    expect(wrapper.findComponent(BaseAddress).exists()).toBe(true)
    expect(wrapper.find('#person-option').exists()).toBe(true)
    expect(wrapper.find('#business-option').exists()).toBe(true)
    expect(wrapper.find('#first-name').exists()).toBe(true)
    expect(wrapper.find('#middle-name').exists()).toBe(true)
    expect(wrapper.find('#last-name').exists()).toBe(true)
    expect(wrapper.find('#contact-info-email').exists()).toBe(true)
    expect(wrapper.find('#contact-info-phone').exists()).toBe(true)
    expect(wrapper.find('#contact-info-phone-ext').exists()).toBe(true)
    expect(wrapper.find('#contact-info-address').exists()).toBe(true)
  })

  it("has the right validations for a person's name", async () => {
    expect(wrapper.vm.contactInfoType).toBe('person')

    wrapper.find('#person-option').trigger('click')

    const firstName = wrapper.find('#first-name')
    firstName.setValue('!?@#$%')
    await nextTick()
    // expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Invalid characters')

    await firstName.setValue(' abc ')
    await nextTick()
    expect(wrapper.vm.contactInfoModel.personName.first).toBe(' abc ')
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')

    await firstName.setValue('abc'.repeat(6))
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Maximum')

    await firstName.setValue('Gary')
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)

    const middleName = wrapper.find('#middle-name')
    await middleName.setValue('!?@#$%')
    await nextTick()
    // expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Invalid characters')

    await middleName.setValue(' abc ')
    await nextTick()
    expect(wrapper.vm.contactInfoModel.personName.middle).toBe(' abc ')
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')

    await middleName.setValue('abc'.repeat(6))
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Maximum')

    await middleName.setValue('fatboy')
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)

    const lastName = wrapper.find('#last-name')
    await lastName.setValue('!?@#$%')
    await nextTick()
    // expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Invalid characters')

    await lastName.setValue(' abc ')
    await nextTick()
    expect(wrapper.vm.contactInfoModel.personName.last).toBe(' abc ')
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')

    await lastName.setValue('abcde'.repeat(6))
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Maximum')

    await lastName.setValue('fatboy')
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)
  })

  it('has the right validations for business and other info', async () => {
    await wrapper.find('#business-option').trigger('click')
    await nextTick()
    expect(wrapper.vm.contactInfoType).toBe('business')

    const businessName = wrapper.find('#business-name')
    await businessName.setValue(' abc ')
    await nextTick()
    expect(wrapper.vm.contactInfoModel.businessName).toBe(' abc ')
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')

    await businessName.setValue('garyblabla123'.repeat(14))
    await nextTick()
    expect(wrapper.findAll('.v-messages__message').length).toBe(2)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Maximum')

    await businessName.setValue('gary fatboy')
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)

    const email = wrapper.find('#contact-info-email')
    await email.setValue('garyfatboy@gmail.com')
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)

    await email.setValue('notAnEmail')
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)

    await email.setValue(' ')
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)

    await email.setValue('')
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)

    const phoneNum = wrapper.find('#contact-info-phone')
    await phoneNum.setValue('1234567890')
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)

    const phoneExt = wrapper.find('#contact-info-phone-ext')
    await phoneExt.setValue('12344')
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)
  })

  it('shows a left-border and trigger field validation when validate is passed', async () => {
    await wrapper.setProps({ validate: true })
    await nextTick()

    await wrapper.find('#business-option').trigger('click')
    await nextTick()
    expect(wrapper.vm.contactInfoType).toBe('business')
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toBe('Business name is required')
    expect(wrapper.find(BORDER_ERROR).exists()).toBe(true)

    await wrapper.find('#person-option').trigger('click')
    await nextTick()
    expect(wrapper.vm.contactInfoType).toBe('person')
    expect(wrapper.find(BORDER_ERROR).exists()).toBe(true)
    expect(wrapper.findAll(ERROR_MSG).length).toBe(2) // first name and last name required
  })
})
