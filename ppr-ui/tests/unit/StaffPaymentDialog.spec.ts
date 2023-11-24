import { createComponent, getLastEvent } from './utils'
import { useStore } from '@/store/store'
import { BaseDialog, StaffPaymentDialog } from '@/components/dialogs'
import { staffPaymentDialog } from '@/resources/dialogOptions'
import { StaffPayment } from '@/components/common'
import flushPromises from 'flush-promises'

const store = useStore()

// emitted events
const proceed = 'proceed'

// Input field selectors / buttons
const title = '.dialog-title'

describe('Payment component', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(StaffPaymentDialog, {
      setOptions: staffPaymentDialog,
      setDisplay: true,
      setShowCertifiedCheckbox: true
    })
    await flushPromises()
  })

  it('renders with staff payment component', () => {
    expect(wrapper.findComponent(StaffPaymentDialog).exists()).toBe(true)
    expect(wrapper.findComponent(StaffPayment).exists()).toBe(true)
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.findAll(title).length).toBe(1)
    expect(wrapper.find(title).text()).toBe('Staff Payment')
  })

  it('Emits the cancel action', async () => {
    wrapper.findComponent(BaseDialog).vm.$emit(proceed, false)
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toEqual(false)
  })

  it('Emits the submit action', async () => {
    wrapper.vm.valid = true

    wrapper.findComponent(BaseDialog).vm.$emit(proceed, true)
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toBe(true)
  })

  it('updates search certified when checkbox is selected', async () => {
    expect(store.getStateModel.search.searchCertified).toBe(false)
    wrapper.vm.certify = true
    wrapper.vm.valid = true
    wrapper.findComponent(BaseDialog).vm.$emit(proceed, true)
    await flushPromises()
    expect(store.getStateModel.search.searchCertified).toBe(true)
  })

  it('updates store payment info', async () => {
    wrapper.findComponent(StaffPayment).vm.$emit('update:staffPaymentData', {
      option: 1,
      routingSlipNumber: '999888777',
      bcolAccountNumber: '',
      datNumber: '',
      folioNumber: '',
      isPriority: false
    })
    await flushPromises()
    wrapper.findComponent(BaseDialog).vm.$emit(proceed, true)
    await flushPromises()
    expect(store.getStateModel.staffPayment.routingSlipNumber).toBe('999888777')
  })

  it('Clears the payment data on cancel', async () => {
    wrapper.findComponent(StaffPayment).vm.$emit('update:staffPaymentData', {
      option: 1,
      routingSlipNumber: '999888777',
      bcolAccountNumber: '',
      datNumber: '',
      folioNumber: '',
      isPriority: false
    })
    await flushPromises()
    wrapper.findComponent(BaseDialog).vm.$emit(proceed, false)
    await flushPromises()
    expect(getLastEvent(wrapper, proceed)).toEqual(false)
    expect(store.getStateModel.staffPayment.routingSlipNumber).toBe('')
  })
})
