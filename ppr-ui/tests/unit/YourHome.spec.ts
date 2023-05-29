// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import VueRouter from 'vue-router'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// local components
import { YourHome } from '@/views'
import {
  HomeCertification,
  HomeSections,
  ManufacturerMakeModel,
  RebuiltStatus,
  OtherInformation
} from '@/components/mhrRegistration'
import { MhrRegistrationType } from '@/resources'
import { defaultFlagSet } from '@/utils'
import mockRouter from './MockRouter'
import { RouteNames } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({
    name: RouteNames.YOUR_HOME
  })

  document.body.setAttribute('data-app', 'true')
  return mount(YourHome, {
    localVue,
    store,
    propsData: {
      appReady: true
    },
    vuetify,
    router
  })
}

describe('Your Home', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    // Staff with MHR enabled
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setRegistrationType(MhrRegistrationType)

    wrapper = createComponent()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays Your Home View', async () => {
    expect(wrapper.findComponent(YourHome).exists()).toBe(true)
  })

  it('renders and displays the correct headers and sub components', async () => {
    expect(wrapper.find('#mhr-make-model h2').text()).toBe('Manufacturer, Make, and Model')
    expect(wrapper.findComponent(ManufacturerMakeModel).exists()).toBe(true)
    expect(wrapper.find('#mhr-home-sections h2').text()).toBe('Home Sections')
    expect(wrapper.findComponent(HomeSections).exists()).toBe(true)
    expect(wrapper.find('#mhr-home-certification h2').text()).toBe('Home Certification')
    expect(wrapper.findComponent(HomeCertification).exists()).toBe(true)
    expect(wrapper.find('#mhr-rebuilt-status h2').text()).toBe('Rebuilt Status')
    expect(wrapper.findComponent(RebuiltStatus).exists()).toBe(true)
    expect(wrapper.find('#mhr-other-information h2').text()).toBe('Other Information')
    expect(wrapper.findComponent(OtherInformation).exists()).toBe(true)
  })
})
