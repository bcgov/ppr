// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { Wrapper } from '@vue/test-utils'

// Components
import { PartySearch } from '@/components/parties/party'
import { createComponent } from './utils'

Vue.use(Vuetify)

// Events
const partyCodeSearch = '#txt-code'
const addPartyLink = '#add-party'
const addRegisteringPartyLink = '#add-registering-party'

describe('Secured Party search event tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = await createComponent(PartySearch, {})
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
