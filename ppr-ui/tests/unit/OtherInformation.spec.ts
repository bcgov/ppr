import { createComponent, getTestId } from './utils'
import { OtherInformation } from '@/components/mhrRegistration'

describe('Other Information component', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(OtherInformation)
  })

  it('renders the component', async () => {
    expect(wrapper.findComponent(OtherInformation).exists()).toBe(true)
  })

  it('show error message for Other Information input', async () => {
    wrapper.find(getTestId('otherRemarks')).exists()
    await wrapper.find(getTestId('otherRemarks')).find('textarea').setValue('x'.repeat(150))

    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 140 characters')
  })
})
