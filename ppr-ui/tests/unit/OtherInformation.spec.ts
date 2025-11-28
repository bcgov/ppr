import { createComponent, getTestId } from './utils'
import { OtherInformation } from '@/components/mhrRegistration'
import { createPinia, setActivePinia } from 'pinia'
import flushPromises from 'flush-promises'
import { useStore } from '@/store/store'

describe('Other Information component', () => {
  let wrapper, store, pinia

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    wrapper = await createComponent(OtherInformation, null, null, null, [pinia])
    await flushPromises()
  })

  it('show error message for Other Information input', async () => {
    wrapper.find(getTestId('otherRemarks')).exists()
    await wrapper.find(getTestId('otherRemarks')).find('textarea').setValue('x'.repeat(150))

    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 140 characters')
  })
})
