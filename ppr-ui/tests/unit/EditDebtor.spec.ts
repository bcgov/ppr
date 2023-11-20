import { nextTick } from 'vue'
import flushPromises from 'flush-promises'
import { mockedDebtors1, mockedDebtors2 } from './test-data'
import { EditDebtor } from '@/components/parties/debtor'
import { useStore } from '@/store/store'
import { createComponent } from './utils'

const doneButtonSelector: string = '#done-btn-debtor'
const cancelButtonSelector: string = '#cancel-btn-debtor'
const removeButtonSelector: string = '#remove-btn-debtor'

const store = useStore()

describe('Debtor add individual tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(EditDebtor, {
      activeIndex: -1,
      isBusiness: false,
      invalidSections: false
    })
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditDebtor).exists()).toBe(true)
    expect(wrapper.vm.currentDebtor.personName.first).toBe('')
  })

  it('shows buttons on the form and remove button is disabled', async () => {
    expect(wrapper.find(doneButtonSelector).exists()).toBe(true)
    expect(wrapper.find(cancelButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).attributes().disabled).toBeDefined()
  })

  it('adds a debtor to the store', async () => {
    wrapper.find('#txt-first-debtor').setValue('JOE')
    wrapper.find('#txt-last-debtor').setValue('SCHMOE')
    await wrapper.find('#txt-month').setValue(6)
    wrapper.vm.month = { value: 6, text: 'June' }
    await nextTick()
    wrapper.find('#txt-day').setValue('25')
    wrapper.find('#txt-year').setValue(1980)
    // for address
    wrapper.vm.currentDebtor.address.street = 'street'
    wrapper.vm.currentDebtor.address.city = 'victoria'
    wrapper.vm.currentDebtor.address.region = 'BC'
    wrapper.vm.currentDebtor.address.country = 'CA'
    wrapper.vm.currentDebtor.address.postalCode = 'v8r1w3'
    await nextTick()
    wrapper.find(doneButtonSelector).trigger('click')
    await nextTick()

    // no validation messages
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(1).text()).toBe('Street address, PO box, rural route, or general delivery address')

    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(store.getAddSecuredPartiesAndDebtors.debtors.length).toBe(1)
  })

  it('adds a debtor birthdate validation', async () => {
    wrapper.find('#txt-first-debtor').setValue('JOE')
    wrapper.find('#txt-last-debtor').setValue('SCHMOE')
    await wrapper.find('#txt-month').setValue(6)
    wrapper.vm.month = { value: 6, text: 'June' }
    await nextTick()
    wrapper.find('#txt-day').setValue('ab')
    wrapper.find('#txt-year').setValue('abcd')
    // for address
    wrapper.vm.currentDebtor.address.street = 'street'
    wrapper.vm.currentDebtor.address.city = 'victoria'
    wrapper.vm.currentDebtor.address.region = 'BC'
    wrapper.vm.currentDebtor.address.country = 'CA'
    wrapper.vm.currentDebtor.address.postalCode = 'v8r1w3'
    await nextTick()
    wrapper.find(doneButtonSelector).trigger('click')
    await nextTick()

    // Expect 2 validation messages
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(4)
    expect(messages.at(1).text()).toBe('Please enter a valid day')
    expect(messages.at(2).text()).toBe('Please enter a valid year')
  })
})

describe('Debtor add business tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(EditDebtor, {
      activeIndex: -1,
      isBusiness: true,
      invalidSections: false
    })
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditDebtor).exists()).toBe(true)
    expect(wrapper.vm.currentDebtor.businessName).toBe('')
  })

  it('adds a debtor to the store', async () => {
    wrapper.find('#txt-name-debtor').setValue('TONYS TOOLS')
    // for the autocomplete
    wrapper.vm.searchValue = 'TONYS TOOLS'
    // for address
    wrapper.vm.currentDebtor.address.street = 'street'
    wrapper.vm.currentDebtor.address.city = 'victoria'
    wrapper.vm.currentDebtor.address.region = 'BC'
    wrapper.vm.currentDebtor.address.country = 'CA'
    wrapper.vm.currentDebtor.address.postalCode = 'v8r1w3'
    await nextTick()
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()

    // no validation messages
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)

    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(store.getAddSecuredPartiesAndDebtors.debtors[1].businessName).toBe('TONYS TOOLS')
  })
})

describe('Debtor edit individual tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      debtors: mockedDebtors1
    })
    wrapper = await createComponent(EditDebtor, {
      activeIndex: 0,
      isBusiness: false,
      invalidSections: false
    })
    await flushPromises()
  })

  it('renders debtor when editing', async () => {
    expect(wrapper.findComponent(EditDebtor).exists()).toBe(true)
    expect(wrapper.vm.currentDebtor.personName.first).toEqual('TEST')
    expect(wrapper.vm.currentDebtor.personName.last).toEqual('INDIVIDUAL DEBTOR')
    expect(wrapper.vm.currentDebtor.birthDate).toEqual('1990-06-15T16:42:00+00:00')
  })

  it('Emits reset event', async () => {
    wrapper.find(cancelButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.emitted().resetEvent).toBeTruthy()
  })
})

describe('Debtor edit business tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      debtors: mockedDebtors2
    })
    wrapper = await createComponent(EditDebtor, {
      activeIndex: 0,
      isBusiness: true,
      invalidSections: false
    })
  })

  it('renders debtor when editing', async () => {
    expect(wrapper.findComponent(EditDebtor).exists()).toBe(true)
    expect(wrapper.vm.currentDebtor.businessName).toEqual('SOMEBODYS BUSINESS')
    expect(wrapper.find('.border-error-left').exists()).toBe(false)
  })

  it('shows error bar', async () => {
    wrapper = await createComponent(EditDebtor, {
      activeIndex: 0,
      isBusiness: true,
      invalidSections: false,
      setShowErrorBar: true
    })
    await nextTick()
    expect(wrapper.find('.border-error-left').exists()).toBe(true)
  })
})
