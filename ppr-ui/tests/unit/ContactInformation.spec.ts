import { nextTick } from 'vue'
import { createComponent } from './utils'
import { submittingPartyRegistrationContent } from '@/resources'
import { ContactInformation } from '@/components/common'
import { PartySearch } from '@/components/parties/party'
import { BaseAddress } from '@/composables/address'
import { ContactTypes } from '@/enums'
import flushPromises from 'flush-promises'

// Error message class selector
const ERROR_MSG = '.v-messages__message'

// Border-error class selector
const BORDER_ERROR = '.border-error-left'

const props = {
  contactInfo: null,
  content: submittingPartyRegistrationContent,
  hidePartySearch: true
}

describe('Contact Information', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ContactInformation, props)
    await nextTick()
  })

  it('renders the component', async () => {
    wrapper = await createComponent(ContactInformation, { ...props, hidePartySearch: false })

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

  it('shows no errors when valid persons name', async () => {
    expect(wrapper.vm.contactInfoType).toBe('person')
    const firstName = await wrapper.find('#first-name')
    firstName.setValue('X')

    const middleName = await wrapper.find('#middle-name')
    middleName.setValue('X')

    const lastName = await wrapper.find('#last-name')
    lastName.setValue('X')


    const form = await wrapper.findComponent('#contact-info-form')
    await form.vm.validate()
    await flushPromises()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)
  })

  it('shows invalid spaces errors when invalid persons name', async () => {
    expect(wrapper.vm.contactInfoType).toBe('person')
    const firstName = await wrapper.find('#first-name')
    firstName.setValue('  X  ')

    const middleName = await wrapper.find('#middle-name')
    middleName.setValue(' X ')

    const lastName = await wrapper.find('#last-name')
    lastName.setValue(' X ')

    const form = await wrapper.findComponent('#contact-info-form')
    await form.vm.validate()
    await flushPromises()

    expect(wrapper.findAll(ERROR_MSG).length).toBe(3)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')
    expect(wrapper.findAll(ERROR_MSG).at(1).text()).toContain('Invalid spaces')
    expect(wrapper.findAll(ERROR_MSG).at(2).text()).toContain('Invalid spaces')
  })

  it('shows maximum characters errors when invalid persons name', async () => {
    expect(wrapper.vm.contactInfoType).toBe('person')
    const firstName = await wrapper.find('#first-name')
    firstName.setValue('xasdasdasd'.repeat(26))

    const middleName = await wrapper.find('#middle-name')
    middleName.setValue('xasdasdasd'.repeat(26))

    const lastName = await wrapper.find('#last-name')
    lastName.setValue('xasdasdasd'.repeat(36))

    const form = await wrapper.findComponent('#contact-info-form')
    await form.vm.validate()
    await flushPromises()
    await nextTick()

    expect(wrapper.findAll(ERROR_MSG).length).toBe(3)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Maximum 50')
    expect(wrapper.findAll(ERROR_MSG).at(1).text()).toContain('Maximum 50')
    expect(wrapper.findAll(ERROR_MSG).at(2).text()).toContain('Maximum 50')
  })

  it('has the right validations for business and other info', async () => {
    wrapper = await createComponent(ContactInformation, { ...props, contactInfo: { businessName: 'MockBus'} })
    await nextTick()
    expect(wrapper.vm.contactInfoType).toBe('business')

    const businessName = wrapper.find('#business-name')
    await businessName.setValue(' abc ')
    await flushPromises()
    expect(wrapper.vm.contactInfoModel.businessName).toBe(' abc ')
    expect(wrapper.findAll('.v-messages__message').length).toBe(1)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Invalid spaces')

    await businessName.setValue('garyblabla123'.repeat(14))
    await flushPromises()
    expect(wrapper.findAll('.v-messages__message').length).toBe(2)
    expect(wrapper.findAll(ERROR_MSG).at(1).text()).toContain('Maximum')

    await businessName.setValue('gary fatboy')
    await flushPromises()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(2)

    const email = wrapper.find('#contact-info-email')
    await email.setValue('garyfatboy@gmail.com')
    await flushPromises()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)

    await email.setValue('notAnEmail')
    await flushPromises()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)

    await email.setValue(' ')
    await flushPromises()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)

    await email.setValue('')
    await flushPromises()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)

    const phoneNum = wrapper.find('#contact-info-phone')
    await phoneNum.setValue('(123) 456-7890')
    await flushPromises()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)

    const phoneExt = wrapper.find('#contact-info-phone-ext')
    await phoneExt.setValue('12344')
    await flushPromises()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)
  })

  it('shows error border and triggers validation when prompted for businesses', async () => {
    wrapper = await createComponent(ContactInformation,
      { ...props, contactInfo: { businessName: 'xyz'}, validate: true }
    )
    await nextTick()

    // Used the props to set Business Name, now clear it to an invalid state
    const businessName = wrapper.find('#business-name')
    await businessName.setValue('')
    await flushPromises()

    // Validate form
    const form = await wrapper.findComponent('#contact-info-form')
    await form.vm.validate()
    await flushPromises()

    expect(wrapper.vm.contactInfoType).toBe(ContactTypes.BUSINESS)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toBe('Business name is required')
    expect(wrapper.find(BORDER_ERROR).exists()).toBe(true)
  })

  it('shows error border and triggers validation when prompted for persons', async () => {
    wrapper = await createComponent(ContactInformation, { ...props, validate: true })
    await nextTick()

    // Validate form
    const form = await wrapper.findComponent('#contact-info-form')
    await form.vm.validate()
    await flushPromises()

    expect(wrapper.vm.contactInfoType).toBe(ContactTypes.PERSON)
    expect(wrapper.find(BORDER_ERROR).exists()).toBe(true)
    // With no country selected - errors: first name, last name, country, address line 1
    expect(wrapper.findAll(ERROR_MSG).length).toBe(7)
  })
})
