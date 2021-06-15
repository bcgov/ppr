// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import flushPromises from 'flush-promises'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { PartySearch } from '@/components/parties'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

const partyCodeSearch = '#txt-code'
const addPartyLink = '#add-party'
const addRegisteringPartyLink = '#add-registering-party'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(PartySearch, {
    localVue,
    propsData: { },
    store,
    vuetify
  })
}

describe('Secured Party search event tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(PartySearch).exists()).toBe(true)
    // text box is there
    expect(wrapper.find(partyCodeSearch).exists()).toBe(true)
    expect(wrapper.find(addPartyLink).exists()).toBe(true)
    expect(wrapper.find(addRegisteringPartyLink).exists()).toBe(true)
  })

  it('emits the add secured party event', async () => {
    
    await wrapper.find(addPartyLink).trigger('click')
    
    expect(wrapper.emitted().showSecuredPartyAdd).toBeTruthy()
    
  })

  it('emits the add registering party event', async () => {
    
    await wrapper.find(addRegisteringPartyLink).trigger('click')
    
    expect(wrapper.emitted().addRegisteringParty).toBeTruthy()
    
  })
})
