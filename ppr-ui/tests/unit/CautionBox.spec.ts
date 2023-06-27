import { CautionBox } from '@/components/common'
import { createComponent } from './utils'

describe('Caution box component tests', () => {
  let wrapper: any

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders caution box component with given text', () => {
    const testMsg = 'this is very important'
    const importantText = 'Important'
    wrapper = createComponent(CautionBox, { setMsg: testMsg, setImportantWord: importantText })
    const cautionBoxTxt = wrapper.findAll('.caution-box')
    expect(cautionBoxTxt.length).toBe(1)
    expect(cautionBoxTxt.at(0).text()).toContain(testMsg)
    expect(cautionBoxTxt.at(0).text()).toContain(importantText)
  })

  it('renders caution box component with changed bold text', () => {
    const testMsg = 'this is very important'
    const importantText = 'Caution'
    wrapper = createComponent(CautionBox, { setMsg: testMsg, setImportantWord: importantText })
    const cautionBoxTxt = wrapper.findAll('.caution-box')
    expect(cautionBoxTxt.length).toBe(1)
    expect(cautionBoxTxt.at(0).text()).toContain(testMsg)
    expect(cautionBoxTxt.at(0).text()).not.toContain('Important')
    expect(cautionBoxTxt.at(0).text()).toContain(importantText)
  })
})
