import { nextTick } from 'vue'
import { createComponent, getLastEvent } from './utils'
import { ChangeSecuredPartyDialog } from '@/components/dialogs'

const proceed: string = 'proceed'
const accept: string = '#accept-btn'
const cancel: string = '#cancel-btn'
const text: string = '.dialog-text'
const title: string = '.dialog-title'

describe('Confirmation Dialog', () => {
  let wrapper

  it('renders the component and executes the correct events', async () => {
    wrapper = await createComponent(ChangeSecuredPartyDialog, {
      display: true,
      securedPartyName: 'Test Company'
    })
    expect(wrapper.findComponent(ChangeSecuredPartyDialog).exists()).toBe(true)
    expect(wrapper.find(title).text()).toContain('Change Secured Party?')
    expect(wrapper.find(text).text()).toContain('Test Company')

    expect(wrapper.find(accept).exists()).toBe(true)
    wrapper.find(accept).trigger('click')
    await nextTick()
    expect(getLastEvent(wrapper, proceed)).toEqual(true)

    expect(wrapper.find(cancel).exists()).toBe(true)
    wrapper.find(cancel).trigger('click')
    await nextTick()
    expect(getLastEvent(wrapper, proceed)).toEqual(false)
  })
})
