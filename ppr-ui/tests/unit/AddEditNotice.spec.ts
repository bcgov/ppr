import { nextTick } from 'vue'
import { createComponent } from './utils'
import { AddEditNotice } from '@/components/registration'
import { ActionTypes, SaNoticeTypes } from '@/enums'
import { beforeEach } from 'vitest'

const mockNotice = {
  noticeId: 1,
  securitiesActNoticeType: 'PROCEEDINGS',
  effectiveDateTime: '2024-05-03',
  securitiesActOrders: [
    {
      courtOrder: false,
      fileNumber: '123123',
      orderDate: '2024-06-03',
      effectOfOrder: ''
    }
  ]
}

describe('AddEditNotice', () => {
  let wrapper
  beforeEach(async () => {
    // Mount the component
    wrapper = await createComponent(AddEditNotice, {
      isEditing: false,
      notice: null
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

describe('AddEditNotice: Amendments', () => {
  let wrapper
  beforeEach(async () => {
    // Mount the component
    wrapper = await createComponent(AddEditNotice, {
      isEditing: true,
      isAmendment: true,
      notice: mockNotice
    })
    await nextTick()
  })

  it('renders with the baseline notice information', async () => {
    expect(wrapper.vm.securitiesActNoticeType).toStrictEqual(SaNoticeTypes.NOTICE_OF_PROCEEDINGS)
    expect(wrapper.vm.effectiveDateTime).toBe(mockNotice.effectiveDateTime)
  })

  it('amends and emits done when submit button is clicked and form is valid', async () => {
    // Simulate user interaction but verify the radios are disabled and values persist
    const lienRadio = await wrapper.find('#lien-option')
    lienRadio.setChecked()

    // Change Effective Date to trigger amendment
    wrapper.vm.effectiveDateTime = '2024-05-10'

    // Trigger the submit event
    await wrapper.find('#submit-add-edit-notice').trigger('click')

    // Wait for Vue to update the DOM
    await nextTick()

    // Check if the done event was emitted with the correct data
    expect(wrapper.emitted().done).toBeTruthy()
    expect(wrapper.emitted().done.length).toBe(1)
    expect(wrapper.emitted().done[0][0]).toEqual({
      noticeId: 1,
      securitiesActNoticeType: SaNoticeTypes.NOTICE_OF_PROCEEDINGS,
      effectiveDateTime: '2024-05-10',
      securitiesActOrders: mockNotice.securitiesActOrders,
      action: ActionTypes.EDITED
    })
  })
})
