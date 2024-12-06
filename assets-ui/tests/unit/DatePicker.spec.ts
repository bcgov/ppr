import { nextTick } from 'vue'
import { RangeDatePicker } from '@/components/common'
import { createComponent, getLastEvent } from './utils'
import flushPromises from 'flush-promises'

const dateSelectors = '.date-selection__picker'
const headers = '.date-selection__heading'
const submitButtons = '.date-selection-btn'

describe('Date Picker tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(RangeDatePicker, { defaultStartDate: null, defaultEndDate: null })
  })

  it('renders and displays the date picker', async () => {
    expect(wrapper.findComponent(RangeDatePicker).exists()).toBe(true)
    expect(wrapper.findAll(headers).length).toBe(2)
    expect(wrapper.findAll(headers).at(0).text()).toBe('Select Start Date:')
    expect(wrapper.findAll(headers).at(1).text()).toBe('Select End Date:')
    expect(wrapper.findAll(dateSelectors).length).toBe(2)
    expect(wrapper.findAll(submitButtons).length).toBe(2)
    expect(wrapper.findAll(submitButtons).at(0).text()).toBe('OK')
    expect(wrapper.findAll(submitButtons).at(1).text()).toBe('Cancel')
    expect(wrapper.vm.datePickerErr).toBe(false)
  })

  it('Validates and submits the date selections', async () => {
    // verify setup
    expect(wrapper.findAll(dateSelectors).length).toBe(2)
    expect(wrapper.findAll(submitButtons).length).toBe(2)
    expect(wrapper.findAll(submitButtons).at(0).text()).toBe('OK')
    expect(wrapper.findAll(submitButtons).at(1).text()).toBe('Cancel')
    expect(wrapper.vm.datePickerErr).toBe(false)
    // click okay + test validation
    wrapper.findAll(submitButtons).at(0).trigger('click')
    await flushPromises()
    expect(wrapper.vm.datePickerErr).toBe(true)
    expect(getLastEvent(wrapper, 'submit')).toBe(null)
    // click cancel + test validation reset / emit nulls
    wrapper.findAll(submitButtons).at(1).trigger('click')
    await flushPromises()
    expect(wrapper.vm.datePickerErr).toBe(false)
    expect(getLastEvent(wrapper, 'submit')).toEqual({ endDate: null, startDate: null })
    // set start date only + test validation
    const startDate = '2021-10-22'
    wrapper.vm.startDate = startDate
    wrapper.vm.endDate = null
    await nextTick()
    await nextTick()
    expect(wrapper.vm.startDate).toBe(startDate)
    // should still trigger validation err
    wrapper.findAll(submitButtons).at(0).trigger('click')
    await nextTick()
    await nextTick()
    expect(wrapper.vm.datePickerErr).toBe(true)
    // last event will be the same as before
    expect(getLastEvent(wrapper, 'submit')).toEqual({ endDate: null, startDate: null })
    // select end date and submit should emit values
    const endDate = '2021-10-23'
    wrapper.vm.endDate = endDate
    await nextTick()
    await nextTick()
    expect(wrapper.vm.endDate).toBe(endDate)
    wrapper.findAll(submitButtons).at(0).trigger('click')
    await nextTick()
    await nextTick()
    expect(wrapper.vm.datePickerErr).toBe(false)
    expect(getLastEvent(wrapper, 'submit')).toEqual({ startDate: startDate, endDate: endDate })
  })
})
