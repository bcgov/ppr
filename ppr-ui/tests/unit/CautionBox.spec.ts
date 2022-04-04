// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { CautionBox } from '@/components/common'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (setMsg: string): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount(CautionBox, {
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
