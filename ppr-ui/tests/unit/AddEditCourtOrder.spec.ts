import { nextTick } from 'vue'
import { createComponent } from './utils'
import { AddEditCourtOrder } from '@/components/registration'
import { beforeEach } from 'vitest'
import flushPromises from 'flush-promises'

describe('AddEditNotice', () => {
  let wrapper
  beforeEach(async () => {
    // Mount the component
    wrapper = await createComponent(AddEditCourtOrder, {
      props: {
        isEditing: false,
        courtOrderProp: null
      }
    })
  })

  it('renders the form and input fields', () => {
    expect(wrapper.findComponent(AddEditCourtOrder).exists()).toBe(true)
    expect(wrapper.find('#txt-court-name').exists()).toBe(true)
    expect(wrapper.find('#txt-court-registry').exists()).toBe(true)
    expect(wrapper.find('#txt-court-file-number').exists()).toBe(true)
    expect(wrapper.find('#court-date-text-field').exists()).toBe(true)
    expect(wrapper.find('#effect-of-order').exists()).toBe(true)
  })

  it('emits done event with data when submit button is clicked and form is valid', async () => {
    wrapper.find('#txt-court-name').setValue('Test Court')
    wrapper.find('#txt-court-registry').setValue('Test Registry')
    wrapper.find('#txt-court-file-number').setValue('Test File Number')
    wrapper.vm.courtOrderData.orderDate = '2021-10-07'
    wrapper.find('#effect-of-order').setValue('Test Effect')

    // Wait for Vue to update the DOM
    await nextTick()

    // Trigger the submit event
    await wrapper.find('#submit-add-edit-order').trigger('click')

    // Wait for Vue to update the DOM and flush validates
    await nextTick()
    await flushPromises()

    // Check if the done event was emitted with the correct data
    expect(wrapper.emitted().done).toBeTruthy()
    expect(wrapper.emitted().done.length).toBe(1)
    expect(wrapper.emitted().done[0][0]).toEqual({
      courtOrder: true,
      courtName: 'Test Court',
      courtRegistry: 'Test Registry',
      fileNumber: 'Test File Number',
      orderDate: '2021-10-07',
      effectOfOrder: 'Test Effect'
    })
  })

  it('emits cancel event when cancel button is clicked', async () => {
    await wrapper.find('#cancel-add-edit-order').trigger('click')

    // Wait for Vue to update the DOM and flush validates
    await nextTick()
    await flushPromises()

    // Check if the done event was emitted with the correct data
    expect(wrapper.emitted().cancel).toBeTruthy()
    expect(wrapper.emitted().cancel.length).toBe(1)
  })


  it('does not emit event when form is invalid', async () => {
    // Trigger the submit event
    await wrapper.find('#submit-add-edit-order').trigger('click')

    // Wait for Vue to update the DOM
    await nextTick()

    // Check if the done event was emitted
    expect(wrapper.emitted().done).toBeFalsy()
  })
})
