import { nextTick } from 'vue'
import { RebuiltStatus } from '@/components/mhrRegistration'
import { createComponent } from './utils'

describe('Rebuilt Status component', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(RebuiltStatus)
  })

  it('renders the component', async () => {
    expect(wrapper.findComponent(RebuiltStatus).exists()).toBe(true)
  })

  it('show error message for text area input', async () => {
    wrapper.find('#rebuilt-status-text').exists()
    await wrapper.find('#rebuilt-status-text').setValue('x'.repeat(290))

    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 280 characters')
  })
})
