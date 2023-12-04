import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'
import { ErrorContact } from '@/components/common'
import { DialogContent } from '@/components/dialogs/common'
import { createComponent } from './utils'
import { nextTick } from 'vue'

// Input field selectors / buttons
const text = '.dialog-text'

describe('Dialog Content tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(DialogContent)
    await flushPromises()
  })

  it('renders the component with empty props', async () => {
    expect(wrapper.findComponent(DialogContent).exists()).toBe(true)
    expect(wrapper.vm.$props.setBaseText).toBe('')
    expect(wrapper.vm.$props.setExtraText).toEqual([])
    expect(wrapper.vm.$props.setHasContactInfo).toBe(false)
    expect(wrapper.findAll(text).length).toBe(0)
    expect(wrapper.findComponent(ErrorContact).exists()).toBe(false)
  })

  it('displays text when given', async () => {
    const newBaseText = 'test base text'
    wrapper = await createComponent(DialogContent, { setBaseText: newBaseText })

    expect(wrapper.vm.$props.setBaseText).toBe(newBaseText)
    expect(wrapper.findAll(text).length).toBe(1)
    expect(wrapper.findAll(text).at(0).text()).toContain(newBaseText)
  })

  it('Displays extra text when set', async () => {
    const extra1 = 'extra text 1'
    const extra2 = 'extra text 2'
    const extra3 = 'extra text 3'
    const newExtraText = [extra1, extra2, extra3]
    wrapper = await createComponent(DialogContent, { setExtraText: newExtraText })
    await nextTick()

    expect(wrapper.vm.$props.setExtraText).toStrictEqual(newExtraText)
    expect(wrapper.findAll(text).length).toBe(newExtraText.length)
    for (let i = 0; i < newExtraText.length; i++) {
      expect(wrapper.findAll(text).at(i).text()).toContain(newExtraText[i])
    }
  })

  it('Displays contact info when given', async () => {
    wrapper = await createComponent(DialogContent, { setHasContactInfo: true })
    await nextTick()

    expect(wrapper.findComponent(ErrorContact).exists()).toBe(true)
  })
})
