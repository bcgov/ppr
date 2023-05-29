// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import SearchBarList from '@/components/search/SearchBarList.vue'

// Other
import { MHRSearchTypes, SearchTypes } from '@/resources'
import {
  mockedDisableAllUserSettingsResponse
} from './test-data'
import { UISearchTypes } from '@/enums'
import { getLastEvent } from './utils'
import flushPromises from 'flush-promises'
import { defaultFlagSet } from '@/utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Input field selectors / buttons
const searchDropDown: string = '.search-bar-type-select'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((SearchBarList as any), {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('SearchBar component basic tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders SearchBar Component with basic elements', async () => {
    expect(wrapper.findComponent(SearchBarList).exists()).toBe(true)
    expect(wrapper.find(searchDropDown).exists()).toBe(true)
  })

  it('shows all of the options', async () => {
    defaultFlagSet['mhr-ui-enabled'] = true
    await store.setAuthRoles(['mhr', 'ppr'])
    await store.setUserProductSubscriptionsCodes(['PPR', 'MHR'])

    wrapper.vm.updateSelections()
    await flushPromises
    expect(wrapper.vm.displayItems.length).toBe(12)
  })

  it('shows only ppr options', async () => {
    await store.setAuthRoles(['ppr'])
    await store.setUserProductSubscriptionsCodes(['PPR'])

    wrapper.vm.updateSelections()
    await flushPromises
    expect(wrapper.vm.displayItems.length).toBe(6)
  })

  it('shows only mhr options', async () => {
    await store.setAuthRoles(['mhr'])
    await store.setUserProductSubscriptionsCodes(['MHR'])

    wrapper.vm.updateSelections()
    await flushPromises
    expect(wrapper.vm.displayItems.length).toBe(4)
  })

  it('sends selected event', async () => {
    wrapper.vm.selectSearchType(SearchTypes[1])
    expect(getLastEvent(wrapper, 'selected')).toBe(SearchTypes[1])
  })
})
