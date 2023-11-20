import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import { createComponent } from './utils'
import { mockedSelectSecurityAgreement } from './test-data'
import flushPromises from 'flush-promises'
import { EditCollateral } from '@/components/collateral'

const store = useStore()

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn-collateral'

describe('Collateral validation tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement)
    wrapper = await createComponent(EditCollateral, { activeIndex: -1, invalidSection: false })
    await nextTick()
  })

  it('validates blank inputs', async () => {
    // no input added
    wrapper.find('#txt-serial').setValue('')
    wrapper.find('#txt-make').setValue('')
    wrapper.find('#txt-model').setValue('')
    wrapper.find('#txt-years').setValue('')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(4)
    expect(messages.at(0).text()).toBe('Type is required')
    expect(messages.at(2).text()).toBe('Enter the vehicle make')
    expect(messages.at(3).text()).toBe('Enter the vehicle model')
  })

  it('validates invalid year', async () => {
    const selectField = await wrapper.findComponent('.vehicle-type-select')
    selectField.setValue({ value: 'MV', title: 'Motor Vehicle' })
    wrapper.find('#txt-serial').setValue('293847298374')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(3000)
    // no input added
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a valid year')
  })

  it('validates serial number for vehicle', async () => {
    const selectField = await wrapper.findComponent('.vehicle-type-select')
    selectField.setValue({ value: 'MV', title: 'Motor Vehicle' })
    const test = await wrapper.findComponent('.serial-number')
    test.setValue('234627834628736428734634234872364')

    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue('2012')
    await nextTick()

    // no input added
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe('Maximum 25 characters')
  })

  it('validates number is correct for manufactured home', async () => {
    wrapper.vm.currentVehicle.type = 'MH'
    await nextTick()

    const manInput = await wrapper.findComponent('.mh-num-input')
    manInput.setValue('444555')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(2012)
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    // messages length is one when correct (because of the YYYY hint for year)
    expect(messages.length).toBe(1)
  })

  it('validates numbers only for manufactured home', async () => {
    wrapper.vm.currentVehicle.type = 'MH'
    await nextTick()

    wrapper.find('#txt-man').setValue('123$a')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue(2012)
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe(
      'Manufactured Home Registration Number must contain 6 digits'
    )
  })

  it('validates serial number max length for manufactured home', async () => {
    wrapper.vm.currentVehicle.type = 'MH'
    await nextTick()

    wrapper.find('#txt-man').setValue('123456')
    wrapper.find('#txt-serial').setValue('123456789012345678901234567890')
    wrapper.find('#txt-make').setValue('Honda')
    wrapper.find('#txt-model').setValue('Civic')
    wrapper.find('#txt-years').setValue('2012')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe(
      'Maximum 25 characters (for longer Serial Numbers include only the last 25 characters)'
    )
  })

  it('validates max lengths', async () => {
    const selectField = await wrapper.findComponent('.vehicle-type-select')
    selectField.setValue({ value: 'MV', title: 'Motor Vehicle' })
    await nextTick()
    wrapper.find('#txt-serial').setValue('ABC123')
    wrapper.find('#txt-make').setValue(
      'This is a very long make for a car or any vehicle for that matter but is it too long'
    )
    wrapper.find('#txt-model').setValue(
      'This is a very long model for a car or any vehicle for that matter but is it too long'
    )
    wrapper.find('#txt-years').setValue(2016)
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(3)
    expect(messages.at(1).text()).toBe('Maximum 60 characters')
    expect(messages.at(2).text()).toBe('Maximum 60 characters')
  })
})
