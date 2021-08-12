// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import flushPromises from 'flush-promises'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { axios as pprAxios } from '@/utils/axios-ppr'
import sinon from 'sinon'
import { getLastEvent } from './utils'

// Components
import { PartySearch } from '@/components/parties'

// Other
import { SearchPartyIF } from '@/interfaces'
import { mockedPartyCodeSearchResults } from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

const partyCodeSearch = '#txt-code'
const addPartyLink = '#add-party'
const addRegisteringPartyLink = '#add-registering-party'
const partyCodeAutoComplete = '#party-search-auto-complete'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(PartySearch, {
    localVue,
    propsData: {},
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

describe('Secured Party search autocomplete tests', () => {
  let wrapper: Wrapper<any>
  const pprResp: SearchPartyIF[] = mockedPartyCodeSearchResults
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  let sandbox

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    // GET autocomplete results
    const get = sandbox.stub(pprAxios, 'get')
    get.returns(
      new Promise(resolve =>
        resolve({
          data: pprResp
        })
      )
    )
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('shows the auto complete drop down when searching for a party', async () => {
    await wrapper.find(partyCodeSearch).setValue('TONY')
    await flushPromises()
    expect(wrapper.vm.$data.autoCompleteIsActive).toBe(true)
    expect(wrapper.vm.$data.autoCompleteResults.length).toBe(3)
    const autoCompleteItems = wrapper.findAll('.v-list-item__subtitle')
    expect(wrapper.find(partyCodeAutoComplete).exists()).toBe(true)
    expect(autoCompleteItems.length).toBeGreaterThan(1)
  })

  it('adds the party aafter a name in the list is clicked', async () => {
    await wrapper.find(partyCodeSearch).setValue('TONY')
    await flushPromises()
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
