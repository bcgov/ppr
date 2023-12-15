import { nextTick } from 'vue'
import { createComponent, getLastEvent, getTestId } from './utils'
import { useStore } from '@/store/store'
import {
  mockedLienUnpaid,
  mockedOtherCarbon,
  mockedPartyCodeSearchResults, mockedRegisteringParty1,
  mockedSecuredParties1, mockedSecuredParties2, mockedSecuredParties3, mockedSecuredPartiesAmendment,
  mockedSelectSecurityAgreement
} from './test-data'
import { EditParty, PartySearch, SecuredParties } from '@/components/parties/party'
import { SearchPartyIF } from '@/interfaces'
import { ChangeSecuredPartyDialog } from '@/components/dialogs'
import { ActionTypes, RegistrationFlowType } from '@/enums'
import flushPromises from 'flush-promises'
import { cloneDeep } from 'lodash'
const store = useStore()

const partyAutoComplete = '#secured-party-autocomplete'

describe('Secured Party SA tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    wrapper = await createComponent(SecuredParties)
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    expect(wrapper.findComponent(PartySearch).exists()).toBeTruthy()
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditParty).exists()).toBeFalsy()
  })
})

describe('Secured Party store tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredParties1
    })
    wrapper = await createComponent(SecuredParties)
  })

  it('renders secured party table and headers', async () => {
    expect(wrapper.find('.party-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('th').length).toBe(5)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.party-row').length

    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.party-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('SECURED PARTY COMPANY LTD.')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[2].textContent).toContain('test@company.com')
  })
})

describe('Secured Party Other registration type tests', () => {
  let wrapper
  const pprResp: Array<SearchPartyIF> = mockedPartyCodeSearchResults

  beforeEach(async () => {
    // get.returns(
    //   new Promise(resolve =>
    //     resolve({
    //       data: pprResp
    //     })
    //   )
    // )
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

describe('Secured party amendment tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredPartiesAmendment
    })
    await store.setOriginalAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredPartiesAmendment
    })
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = await createComponent(SecuredParties, {})
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.party-row').length
    // three parties, three rows
    expect(rowCount).toEqual(3)
  })

  it('displays the correct chips in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.party-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.party-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.party-row')[2]
    expect(item1.querySelectorAll('td')[0].textContent).toContain('ADDED')
    expect(item2.querySelectorAll('td')[0].textContent).toContain('AMENDED')
    expect(item3.querySelectorAll('td')[0].textContent).toContain('DELETED')
  })

  it('displays the correct actions in the table rows', async () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.party-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.party-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.party-row')[2]
    expect(item1.querySelectorAll('td')[4].textContent).toContain('Edit')
    expect(item2.querySelectorAll('td')[4].textContent).toContain('Undo')
    expect(item3.querySelectorAll('td')[4].textContent).toContain('Undo')

    // Note: V-menus have moved to overlays (amongst other things) and out of the wrapper. TBD how to access and test
  })

  it('displays the error', async () => {
    const parties = cloneDeep(mockedSecuredParties1)
    expect(parties.length).toEqual(1)
    parties[0].action = ActionTypes.REMOVED
    wrapper = await createComponent(SecuredParties, {})
    wrapper.vm.securedParties = parties
    wrapper.vm.$props.setShowInvalid = true
    expect(wrapper.vm.getSecuredPartyValidity()).toBe(false)
    wrapper.vm.showErrorSecuredParties = true
    await nextTick()
    expect(wrapper.findAll('.border-error-left').length).toBe(1)
  })

  it('fires the open event', async () => {
    wrapper.vm.initEdit(1)
    await flushPromises()
    expect(getLastEvent(wrapper, 'securedPartyOpen')).toBeTruthy()
  })

  it('It does not display restrict secured party', () => {
    expect(wrapper.find(getTestId('restricted-prompt')).exists()).toBe(false)
  })
})

describe('Secured party with code test', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredParties3
    })
    await store.setOriginalAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredParties3
    })
    await store.setRegistrationType(mockedSelectSecurityAgreement())
    wrapper = await createComponent(SecuredParties, {})
  })

  it('displays remove only for a secured party with code', async () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.party-row')[0]
    expect(item1.querySelectorAll('td')[4].textContent).toContain('Delete')

    const dropDowns = wrapper.findAll('.party-row .actions__more-actions__btn')
    // 0 drop downs
    expect(dropDowns.length).toBe(0)
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
