import { useStore } from '@/store/store'
import { mockedDisableAllUserSettingsResponse } from './test-data'
import { createComponent, getLastEvent } from './utils'
import { SearchBarList } from '@/components/search'
import flushPromises from 'flush-promises'
import { SearchTypes } from '@/resources'
import { nextTick } from 'vue'

const store = useStore()

// Input field selectors / buttons
const searchDropDown: string = '.search-bar-type-select'

describe('SearchBar component basic tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setUserInfo({
      firstname: 'test',
      lastname: 'tester',
      username: 'user',
      settings: mockedDisableAllUserSettingsResponse
    })
    wrapper = await createComponent(SearchBarList)
  })

  it('renders SearchBar Component with basic elements', async () => {
    expect(wrapper.findComponent(SearchBarList).exists()).toBe(true)
    expect(wrapper.find(searchDropDown).exists()).toBe(true)
  })

  it('shows all of the options', async () => {
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
