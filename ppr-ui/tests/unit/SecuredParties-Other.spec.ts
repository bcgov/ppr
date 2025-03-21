import type { SearchPartyIF } from '../../src/interfaces'
import {
  mockedLienUnpaid,
  mockedOtherCarbon,
  mockedPartyCodeSearchResults,
  mockedRegisteringParty1, mockedSecuredParties1,
  mockedSecuredParties2, mockedSecuredParties3
} from './test-data'
import { createComponent, getTestId } from './utils'
import { EditParty, PartySearch, SecuredParties } from '../../src/components/parties/party'
import { ChangeSecuredPartyDialog } from '../../src/components/dialogs'
import { ActionTypes, RegistrationFlowType } from '../../src/enums'
import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import { cloneDeep } from 'lodash'

const store = useStore()

const partyAutoComplete = '#secured-party-autocomplete'

describe('Secured Party Other registration type tests', () => {
  let wrapper
  const pprResp: Array<SearchPartyIF> = mockedPartyCodeSearchResults

  beforeEach(async () => {
    await store.setRegistrationType(mockedOtherCarbon())
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1,
      securedParties: mockedSecuredParties2
    })
    wrapper = await createComponent(SecuredParties, {})
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditParty).exists()).toBeFalsy()
    // shouldn't show party code search for other registration types
    expect(wrapper.findComponent(PartySearch).exists()).toBeFalsy()
    // should have autocomplete instead
    expect(wrapper.find(partyAutoComplete).exists()).toBeTruthy()

    // should have the dialog
    expect(wrapper.findComponent(ChangeSecuredPartyDialog).exists()).toBeTruthy()
  })

  it('shows the dialog with a secured party code change', async () => {
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)

    // should have the dialog
    expect(wrapper.findComponent(ChangeSecuredPartyDialog).exists()).toBeTruthy()

    expect(wrapper.find('#secured-party-autocomplete').exists()).toBeTruthy()

    // change the party code and then the dialog should show
    wrapper.vm.selectResult({ code: 123, businessName: 'Forrest Gump' })

    expect(wrapper.findComponent(ChangeSecuredPartyDialog).isVisible()).toBeTruthy()
  })

  it('is not valid if you remove the secured party for amendment', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    const parties = cloneDeep(mockedSecuredParties2)
    parties[0].action = ActionTypes.REMOVED
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1,
      securedParties: parties
    })

    // click remove
    wrapper.find('.party-row .actions__more-actions .v-remove').trigger('click')
    await nextTick()
    expect(wrapper.vm.getSecuredPartyValidity()).toBe(false)
  })

  it('shows the the removed & added secured parties for amendment', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    const parties = cloneDeep(mockedSecuredParties1)
    expect(parties.length).toEqual(1)
    parties[0].action = ActionTypes.REMOVED
    parties[1] = {
      action: ActionTypes.ADDED,
      businessName: 'SECURED PARTY COMPANY LTD.',
      emailAddress: 'test@company.com',
      address: {
        street: '1234 Fort St.',
        streetAdditional: '2nd floor',
        city: 'Victoria',
        region: 'BC',
        country: 'CA',
        postalCode: 'V8R1L2',
        deliveryInstructions: ''
      }
    }

    expect(parties.length).toEqual(2)
    wrapper.vm.securedParties = parties
    await nextTick()
    const rowCount = wrapper.vm.$el.querySelectorAll('.party-row').length
    // one removed party, one added party
    expect(rowCount).toEqual(2)
    const item1 = wrapper.vm.$el.querySelectorAll('.party-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.party-row')[1]
    expect(item1.querySelectorAll('td')[0].textContent).toContain('DELETED')
    expect(item2.querySelectorAll('td')[0].textContent).toContain('ADDED')
  })
})

describe('Restricted secured party test', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredParties3
    })

    await store.setRegistrationType(mockedLienUnpaid())
    wrapper = await createComponent(SecuredParties)
  })



  it('displays the correct prompt for a registration with restrictions on secured party', async () => {
    expect(wrapper.find(getTestId('restricted-prompt')).exists()).toBe(true)
  })

  it('validates secured parties properly', async () => {
    expect(wrapper.vm.getSecuredPartyValidity()).toBe(true)
    wrapper.vm.securedParties = [...mockedSecuredParties3, ...mockedSecuredParties1]
    expect(wrapper.vm.getSecuredPartyValidity()).toBe(false)
  })
})