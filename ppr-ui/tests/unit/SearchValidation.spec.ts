// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { SearchBar } from '@/components/search'

// Other
import { SearchTypes } from '@/resources'
import { SearchTypeIF } from '@/interfaces'
import { getLastEvent } from './utils'

// Vue.use(CompositionApi)
Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const searchError: string = 'search-error'
const searchData: string = 'search-data'

// Input field selectors / buttons
const searchButtonSelector: string = '.search-bar-btn'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  searchTypes: Array<SearchTypeIF>
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(SearchBar, {
    localVue,
    propsData: { searchTypes },
    store,
    vuetify
  })
}

describe('SearchBar base validation', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('prevents searching and gives validation when category is not selected', async () => {
    expect(wrapper.vm.$data.selectedSearchType).toBeUndefined()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchTypes).toStrictEqual(SearchTypes)
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
    expect(wrapper.vm.$data.validations.category?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Please select a category')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })
})

describe('Serial number validation', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[0]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchValue).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a serial number to search')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching and gives validation when the search is over 25 characters', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[0]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = '12345678901234567890123456'
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchValue).toBe('12345678901234567890123456')
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 25 characters')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[0]
    // hint
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Serial numbers normally contain')
    // popup
    wrapper.vm.$data.searchValue = 'F10'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.popUp).toBeDefined()
    await Vue.nextTick()
    const popUpMessages = wrapper.findAll('.v-tooltip__content')
    expect(popUpMessages.length).toBe(1)
    expect(popUpMessages.at(0).text()).toContain('This may not be a valid serial')
    // special chars
    wrapper.vm.$data.searchValue = 'F10@'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.message).toBeDefined()
    await Vue.nextTick()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toContain("don't normally contain special characters")
    // maximum 25 characters
    wrapper.vm.$data.searchValue = '12345678901234567890123456'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.message).toBeDefined()
    await Vue.nextTick()
    const errorMessages = wrapper.findAll('.v-messages__message')
    expect(errorMessages.length).toBe(1)
    expect(errorMessages.at(0).text()).toBe('Maximum 25 characters')
  })
})

describe('Individual debtor validation', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('prevents searching and gives validation when first name or last name is empty', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[1]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchValue).toBeNull()
    expect(wrapper.vm.$data.searchValueFirst).toBeUndefined()
    expect(wrapper.vm.$data.searchValueSecond).toBeUndefined()
    expect(wrapper.vm.$data.searchValueLast).toBeUndefined()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.messageFirst).toBeDefined()
    expect(wrapper.vm.$data.validations.searchValue?.messageSecond).toBeUndefined()
    expect(wrapper.vm.$data.validations.searchValue?.messageLast).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe('Enter a first name')
    expect(messages.at(1).text()).toBe('Enter a last name')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching and gives validation when first name is above max characters', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[1]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    wrapper.vm.$data.searchValueFirst = '1234567890123456'
    wrapper.vm.$data.searchValueLast = 'last'
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.messageFirst).toBeDefined()
    expect(wrapper.vm.$data.validations.searchValue?.messageSecond).toBeUndefined()
    expect(wrapper.vm.$data.validations.searchValue?.messageLast).toBeUndefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 15 characters')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching and gives validation when last name is above max characters', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[1]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    wrapper.vm.$data.searchValueFirst = 'first'
    wrapper.vm.$data.searchValueLast = '12345678901234567890123456'
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.messageFirst).toBeUndefined()
    expect(wrapper.vm.$data.validations.searchValue?.messageSecond).toBeUndefined()
    expect(wrapper.vm.$data.validations.searchValue?.messageLast).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 25 characters')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[0]
    // hint
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Serial numbers normally contain')
    // popup
    wrapper.vm.$data.searchValue = 'F10'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.popUp).toBeDefined()
    await Vue.nextTick()
    const popUpMessages = wrapper.findAll('.v-tooltip__content')
    expect(popUpMessages.length).toBe(1)
    expect(popUpMessages.at(0).text()).toContain('This may not be a valid serial')
    // special chars
    wrapper.vm.$data.searchValue = 'F10@'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.message).toBeDefined()
    await Vue.nextTick()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toContain("don't normally contain special characters")
  })
})

describe('Business debtor validation', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[2]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchValue).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a business debtor name to search')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is less than minimum characters', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[2]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 'F'
    await Vue.nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Must contain more than 1 character')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is more than maximum characters', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[2]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = '1'.repeat(151)
    await Vue.nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 150 characters')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[2]
    // hint
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Business names must contain')
    // max chars
    wrapper.vm.$data.searchValue = '12345678901234567890123456789012345678901234567890123456789012345678901'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.message).toBeDefined()
    await Vue.nextTick()
    const messages1 = wrapper.findAll('.v-messages__message')
    expect(messages1.length).toBe(1)
    expect(messages1.at(0).text()).toContain('Maximum 70 characters')
    // special chars
    wrapper.vm.$data.searchValue = 'F10@'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.message).toBeDefined()
    await Vue.nextTick()
    const messages2 = wrapper.findAll('.v-messages__message')
    expect(messages2.length).toBe(1)
    expect(messages2.at(0).text()).toContain("don't normally contain special characters")
  })
})

describe('MHR validation', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[4]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchValue).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a manufactured home registration number to search')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is not numbers only', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[4]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = '1234F'
    await Vue.nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Must contain numbers only')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is more than maximum characters', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[4]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = '1234567'
    await Vue.nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 6 digits')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[4]
    // hint
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Manufactured home registration number must contain')
    // popup
    wrapper.vm.$data.searchValue = '10'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.popUp).toBeDefined()
    await Vue.nextTick()
    const popUpMessages = wrapper.findAll('.v-tooltip__content')
    expect(popUpMessages.length).toBe(1)
    expect(popUpMessages.at(0).text()).toContain('This may not be a valid manufactured')
    // max digits
    wrapper.vm.$data.searchValue = '1234567'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.message).toBeDefined()
    await Vue.nextTick()
    const messages1 = wrapper.findAll('.v-messages__message')
    expect(messages1.length).toBe(1)
    expect(messages1.at(0).text()).toContain('Maximum 6 digits')
    // numbers only
    wrapper.vm.$data.searchValue = '12345A'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.message).toBeDefined()
    await Vue.nextTick()
    const messages2 = wrapper.findAll('.v-messages__message')
    expect(messages2.length).toBe(1)
    expect(messages2.at(0).text()).toContain('Must contain numbers only')
    // special chars
    wrapper.vm.$data.searchValue = '10@'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.message).toBeDefined()
    await Vue.nextTick()
    const messages3 = wrapper.findAll('.v-messages__message')
    expect(messages3.length).toBe(1)
    expect(messages3.at(0).text()).toContain('Must contain numbers only')
  })
})

describe('Aircraft validation', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[5]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchValue).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter an aircraft airframe D.O.T. number to search')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is more than maximum characters', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[5]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    wrapper.vm.$data.searchValue = 'abcdefghijklmnopqrstuvwxyz'
    await Vue.nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 25 characters')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[5]
    // hint
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Up to 25 characters')
    // popup
    wrapper.vm.$data.searchValue = 'ab'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.popUp).toBeDefined()
    await Vue.nextTick()
    const popUpMessages = wrapper.findAll('.v-tooltip__content')
    expect(popUpMessages.length).toBe(1)
    expect(popUpMessages.at(0).text()).toContain('This may not be a valid Aircraft')
    // max digits
    wrapper.vm.$data.searchValue = 'abcdefghijklmnopqrstuvwxyz'
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations?.searchValue?.message).toBeDefined()
    await Vue.nextTick()
    const messages1 = wrapper.findAll('.v-messages__message')
    expect(messages1.length).toBe(1)
    expect(messages1.at(0).text()).toContain('Maximum 25 characters')

  })
})

describe('Registration number validation', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(SearchTypes)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[6]
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    expect(wrapper.vm.$data.searchValue).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a registration number to search')
    await Vue.nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is in incorrect format', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[6]
    const incorrectValues = ['123456WW', '12345W', '123', 'abc']
    for (let i = 0; i < incorrectValues.length; i++) {
      wrapper.vm.$data.selectedSearchType = select1
      await Vue.nextTick()
      wrapper.vm.$data.searchValue = incorrectValues[i]
      await Vue.nextTick()
      wrapper.find(searchButtonSelector).trigger('click')
      await Vue.nextTick()
      expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
      const messages1 = wrapper.findAll('.v-messages__message')
      expect(messages1.length).toBe(1)
      expect(messages1.at(0).text()).toBe('Registration numbers contain 7 characters')
      await Vue.nextTick()
      expect(getLastEvent(wrapper, searchError)).toBeNull()
      expect(getLastEvent(wrapper, searchData)).toBeNull()
    }
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = wrapper.vm.$data.searchTypes[6]
    // hint
    wrapper.vm.$data.selectedSearchType = select1
    await Vue.nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Registration numbers contain')
    const incorrectValues = ['123456WW', 'W1', 'ab', '@', '123WA', '.']
    for (let i = 0; i < incorrectValues.length; i++) {
      wrapper.vm.$data.selectedSearchType = select1
      await Vue.nextTick()
      wrapper.vm.$data.searchValue = incorrectValues[i]
      await Vue.nextTick()
      expect(wrapper.vm.$data.validations.searchValue?.message).toBeDefined()
      await Vue.nextTick()
      const messages1 = wrapper.findAll('.v-messages__message')
      expect(messages1.length).toBe(1)
      expect(messages1.at(0).text()).toBe('Registration numbers contain 7 characters')
    }
  })
})
