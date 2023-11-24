import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import { RegistrationConfirmation } from '@/components/dialogs'
import {
  dischargeConfirmationDialog,
  amendConfirmationDialog,
  renewConfirmationDialog
} from '@/resources/dialogOptions'
import { mockedDebtorNames } from './test-data'
import { createComponent, getLastEvent } from './utils'
import flushPromises from 'flush-promises'
import { vi } from 'vitest'

const store = useStore()

// Input field selectors / buttons
const accept: string = '#accept-btn'
const cancel: string = '#cancel-btn'
const title: string = '.dialog-title'
const dropDown: string = '#debtor-drop'

const dischargeOptions = dischargeConfirmationDialog
const amendOptions = amendConfirmationDialog
const renewOptions = renewConfirmationDialog

describe('Registration Confirmation Dialog', () => {
  let wrapper

  vi.mock('@/utils/ppr-api-helper', () => ({
    debtorNames: vi.fn(() =>
      Promise.resolve({ ...mockedDebtorNames }))
  }))

  beforeEach(async () => {
    wrapper = await createComponent(RegistrationConfirmation, {
      attach: '',
      display: true,
      options: dischargeOptions,
      registrationNumber: '123'
    })
    await nextTick()
  })

  it('renders the component and allows debtor name selection', async () => {
    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    expect(wrapper.isVisible()).toBe(true)
    expect(wrapper.find(title).text()).toBe(dischargeOptions.title)

    expect(wrapper.find(dropDown).exists()).toBe(true)
    expect(wrapper.find(accept).exists()).toBe(true)

    wrapper.vm.debtors = [ 'Forrest Gump' ]
    wrapper.vm.fullDebtorInfo = mockedDebtorNames
    await nextTick()

    const autocompleteControls = await wrapper.find('#debtor-drop')
    autocompleteControls.trigger('click')

    wrapper.vm.userInput = 'Forrest Gump'
    await nextTick()

    wrapper.find(accept).trigger('click')
    const acceptBtn = await wrapper.find(accept)
    await acceptBtn.trigger('click')
    await nextTick()

    expect(getLastEvent(wrapper, 'proceed')).toBe(true)

    expect(store.getConfirmDebtorName.businessName).toBe('Forrest Gump')
  })

  it('the cancel button works', async () => {
    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    expect(wrapper.isVisible()).toBe(true)

    wrapper.vm.userInput = 'Forrest Gump'
    await flushPromises()

    expect(wrapper.find(cancel).exists()).toBe(true)
    wrapper.find(cancel).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'proceed')).toBe(false)
    expect(wrapper.vm.userInput).toBe(null)
  })

  it('renders the amendment dialog', async () => {
    wrapper = await createComponent(RegistrationConfirmation, {
      attach: '',
      display: true,
      options: amendOptions,
      registrationNumber: '123'
    })
    await nextTick()

    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    expect(wrapper.isVisible()).toBe(true)
    expect(wrapper.find(title).text()).toContain(amendOptions.title)
  })

  it('renders the renewal dialog', async () => {
    wrapper = await createComponent(RegistrationConfirmation, {
      attach: '',
      display: true,
      options: renewOptions,
      registrationNumber: '123'
    })
    await nextTick()

    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    expect(wrapper.isVisible()).toBe(true)
    expect(wrapper.find(title).text()).toBe(renewOptions.title)
  })
})
