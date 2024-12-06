import {
  mockedDefaultUserSettingsResponse,
  mockedDisablePayUserSettingsResponse
} from './test-data'
import { useStore } from '@/store/store'
import { createComponent, getLastEvent } from './utils'
import flushPromises from 'flush-promises'
import { paymentConfirmaionDialog, selectionConfirmaionDialog } from '@/resources/dialogOptions'
import { BaseDialog, ConfirmationDialog } from '@/components/dialogs'
import { SettingOptions } from '@/enums'
import { DialogContent } from '@/components/dialogs/common'
import { nextTick } from 'vue'
import { vi } from 'vitest'

const store = useStore()

// emitted events
const proceed = 'proceed'

// Input field selectors / buttons
const checkbox = '.dialog-checkbox'

vi.mock('@/utils/ppr-api-helper', () => ({
  updateUserSettings: vi.fn(() =>
    Promise.resolve({ ...mockedDisablePayUserSettingsResponse }))
}))

describe('Confirmation Dialog', () => {
  let wrapper

  beforeEach(async () => {
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDefaultUserSettingsResponse
    })
  })

  it('renders the component with all error options', async () => {
    const confirmationOptions = [paymentConfirmaionDialog, selectionConfirmaionDialog]
    const settingOptions = [SettingOptions.PAYMENT_CONFIRMATION_DIALOG, SettingOptions.SELECT_CONFIRMATION_DIALOG]
    for (let i = 0; i < confirmationOptions.length; i++) {
      const options = confirmationOptions[i]
      const settingOption = settingOptions[i]
      wrapper = await createComponent(
        ConfirmationDialog, {
          setDisplay: true,
          setOptions: options,
          setSettingOption: settingOption
        })
      await flushPromises()

      expect(wrapper.findComponent(ConfirmationDialog).exists()).toBe(true)
      expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
      expect(wrapper.findComponent(DialogContent).exists()).toBe(true)
      expect(wrapper.isVisible()).toBe(true)
      expect(wrapper.findComponent(BaseDialog).text()).toContain(options.title)
      expect(wrapper.findComponent(DialogContent).text()).toContain(options.text)
      expect(wrapper.find(checkbox).exists()).toBe(true)

      wrapper.findComponent(BaseDialog).vm.$emit(proceed, true)
      await flushPromises()
      expect(getLastEvent(wrapper, proceed)).toEqual(true)

      wrapper.findComponent(BaseDialog).vm.$emit(proceed, false)
      await flushPromises()
      expect(getLastEvent(wrapper, proceed)).toEqual(false)
    }
  })

  it('updates user settings when checkbox is selected', async () => {
    wrapper = await createComponent(
      ConfirmationDialog, {
        setDisplay: true,
        setOptions: paymentConfirmaionDialog,
        setSettingOption: SettingOptions.PAYMENT_CONFIRMATION_DIALOG
      })
    await flushPromises()
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(true)
    expect(wrapper.vm.preventDialog).toBe(false)
    wrapper.vm.preventDialog = true
    await flushPromises()
    await nextTick()
    expect(wrapper.vm.updateFailed).toBe(false)
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
  })
})
