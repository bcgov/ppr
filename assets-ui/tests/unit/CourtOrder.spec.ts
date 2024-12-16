import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import { CourtOrder } from '@/components/common'
import { createComponent, getLastEvent } from './utils'
import flushPromises from 'flush-promises'

const store = useStore()

describe('Court Order component', () => {
  let wrapper

  beforeEach(async () => {
    await store.setCourtOrderInformation(
      {
        courtName: 'ABC',
        courtRegistry: '123',
        orderDate: '2021-10-07',
        fileNumber: 'DEF',
        effectOfOrder: 'Good'
      })
    wrapper = await createComponent(CourtOrder)
  })

  it('renders the view with text boxes', () => {
    expect(wrapper.findComponent(CourtOrder).exists()).toBe(true)
    expect(wrapper.find('#txt-court-name').exists()).toBe(true)
    expect(wrapper.find('#txt-court-registry').exists()).toBe(true)
    expect(wrapper.find('#txt-court-file-number').exists()).toBe(true)
    expect(wrapper.find('#court-date-text-field').exists()).toBe(true)
    expect(wrapper.find('#effect-of-order').exists()).toBe(true)
  })

  it('renders the court order data from the store', async () => {
    await flushPromises()
    expect(wrapper.find('#txt-court-name').element.value).toBe('ABC')
    expect(wrapper.find('#txt-court-registry').element.value).toBe('123')
    expect(wrapper.find('#txt-court-file-number').element.value).toBe('DEF')
    expect(wrapper.find('#effect-of-order').element.value).toBe('Good')
  })

  it('sets the validity to true when filled in', async () => {
    wrapper.find('#txt-court-name').setValue('Test Court')
    wrapper.find('#txt-court-registry').setValue('Test Registry')
    wrapper.find('#txt-court-file-number').setValue('Test File Number')
    const datePicker = await wrapper.findComponent('.court-date-text-input')
    datePicker.setValue('2021-10-07')
    // wrapper.vm.$data.orderDate = 'October 7, 2021'
    wrapper.find('#effect-of-order').setValue('Test Effect')

    await flushPromises()
    expect(getLastEvent(wrapper, 'setCourtOrderValid')).toBe(true)
  })

  it('sets the individual properties to invalid lengths', async () => {
    let invalidLengthTxt = 'x'.repeat(257)
    wrapper.find('#txt-court-name').setValue(invalidLengthTxt)
    invalidLengthTxt = 'x'.repeat(65)
    wrapper.find('#txt-court-registry').setValue(invalidLengthTxt)
    invalidLengthTxt = 'x'.repeat(21)
    wrapper.find('#txt-court-file-number').setValue(invalidLengthTxt)
    const datePicker = await wrapper.findComponent('.court-date-text-input')
    datePicker.setValue('2021-10-07')
    invalidLengthTxt = 'x'.repeat(513)
    wrapper.find('#effect-of-order').setValue(invalidLengthTxt)
    await nextTick()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(4)
    expect(messages.at(0).text()).toBe('Maximum 256 characters')
    expect(messages.at(1).text()).toBe('Maximum 64 characters')
    expect(messages.at(2).text()).toBe('Maximum 20 characters')
    expect(messages.at(3).text()).toBe('Maximum 512 characters')
  })

  it('sets the validity to false for blank fields', async () => {
    wrapper.find('#txt-court-name').setValue('')
    await nextTick()
    await flushPromises()
    expect(getLastEvent(wrapper, 'setCourtOrderValid')).toBe(false)
  })
})

describe('Court Order summary component', () => {
  let wrapper

  beforeEach(async () => {
    await store.setCourtOrderInformation(
      {
        courtName: 'ABC',
        courtRegistry: '123',
        orderDate: '2021-10-07',
        fileNumber: 'DEF',
        effectOfOrder: 'Good'
      })
    wrapper = await createComponent(CourtOrder, { setSummary: true })
  })

  it('renders the view with text boxes', () => {
    expect(wrapper.findComponent(CourtOrder).exists()).toBe(true)
    expect(wrapper.find('#court-name-display').exists()).toBe(true)
    expect(wrapper.find('#txt-court-name').exists()).toBe(false)
    expect(wrapper.find('#court-registry-display').exists()).toBe(true)
    expect(wrapper.find('#txt-court-registry').exists()).toBe(false)
    expect(wrapper.find('#txt-court-file-number').exists()).toBe(false)
    expect(wrapper.find('#file-number-display').exists()).toBe(true)
    expect(wrapper.find('#court-date-text-field').exists()).toBe(false)
    expect(wrapper.find('#date-display').exists()).toBe(true)
    expect(wrapper.find('#effect-display').exists()).toBe(true)
    expect(wrapper.find('#effect-of-order').exists()).toBe(false)

    expect(wrapper.find('#court-name-display').text()).toContain('ABC')
    expect(wrapper.find('#court-registry-display').text()).toContain('123')
    expect(wrapper.find('#file-number-display').text()).toContain('DEF')
    expect(wrapper.find('#effect-display').text()).toContain('Good')
  })
})
