// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { ButtonsStacked } from '@/components/common'

// Other
import mockRouter from './MockRouter'
import { RouteNames } from '@/enums'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// selectors
const cancelBtn = '#btn-stacked-cancel'
const submitBtn = '#btn-stacked-submit'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResult> object with the given parameters.
 */
function createComponent (mockRoute: string, cancelBtn: string, submitBtn: string): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({ name: mockRoute })

  return mount(ButtonsStacked, {
    localVue,
    propsData: { setCancelBtn: cancelBtn, setSubmitBtn: submitBtn },
    store,
    router,
    vuetify
  })
}

describe('ButtonsStacked component tests', () => {
  let wrapper: any
  const { assign } = window.location
  const cancelBtnTxt = 'Test Cancel'
  const submitBtnTxt = 'Test Confirm and Complete'

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any
    wrapper = createComponent(RouteNames.REVIEW_DISCHARGE, cancelBtnTxt, submitBtnTxt)

  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders ButtonsStacked component with buttons / proper text', () => {
    expect(wrapper.findComponent(ButtonsStacked).exists()).toBe(true)
    const cancel = wrapper.findAll(cancelBtn)
    expect(cancel.length).toBe(1)
    expect(cancel.at(0).text()).toBe(cancelBtnTxt)
    const submit = wrapper.findAll(submitBtn)
    expect(submit.length).toBe(1)
    expect(submit.at(0).text()).toBe(submitBtnTxt)
  })

  it('routes back to dashboard on cancel', async () => {
    const cancel = wrapper.find(cancelBtn)
    cancel.trigger('click')
    await flushPromises()
    expect(wrapper.vm.$router.currentRoute.name).toBe(RouteNames.DASHBOARD)
  })
})
