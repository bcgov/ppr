import { nextTick } from 'vue'
import { SearchBar } from '@/components/search'
import { createComponent, getLastEvent } from './utils'
import { useStore } from '@/store/store'
import flushPromises from 'flush-promises'
import { SearchTypeIF } from '@/interfaces'
import { MHRSearchTypes, SearchTypes } from '@/resources'
import { UISearchTypes } from '@/enums'

const store = useStore()

// Events
const searchError: string = 'searchError'
const searchData: string = 'searchData'

// Input field selectors / buttons
const searchButtonSelector: string = '.search-bar-btn'

describe('SearchBar base validation', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAuthRoles(['staff', 'ppr_staff'])
    wrapper = await createComponent(SearchBar)
  })

  it('prevents searching and gives validation when category is not selected', async () => {
    expect(wrapper.vm.selectedSearchType).toBeUndefined()
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await flushPromises()
    expect(wrapper.vm.validations.category?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Please select a category')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })
})

describe('Serial number validation', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(SearchBar)
  })

  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = SearchTypes[1]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    expect(wrapper.vm.searchValue).toBeNull()
    expect(wrapper.vm.selectedSearchType).toEqual(select1)
    wrapper.find(searchButtonSelector).trigger('click')
    await flushPromises()
    expect(wrapper.vm.validations).toBeDefined()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a serial number to search')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching and gives validation when the search is over 25 characters', async () => {
    const select1: SearchTypeIF = SearchTypes[1]
    wrapper.vm.selectedSearchType = select1
    expect(wrapper.vm.selectedSearchType.searchTypeUI).toBe(UISearchTypes.SERIAL_NUMBER)
    await nextTick()
    wrapper.vm.searchValue = '12345678901234567890123456'
    await nextTick()
    expect(wrapper.vm.searchValue).toBe('12345678901234567890123456')
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 25 characters')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = SearchTypes[1]
    // hint
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Serial numbers normally contain')
    // popup
    wrapper.vm.searchValue = 'F10'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.popUp).toBeDefined()
    await nextTick()

    const popUpMessages = await wrapper.find('.tooltip-col')
    expect(popUpMessages.exists()).toBe(true)
    expect(wrapper.vm.searchPopUp[0]).toContain('This may not be a valid serial')
    // special chars
    wrapper.vm.searchValue = 'F10@'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.message).toBeDefined()
    await nextTick()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toContain("don't normally contain special characters")
    // maximum 25 characters
    wrapper.vm.searchValue = '12345678901234567890123456'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.message).toBeDefined()
    await nextTick()
    const errorMessages = wrapper.findAll('.v-messages__message')
    expect(errorMessages.length).toBe(1)
    expect(errorMessages.at(0).text()).toBe('Maximum 25 characters')
  })
})

describe('Individual debtor validation', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(SearchBar)
  })


  it('prevents searching and gives validation when first name or last name is empty', async () => {
    const select1: SearchTypeIF = SearchTypes[2]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    expect(wrapper.vm.searchValue).toBeNull()
    expect(wrapper.vm.searchValueFirst).toBeUndefined()
    expect(wrapper.vm.searchValueSecond).toBeUndefined()
    expect(wrapper.vm.searchValueLast).toBeUndefined()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.messageFirst).toBeDefined()
    expect(wrapper.vm.validations.searchValue?.messageSecond).toBeUndefined()
    expect(wrapper.vm.validations.searchValue?.messageLast).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(2)
    expect(messages.at(0).text()).toBe('Enter a first name')
    expect(messages.at(1).text()).toBe('Enter a last name')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching and gives validation when first name is above max characters', async () => {
    const select1: SearchTypeIF = SearchTypes[2]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    wrapper.vm.searchValueFirst = '1'.repeat(51)
    wrapper.vm.searchValueLast = 'last'
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.messageFirst).toBeDefined()
    expect(wrapper.vm.validations.searchValue?.messageSecond).toBeUndefined()
    expect(wrapper.vm.validations.searchValue?.messageLast).toBeUndefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 50 characters')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching and gives validation when last name is above max characters', async () => {
    const select1: SearchTypeIF = SearchTypes[2]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    wrapper.vm.searchValueFirst = 'first'
    wrapper.vm.searchValueLast = '1'.repeat(51)
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.messageFirst).toBeUndefined()
    expect(wrapper.vm.validations.searchValue?.messageSecond).toBeUndefined()
    expect(wrapper.vm.validations.searchValue?.messageLast).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 50 characters')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = SearchTypes[1]
    // hint
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Serial numbers normally contain')
    // popup
    wrapper.vm.searchValue = 'F10'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.popUp).toBeDefined()
    await nextTick()
    const popUpMessages = await wrapper.find('.tooltip-col')
    expect(popUpMessages.exists()).toBe(true)
    expect(wrapper.vm.searchPopUp[0]).toContain('This may not be a valid serial')
    // special chars
    wrapper.vm.searchValue = 'F10@'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.message).toBeDefined()
    await nextTick()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toContain("don't normally contain special characters")
  })
})

describe('Business debtor validation', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(SearchBar)
  })

  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = SearchTypes[3]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    expect(wrapper.vm.searchValue).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a business debtor name to search')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is less than minimum characters', async () => {
    const select1: SearchTypeIF = SearchTypes[3]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    wrapper.vm.searchValue = 'F'
    await nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Must contain more than 1 character')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is more than maximum characters', async () => {
    const select1: SearchTypeIF = SearchTypes[3]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    wrapper.vm.searchValue = '1'.repeat(151)
    await nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 150 characters')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = SearchTypes[3]
    // hint
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Business names must contain')
    // max chars
    wrapper.vm.searchValue = '1'.repeat(151)
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.message).toBeDefined()
    await nextTick()
    const messages1 = wrapper.findAll('.v-messages__message')
    expect(messages1.length).toBe(1)
    expect(messages1.at(0).text()).toContain('Maximum 150 characters')
  })
})

describe('MHR validation', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAuthRoles(['staff', 'ppr_staff'])
    wrapper = await createComponent(SearchBar)
  })


  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = SearchTypes[4]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    expect(wrapper.vm.searchValue).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a manufactured home registration number')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is not numbers only', async () => {
    const select1: SearchTypeIF = SearchTypes[4]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    wrapper.vm.searchValue = '1234F'
    await nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Must contain numbers only')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is more than maximum characters', async () => {
    const select1: SearchTypeIF = SearchTypes[4]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    wrapper.vm.searchValue = '1234567'
    await nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 6 digits')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = SearchTypes[4]
    // hint
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Manufactured home registration numbers normally contain up to 6 digits')
    // popup
    wrapper.vm.searchValue = '10'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.popUp).toBeDefined()
    await nextTick()
    const popUpMessages = await wrapper.find('.tooltip-col')
    expect(popUpMessages.exists()).toBe(true)
    expect(wrapper.vm.searchPopUp[0]).toContain('This may not be a valid manufactured')
    // max digits
    wrapper.vm.searchValue = '1234567'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.message).toBeDefined()
    await nextTick()
    const messages1 = wrapper.findAll('.v-messages__message')
    expect(messages1.length).toBe(1)
    expect(messages1.at(0).text()).toContain('Maximum 6 digits')
    // numbers only
    wrapper.vm.searchValue = '12345A'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.message).toBeDefined()
    await nextTick()
    const messages2 = wrapper.findAll('.v-messages__message')
    expect(messages2.length).toBe(1)
    expect(messages2.at(0).text()).toContain('Must contain numbers only')
    // special chars
    wrapper.vm.searchValue = '10@'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.message).toBeDefined()
    await nextTick()
    const messages3 = wrapper.findAll('.v-messages__message')
    expect(messages3.length).toBe(1)
    expect(messages3.at(0).text()).toContain('Must contain numbers only')
  })
})

describe('Aircraft validation', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(SearchBar)
  })


  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = SearchTypes[5]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    expect(wrapper.vm.searchValue).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter an aircraft airframe D.O.T. number to search')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is more than maximum characters', async () => {
    const select1: SearchTypeIF = SearchTypes[5]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    wrapper.vm.searchValue = 'abcdefghijklmnopqrstuvwxyz'
    await nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 25 characters')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = SearchTypes[5]
    // hint
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Up to 25 characters')
    // popup
    wrapper.vm.searchValue = 'ab'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.popUp).toBeDefined()
    await nextTick()
    const popUpMessages = await wrapper.find('.tooltip-col')
    expect(popUpMessages.exists()).toBe(true)
    expect(wrapper.vm.searchPopUp[0]).toContain('This may not be a valid Aircraft')
    // max digits
    wrapper.vm.searchValue = 'abcdefghijklmnopqrstuvwxyz'
    await nextTick()
    expect(wrapper.vm.validations?.searchValue?.message).toBeDefined()
    await nextTick()
    const messages1 = wrapper.findAll('.v-messages__message')
    expect(messages1.length).toBe(1)
    expect(messages1.at(0).text()).toContain('Maximum 25 characters')
  })
})

describe('Registration number validation', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(SearchBar)
  })


  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = SearchTypes[6]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    expect(wrapper.vm.searchValue).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter a registration number to search')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is in incorrect format', async () => {
    const select1: SearchTypeIF = SearchTypes[6]
    const incorrectValues = ['123456WW', '12345W', '123', 'abc']
    for (let i = 0; i < incorrectValues.length; i++) {
      wrapper.vm.selectedSearchType = select1
      await nextTick()
      wrapper.vm.searchValue = incorrectValues[i]
      await nextTick()
      wrapper.find(searchButtonSelector).trigger('click')
      await nextTick()
      expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
      const messages1 = wrapper.findAll('.v-messages__message')
      expect(messages1.length).toBe(1)
      expect(messages1.at(0).text()).toBe('Registration numbers contain 7 characters')
      await nextTick()
      expect(getLastEvent(wrapper, searchError)).toBeNull()
      expect(getLastEvent(wrapper, searchData)).toBeNull()
    }
  })

  it('gives validation messages/hints as user types', async () => {
    const select1: SearchTypeIF = SearchTypes[6]
    // hint
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    const hints = wrapper.findAll('.v-messages__message')
    expect(hints.length).toBe(1)
    expect(hints.at(0).text()).toContain('Registration numbers contain')
    const incorrectValues = ['123456WW', 'W1', 'ab', '@', '123WA', '.']
    for (let i = 0; i < incorrectValues.length; i++) {
      wrapper.vm.selectedSearchType = select1
      await nextTick()
      wrapper.vm.searchValue = incorrectValues[i]
      await nextTick()
      expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
      await nextTick()
      const messages1 = wrapper.findAll('.v-messages__message')
      expect(messages1.length).toBe(1)
      expect(messages1.at(0).text()).toBe('Registration numbers contain 7 characters')
    }
  })
})

describe('organization name validation', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(SearchBar)
  })


  it('prevents searching and gives validation when the search is empty', async () => {
    const select1: SearchTypeIF = MHRSearchTypes[3]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    expect(wrapper.vm.searchValue).toBeNull()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Enter an organization name to search')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is less than minimum characters', async () => {
    const select1: SearchTypeIF = MHRSearchTypes[3]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    wrapper.vm.searchValue = 'F'
    await nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Must contain more than 1 character')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })

  it('prevents searching when search value is more than maximum characters', async () => {
    const select1: SearchTypeIF = MHRSearchTypes[3]
    wrapper.vm.selectedSearchType = select1
    await nextTick()
    wrapper.vm.searchValue = '1'.repeat(81)
    await nextTick()
    wrapper.find(searchButtonSelector).trigger('click')
    await nextTick()
    expect(wrapper.vm.validations.searchValue?.message).toBeDefined()
    const messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 70 characters')
    await nextTick()
    expect(getLastEvent(wrapper, searchError)).toBeNull()
    expect(getLastEvent(wrapper, searchData)).toBeNull()
  })
})
