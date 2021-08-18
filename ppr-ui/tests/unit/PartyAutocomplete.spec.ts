// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import flushPromises from 'flush-promises'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'


// Components
import { PartyAutocomplete } from '@/components/parties'

// Other
import { SearchPartyIF } from '@/interfaces'
import { mockedPartyCodeSearchResults } from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

const partyCodeAutoComplete = '#party-search-auto-complete'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  autoCompleteItems: Array<SearchPartyIF>
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(PartyAutocomplete, {
    localVue,
    propsData: { autoCompleteItems },
    store,
    vuetify
  })
}

describe('Secured Party search autocomplete tests', () => {
  let wrapper: Wrapper<any>
  
  beforeEach(async () => {
    wrapper = createComponent(mockedPartyCodeSearchResults)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('shows the auto complete drop down when searching for a party', async () => {
    expect(wrapper.vm.$data.autoCompleteIsActive).toBe(true)
    expect(wrapper.vm.$data.autoCompleteResults.length).toBe(3)
    const autoCompleteItems = wrapper.findAll('.v-list-item__subtitle')
    expect(wrapper.find(partyCodeAutoComplete).exists()).toBe(true)
    expect(autoCompleteItems.length).toBeGreaterThan(1)
  })

  it('adds the party aafter a name in the list is clicked', async () => {
    const partySearchAddLinks = wrapper.findAll('.v-list-item__action')
    expect(partySearchAddLinks.length).toBe(3)
    const icon = partySearchAddLinks.at(0).find('.v-icon')
    icon.trigger('click')
    await flushPromises()
    expect(store.getters.getAddSecuredPartiesAndDebtors.securedParties.length).toBe(1)
    expect(
      store.getters.getAddSecuredPartiesAndDebtors.securedParties[0].businessName
    ).toBe('TONY SCOTT REVENUE ADMINISTRATION BRANCH')
  })
})
