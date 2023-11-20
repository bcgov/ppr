// Libraries
import { nextTick } from 'vue'
import flushPromises from 'flush-promises'
import { mockedRegisteringParty1, mockedSecuredParties2 } from './test-data'
import { EditParty } from '@/components/parties/party'
import { useStore } from '@/store/store'
import { createComponent } from './utils'

const store = useStore()

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn-party'
const cancelButtonSelector: string = '#cancel-btn-party'
const removeButtonSelector: string = '#remove-btn-party'

const ERROR_MSG = '.error--text .v-messages__message'

describe('Secured Party add individual tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(EditParty, { activeIndex: -1, invalidSection: false })
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditParty).exists()).toBe(true)
    // radio button value is blank
    expect(wrapper.vm.partyType).toBe(null)
  })

  it('shows buttons on the form and remove button is disabled', async () => {
    expect(wrapper.find(doneButtonSelector).exists()).toBe(true)
    expect(wrapper.find(cancelButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).attributes().disabled).toBeDefined()
  })

  it('adds a secured party to the store', async () => {
    // Mock radio select
    wrapper.vm.partyType = 'individual'
    await nextTick()
    wrapper.find('#txt-first-party').setValue('JOE')
    wrapper.find('#txt-last-party').setValue('SCHMOE')
    wrapper.find('#txt-email-party').setValue('joe@apples.com')
    // for address
    wrapper.vm.currentSecuredParty.address.street = 'street'
    wrapper.vm.currentSecuredParty.address.city = 'victoria'
    wrapper.vm.currentSecuredParty.address.region = 'BC'
    wrapper.vm.currentSecuredParty.address.country = 'CA'
    wrapper.vm.currentSecuredParty.address.postalCode = 'v8r1w3'
    await nextTick()
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()

    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(store.getAddSecuredPartiesAndDebtors.securedParties.length).toBe(1)
  })
})

describe('Secured Party edit individual tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredParties2
    })
    wrapper = await createComponent(EditParty, { activeIndex: 0, invalidSection: false })
  })

  it('renders secured party when editing', async () => {
    expect(wrapper.findComponent(EditParty).exists()).toBe(true)
    expect(wrapper.vm.currentSecuredParty.personName.first).toEqual('TEST')
    expect(wrapper.vm.currentSecuredParty.personName.last).toEqual('INDIVIDUAL PARTY')
    expect(wrapper.vm.currentSecuredParty.emailAddress).toEqual('test@person.com')
  })

  it('Emits reset event', async () => {
    wrapper.find(cancelButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.emitted().resetEvent).toBeTruthy()
    expect(wrapper.find('.border-error-left').exists()).toBe(false)
  })

  it('shows error bar', async () => {
    wrapper = await createComponent(EditParty, { activeIndex: 0, invalidSection: false, setShowErrorBar: true })
    await nextTick()
    expect(wrapper.find('.border-error-left').exists()).toBe(true)
  })
})

describe('Registering party test', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1
    })
    wrapper = await createComponent(EditParty, { activeIndex: -1, invalidSection: false, isRegisteringParty: true })
  })

  it('renders registering party when editing', async () => {
    expect(wrapper.findComponent(EditParty).exists()).toBe(true)
    await nextTick()
    expect(wrapper.find('.add-party-header').text()).toContain('Registering')
  })
})
