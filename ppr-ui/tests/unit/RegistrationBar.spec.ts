import { nextTick } from 'vue'
import { RegistrationBar, RegistrationBarButtonList, RegistrationBarTypeAheadList } from '@/components/registration'
import {
  RegistrationTypesMiscellaneousCC,
  RegistrationTypesStandard
} from '@/resources'
import { AccountProductCodes, AccountProductMemberships, UIRegistrationTypes } from '@/enums'
import type { RegistrationTypeIF } from '@/interfaces'
import { useStore } from '@/store/store'
import { createComponent, getLastEvent } from './utils'
import flushPromises from 'flush-promises'
const store = useStore()

// registration lists
const standardRegistrations: Array<RegistrationTypeIF> = RegistrationTypesStandard
const miscCrownChargeRegistrations: Array<RegistrationTypeIF> = RegistrationTypesMiscellaneousCC

// Events
const selectedType = 'selected'

// Input field selectors / buttons
const registrationBar = '.registration-bar'
const registrationButton = '#registration-bar-btn'
const registrationButtonDropdown = '#registration-more-actions-btn'
// basic drop down selects
const selectSecurity = '#btn-security'
const selectReparers = '#btn-repairers'
const selectMarriage = '#btn-marriage'
const selectLand = '#btn-land'
const selectSale = '#btn-sale'
const selectMHL = '#btn-mhl'
const selectFCL = '#btn-fcl'
const selectFCC = '#btn-fcc'
const selectFSL = '#btn-fsl'

describe('RegistrationBar select basic drop down tests', () => {
  let wrapper
  const defaultRegistration: RegistrationTypeIF = standardRegistrations[1]

  beforeEach(async () => {
    await store.setAccountProductSubscription({
      [AccountProductCodes.RPPR]: {
        membership: AccountProductMemberships.MEMBER,
        roles: []
      }
    })
    wrapper = await createComponent(RegistrationBarButtonList)
  })

  it('renders with default registration button', async () => {
    expect(wrapper.findComponent(RegistrationBarButtonList).exists()).toBe(true)
    /** verify test setup:
    * 1) account subscription with no roles
    * 2) default registration is set to security agreement
    */
    expect(store.getStateModel.accountProductSubscriptions[AccountProductCodes.RPPR].roles).toEqual([])
    expect(defaultRegistration.registrationTypeUI).toBe(UIRegistrationTypes.SECURITY_AGREEMENT)
    // check security agreement displayed
    const button = wrapper.findAll(registrationButton)
    expect(button.length).toBe(1)
    expect(button.at(0).text()).toContain(UIRegistrationTypes.SECURITY_AGREEMENT)
    // click security agreement
    wrapper.find(registrationButton).trigger('click')
    await flushPromises()
    // check emit
    expect(getLastEvent(wrapper, selectedType)).toBe(defaultRegistration)
  })
  it('renders the default button dropdown list', async () => {
    // check drop down button displayed
    const buttonDropDown = wrapper.find(registrationButtonDropdown)
    expect(buttonDropDown.exists()).toBe(true)
    buttonDropDown.trigger('click')
    await flushPromises()
    // Verify displayed list of standard registration types
    const dropDownItems = [
      selectSecurity,
      selectReparers,
      selectMarriage,
      selectLand,
      selectSale,
      selectMHL,
      selectFCL,
      selectFCC,
      selectFSL
    ]
    for (let i = 0; i < dropDownItems.length; i++) {
      expect(wrapper.find(dropDownItems[i]).exists()).toBe(true)
    }
    // FUTURE: add a test for each registration type
    // selecting an item in the list emits it from the component
    wrapper.find(selectReparers).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, selectedType)).toBe(standardRegistrations[2])
  })
})

describe('RegistrationBar rppr subscribed autocomplete tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setAccountProductSubscription({
      [AccountProductCodes.RPPR]: {
        membership: AccountProductMemberships.MEMBER,
        roles: ['edit']
      }
    })
    wrapper = await createComponent(RegistrationBar)
  })

  it('renders with registration autocomplete', async () => {
    expect(wrapper.findComponent(RegistrationBar).exists()).toBe(true)
    expect(wrapper.find(registrationBar).exists()).toBe(true)
    // verify edit role set
    const accountProductSubscriptions = store.getStateModel.accountProductSubscriptions
    expect(accountProductSubscriptions[AccountProductCodes.RPPR].roles).toEqual(['edit'])

    // check autocomplete displayed
    const autocomplete = wrapper.findComponent(RegistrationBarTypeAheadList)
    expect(autocomplete.text()).toContain('Start a New Personal Property Registration')
    // simulate selection (vitest does not pickup autocomplete list)
    autocomplete.vm.$emit('selected', miscCrownChargeRegistrations[3])
    await flushPromises()
    // check emit
    expect(getLastEvent(autocomplete, selectedType)).toBe(miscCrownChargeRegistrations[3])
  })
})
