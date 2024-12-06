import { RegistrationOtherDialog } from '@/components/dialogs'
import { registrationOtherDialog } from '@/resources/dialogOptions'
import { createComponent, getLastEvent } from './utils'
import { useStore } from '@/store/store'
import flushPromises from 'flush-promises'

const store = useStore()

const proceed = 'proceed'
const dialogClose = '#close-btn'
const dialogCancel = '#cancel-btn'
const dialogSubmit = '#accept-btn'
const dialogTextField = '#dialog-text-field'

describe('Registration Other Dialog tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(RegistrationOtherDialog, {
      attach: '#app',
      display: true,
      options: registrationOtherDialog
    })
  })

  it('renders the dialog', async () => {
    expect(wrapper.findComponent(RegistrationOtherDialog).exists()).toBe(true)
    expect(wrapper.findAll('.v-dialog').length).toBe(1)
    expect(wrapper.find('.dialog-title').text()).toContain(registrationOtherDialog.title)
    expect(wrapper.find('.dialog-text').text()).toContain(registrationOtherDialog.text)
    expect(wrapper.find(dialogTextField).exists()).toBe(true)
    expect(wrapper.find(dialogSubmit).text()).toContain(registrationOtherDialog.acceptText)
    expect(wrapper.find(dialogCancel).text()).toContain(registrationOtherDialog.cancelText)
    expect(wrapper.find(dialogClose).exists()).toBe(true)
  })

  it('closes the dialog when pressing the close button', async () => {
    wrapper.find(dialogClose).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(false)
  })

  it('closes the dialog when pressing the cancel button', async () => {
    wrapper.find(dialogCancel).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(false)
  })

  it('validates for name of statute before submitting', async () => {
    expect(wrapper.findAll('.v-messages').length).toBe(1)
    expect(wrapper.findAll('.v-messages').at(0).text()).toBe('')
    wrapper.find(dialogSubmit).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBeNull()
    expect(wrapper.findAll('.v-messages').length).toBe(1)
    expect(wrapper.findAll('.v-messages').at(0).text()).toContain('required')
    // click modal submit
    wrapper.find(dialogTextField).setValue('test')
    wrapper.find(dialogSubmit).trigger('click')
    await flushPromises()
    // check emitted other + set other name desc
    expect(store.getStateModel.registration.registrationTypeOtherDesc).toBe('test')
    expect(getLastEvent(wrapper, proceed)).toBe(true)
  })
})
