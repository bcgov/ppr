import { PartySearch } from '@/components/parties/party'
import { createComponent } from './utils'
import { nextTick } from 'vue'
const partyCodeSearch = '#txt-code'
const addPartyLink = '#add-party'
const addRegisteringPartyCkbx = '#add-registering-party'

describe('Secured Party search event tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(PartySearch, {})
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(PartySearch).exists()).toBe(true)
    // text box is there
    expect(wrapper.find(partyCodeSearch).exists()).toBe(true)
    expect(wrapper.find(addPartyLink).exists()).toBe(true)
    expect(wrapper.find(addRegisteringPartyCkbx).exists()).toBe(true)
  })

  it('emits the add secured party event', async () => {
    await wrapper.find(addPartyLink).trigger('click')

    expect(wrapper.emitted().showSecuredPartyAdd).toBeTruthy()
  })

  it('emits the add registering party event', async () => {
    const chckBx = await wrapper.find(addRegisteringPartyCkbx)
    await chckBx.setValue(true)
    await nextTick()

    expect(wrapper.vm.registeringPartySelected).toBe(true)
    expect(wrapper.emitted().addRegisteringParty).toBeTruthy()
  })
})
