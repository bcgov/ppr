import { nextTick } from 'vue'
import { LargeSearchResultDialog, BaseDialog } from '@/components/dialogs'
import {
  largeSearchReportError
} from '@/resources/dialogOptions'
import { createComponent, getLastEvent } from './utils'

// emitted events
const proceed: string = 'proceed'

// Input field selectors / buttons
const accept: string = '#accept-btn'
const cancel: string = '#cancel-btn'
const text: string = '.dialog-text'
const title: string = '.dialog-title'

describe('Large Search Result Dialog', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(LargeSearchResultDialog, {
      setDisplay: true,
      setOptions: largeSearchReportError,
      setNumberRegistrations: 75
    })
    await nextTick()
  })

  it('renders the component with all options', async () => {
    const options = largeSearchReportError

    expect(wrapper.findComponent(LargeSearchResultDialog).exists()).toBe(true)
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.isVisible()).toBe(true)
    expect(wrapper.find(title).text()).toBe(options.title)
    // number of registrations
    expect(wrapper.find(text).text()).toContain('75 registrations')
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
