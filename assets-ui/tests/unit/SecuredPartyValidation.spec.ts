import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import { createComponent } from './utils'
import { EditParty } from '@/components/parties/party'
import flushPromises from 'flush-promises'
import { SecuredPartyTypes } from '@/enums'
const store = useStore()

// Events

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn-party'
const ERROR_MSG = '.v-messages__message'

describe('Secured Party validation tests - business', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(EditParty, { activeIndex: -1, invalidSection: false })
  })

  it('validates blank inputs', async () => {
    wrapper.vm.partyType = SecuredPartyTypes.BUSINESS
    await nextTick()

    // no input added
    const partyNameField = await wrapper.find('#txt-name-party')
    partyNameField.setValue('')

    const doneButton = await wrapper.find(doneButtonSelector)
    doneButton.trigger('click')
    await flushPromises()
    await nextTick()
    const messages = wrapper.findAll(ERROR_MSG)
    // With no country selected - errors: business name, country, address line 1
    expect(messages.length).toBe(3)
    expect(messages.at(0).text()).toBe('Please enter a business name')
  })
})

describe('Secured Party validation tests - individual', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(EditParty, { activeIndex: -1, invalidSection: false })
  })

  it('validates blank inputs', async () => {
    wrapper.vm.partyType = SecuredPartyTypes.INDIVIDUAL
    await nextTick()

    // no input added
    wrapper.find('#txt-first-party').setValue('')
    wrapper.find('#txt-last-party').setValue('')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()

    const messages = wrapper.findAll(ERROR_MSG)
    // With no country selected - errors: first name, last name, country, address line 1
    expect(messages.length).toBe(4)
    expect(messages.at(0).text()).toBe('Please enter a first name')
    expect(messages.at(1).text()).toBe('Please enter a last name')
  })

  it('validates the email', async () => {
    wrapper.vm.partyType = SecuredPartyTypes.INDIVIDUAL
    await nextTick()
    wrapper.find('#txt-first-party').setValue('first')
    wrapper.find('#txt-last-party').setValue('person')

    wrapper.find('#txt-email-party').setValue('person@')
    wrapper.find('#txt-email-party').trigger('blur')

    await flushPromises()
    const messages = wrapper.findAll(ERROR_MSG)
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe('Please enter a valid email address')
  })
})
