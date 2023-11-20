import { PartyAutocomplete } from '@/components/parties/party'
import { mockedPartyCodeSearchResults, mockedSelectSecurityAgreement } from './test-data'
import { createComponent, getLastEvent } from './utils'
import flushPromises from 'flush-promises'
import { useStore } from '@/store/store'

const store = useStore()
const partyCodeAutoComplete = '#party-search-auto-complete'

// event
const selectItem: string = 'selectItem'

describe('Secured Party search autocomplete tests', () => {
  let wrapper

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.setRegistrationType(registrationType)
    wrapper = await createComponent(PartyAutocomplete, { autoCompleteItems: mockedPartyCodeSearchResults })
    await flushPromises()
  })

  it('shows the auto complete drop down when searching for a party', async () => {
    const autoCompleteItems = wrapper.findAll('.v-list-item-subtitle')
    expect(wrapper.find(partyCodeAutoComplete).exists()).toBe(true)
    expect(autoCompleteItems.length).toBeGreaterThan(1)
    expect(wrapper.find('#no-party-matches').exists()).toBe(false)
  })

  it('adds the party after a name in the list is clicked', async () => {
    const partySearchAddLinks = wrapper.findAll('.v-list-item-action')
    expect(store.getAddSecuredPartiesAndDebtors.securedParties.length).toBe(0)
    expect(partySearchAddLinks.length).toBe(3)
    const icon = partySearchAddLinks.at(0).find('.v-icon')
    icon.trigger('click')
    await flushPromises()
    expect(store.getAddSecuredPartiesAndDebtors.securedParties.length).toBe(1)
    expect(
      store.getAddSecuredPartiesAndDebtors.securedParties[0].businessName
    ).toBe('TONY SCOTT REVENUE ADMINISTRATION BRANCH')
    // the autocomplete is then closed & event emitted
    expect(wrapper.emitted().selectItem).toBeTruthy()
  })
})

describe('Registering Party search autocomplete tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(PartyAutocomplete,
      { autoCompleteItems: [], isRegisteringParty: true }
    )
    await flushPromises()
  })

  it('shows the auto complete drop down when searching for a party', async () => {
    expect(wrapper.find('#no-party-matches').text()).toContain('No matches found')
    expect(wrapper.find('#no-party-matches').text()).toContain('Registering Party')
  })
})
