import { nextTick } from 'vue'
import { createComponent } from './utils'
import { AddEditNotice } from '@/components/registration'
import { SaNoticeTypes } from '@/enums'
import { beforeEach } from 'vitest'

describe('AddEditNotice', () => {
  let wrapper
  beforeEach(async () => {
    // Mount the component
    wrapper = await createComponent(AddEditNotice, {
      props: {
        isEditing: false,
        notice: null
      }
    })
  })
  it('emits done event with Lien when submit button is clicked and form is valid', async () => {
    // Simulate user interaction to set form values
    const lienRadio = await wrapper.find('#lien-option')
    lienRadio.setChecked()
    wrapper.vm.effectiveDateTime = '2024-05-10'

    // Trigger the submit event
    await wrapper.find('#submit-add-edit-notice').trigger('click')

    // Wait for Vue to update the DOM
    await nextTick()

    // Check if the done event was emitted with the correct data
    expect(wrapper.emitted().done).toBeTruthy()
    expect(wrapper.emitted().done.length).toBe(1)
    expect(wrapper.emitted().done[0][0]).toEqual({
      securitiesActNoticeType: SaNoticeTypes.NOTICE_OF_LIEN,
      effectiveDateTime: '2024-05-10',
      securitiesActOrders: []
    })
  })

  it('emits done event with Proceedings when submit button is clicked and form is valid', async () => {
    // Simulate user interaction to set form values
    const proceedingsRadio = await wrapper.find('#proceedings-option')
    proceedingsRadio.setChecked()
    wrapper.vm.effectiveDateTime = '2024-05-10'

    // Trigger the submit event
    await wrapper.find('#submit-add-edit-notice').trigger('click')

    // Wait for Vue to update the DOM
    await nextTick()

    // Check if the done event was emitted with the correct data
    expect(wrapper.emitted().done).toBeTruthy()
    expect(wrapper.emitted().done.length).toBe(1)
    expect(wrapper.emitted().done[0][0]).toEqual({
      securitiesActNoticeType: SaNoticeTypes.NOTICE_OF_PROCEEDINGS,
      effectiveDateTime: '2024-05-10',
      securitiesActOrders: []
    })
  })

  it('emits done event without a set date when submit button is clicked and form is valid', async () => {
    // Simulate user interaction to set form values
    const proceedingsRadio = await wrapper.find('#proceedings-option')
    proceedingsRadio.setChecked()

    // Trigger the submit event
    await wrapper.find('#submit-add-edit-notice').trigger('click')

    // Wait for Vue to update the DOM
    await nextTick()

    // Check if the done event was emitted with the correct data
    expect(wrapper.emitted().done).toBeTruthy()
    expect(wrapper.emitted().done.length).toBe(1)
    expect(wrapper.emitted().done[0][0]).toEqual({
      securitiesActNoticeType: SaNoticeTypes.NOTICE_OF_PROCEEDINGS,
      effectiveDateTime: '',
      securitiesActOrders: []
    })
  })

  it('does not emit event when form is invalid', async () => {
    // Trigger the submit event
    await wrapper.find('#submit-add-edit-notice').trigger('click')

    // Wait for Vue to update the DOM
    await nextTick()

    // Check if the done event was emitted
    expect(wrapper.emitted().done).toBeFalsy()
  })
})
