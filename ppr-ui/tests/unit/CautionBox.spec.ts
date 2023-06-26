// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { CautionBox } from '@/components/common'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (setMsg: string, setImportantWord?: string): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount((CautionBox as any), {
    localVue,
    propsData: { setMsg: setMsg, setImportantWord: setImportantWord },
    store,
    vuetify
  })
}

describe('Caution box component tests', () => {
  let wrapper: any

  beforeEach(async () => {
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders caution box component with given text', () => {
    const testMsg = 'this is very important'
    const importantText = 'Important'
    wrapper = createComponent(testMsg)
    const cautionBoxTxt = wrapper.findAll('.caution-box')
    expect(cautionBoxTxt.length).toBe(1)
    expect(cautionBoxTxt.at(0).text()).toContain(testMsg)
    expect(cautionBoxTxt.at(0).text()).toContain(importantText)
  })

  it('renders caution box component with changed bold text', () => {
    const testMsg = 'this is very important'
    const importantText = 'Caution'
    wrapper = createComponent(testMsg, importantText)
    const cautionBoxTxt = wrapper.findAll('.caution-box')
    expect(cautionBoxTxt.length).toBe(1)
    expect(cautionBoxTxt.at(0).text()).toContain(testMsg)
    expect(cautionBoxTxt.at(0).text()).not.toContain('Important')
    expect(cautionBoxTxt.at(0).text()).toContain(importantText)
  })
})
