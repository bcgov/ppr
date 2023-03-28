// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Local
import { RegistrationBar, RegistrationBarTypeAheadList } from '@/components/registration'
import {
  RegistrationTypesMiscellaneousCC,
  RegistrationTypesStandard
} from '@/resources'
import { AccountProductCodes, AccountProductMemberships, UIRegistrationTypes } from '@/enums'
import { RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// registration lists
const standardRegistrations: Array<RegistrationTypeIF> = RegistrationTypesStandard
const miscCrownChargeRegistrations: Array<RegistrationTypeIF> = RegistrationTypesMiscellaneousCC

// Events
const selectedType = 'selected-registration-type'

// Input field selectors / buttons
const registrationBar = '.registration-bar'
const registrationButton = '#registration-bar-btn'
const registrationButtonDropdown = '#registration-more-actions-btn'
// basic drop down selects
const selectSecurity = '#btn-security'
const selectReparers = '#btn-reparers'
const selectMarriage = '#btn-marriage'
const selectLand = '#btn-land'
const selectSale = '#btn-sale'
const selectMHL = '#btn-mhl'
const selectFCL = '#btn-fcl'
const selectFCC = '#btn-fcc'
const selectFSL = '#btn-fsl'

/**
 * Returns the last event for a given name, to be used for testing event propagation in response to component changes.
 *
 * @param wrapper the wrapper for the component that is being tested.
 * @param name the name of the event that is to be returned.
 *
 * @returns the value of the last named event for the wrapper.
 */
function getLastEvent (wrapper: Wrapper<any>, name: string): any {
  const eventsList: Array<any> = wrapper.emitted(name)
  if (!eventsList) {
    return null
  }
  const events: Array<any> = eventsList[eventsList.length - 1]
  return events[0]
}

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
  return mount(RegistrationBar, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('RegistrationBar select basic drop down tests', () => {
  let wrapper: Wrapper<any>
  const defaultRegistration: RegistrationTypeIF = standardRegistrations[1]

  beforeEach(async () => {
    await store.dispatch('setAccountProductSubscription', {
      [AccountProductCodes.RPPR]: {
        membership: AccountProductMemberships.MEMBER,
        roles: []
      }
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default registration button', async () => {
    expect(wrapper.findComponent(RegistrationBar).exists()).toBe(true)
    expect(wrapper.find(registrationBar).exists()).toBe(true)
    /** verify test setup:
    * 1) account subscription with no roles
    * 2) default registration is set to security agreement
    */
    expect(wrapper.vm.$store.state.stateModel.accountProductSubscriptions[AccountProductCodes.RPPR].roles).toEqual([])
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
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAccountProductSubscription', {
      [AccountProductCodes.RPPR]: {
        membership: AccountProductMemberships.MEMBER,
        roles: ['edit']
      }
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with registration autocomplete', async () => {
    expect(wrapper.findComponent(RegistrationBar).exists()).toBe(true)
    expect(wrapper.find(registrationBar).exists()).toBe(true)
    // verify edit role set
    const accountProductSubscriptions = wrapper.vm.$store.state.stateModel.accountProductSubscriptions
    expect(accountProductSubscriptions[AccountProductCodes.RPPR].roles).toEqual(['edit'])
    // check autocomplete displayed
    const autocomplete = wrapper.findComponent(RegistrationBarTypeAheadList)
    expect(autocomplete.text()).toContain('Start a New Personal Property Registration')
    // simulate selection (jest does not pickup autocomplete list)
    autocomplete.vm.$emit('selected', miscCrownChargeRegistrations[3])
    await flushPromises()
    // check emit
    expect(getLastEvent(wrapper, selectedType)).toBe(miscCrownChargeRegistrations[3])
  })
})
