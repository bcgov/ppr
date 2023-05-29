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
function createComponent (setMsg: string): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount((CautionBox as any), {
    localVue,
    propsData: { setMsg: setMsg },
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
    wrapper = createComponent(testMsg)
    expect(wrapper.vm.msg).toBe(testMsg)
    const cautionBoxTxt = wrapper.findAll('.caution-box')
    expect(cautionBoxTxt.length).toBe(1)
    expect(cautionBoxTxt.at(0).text()).toContain(testMsg)
  })
})
