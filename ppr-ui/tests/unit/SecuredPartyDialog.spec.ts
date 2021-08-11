// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedPartyCodeSearchResponse,
  mockedSecuredParties1
} from './test-data'

// Components
import { SecuredPartyDialog } from '@/components/dialogs'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<Debtors> object with the given parameters.
 */
function createComponent (
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(SecuredPartyDialog, {
    localVue,
    propsData: {
      defaultDialog: true,
      defaultParty: mockedSecuredParties1[0],
      defaultResults: mockedPartyCodeSearchResponse
    },
    store,
    vuetify
  })
}

describe('Secured Party Dialog SA tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(SecuredPartyDialog).exists()).toBe(true)
    expect(wrapper.isVisible()).toBe(true)
    expect(wrapper.find('#dialog-cancel-button').exists()).toBe(true)
  })

  it('renders secured party search responses', async () => {
    expect(wrapper.findAll('.searchResponse').length).toBe(2)
    // get the first result name
    expect(wrapper.find('.searchResponse .businessName').text()).toBe(mockedPartyCodeSearchResponse[0].businessName)
  })

  it('displays the correct current secured party info', () => {
    expect(wrapper.find('.currentParty .businessName').text()).toBe(mockedSecuredParties1[0].businessName)
  })
})
