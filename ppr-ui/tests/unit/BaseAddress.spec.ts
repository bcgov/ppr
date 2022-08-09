// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { BaseAddress } from '@/composables/address'

// Other
import { AddressIF, SchemaIF } from '@/composables/address/interfaces'
import { DefaultSchema } from '@/composables/address/resources'
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const valid: string = 'valid'

// Input field selectors / buttons
const readOnlyAddressBlock = '.address-block__info'
const countryEdit = '.address-country'
const streetEdit = '.street-address'
const streetAdditionalEdit = '.street-address-additional'
const cityEdit = '.address-city'
const regionEdit = '.address-region'
const postalCodeEdit = '.postal-code'
const deliveryEdit = '.delivery-instructions'

const emptyAddress: AddressIF = {
  street: '',
  streetAdditional: '',
  city: '',
  region: '',
  country: '',
  postalCode: '',
  deliveryInstructions: ''
}

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  value: AddressIF,
  schema: SchemaIF,
  editing: boolean,
  triggerErrors: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(BaseAddress, {
    localVue,
    propsData: { value, editing, schema, triggerErrors },
    store,
    vuetify
  })
}

describe('Base Address component display', () => {
  let wrapper: Wrapper<any>
  let address: AddressIF = null

  beforeEach(async () => {
    address = { ...emptyAddress }
    address.city = 'Victoria'
    address.country = 'CA'
    address.postalCode = 'V8V 1S9'
    address.region = 'BC'
    address.street = '1234'
    address.streetAdditional = 'bla'
    address.deliveryInstructions = 'deliver'
    wrapper = createComponent(address, DefaultSchema, false, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the address in read only state', async () => {
    expect(wrapper.findComponent(BaseAddress).exists()).toBe(true)
    // displays address
    const addressBlock = wrapper.findAll(readOnlyAddressBlock)
    expect(addressBlock.length).toBe(1)
    expect(addressBlock.at(0).text()).toContain(address.city)
    expect(addressBlock.at(0).text()).toContain('Canada')
    expect(addressBlock.at(0).text()).toContain(address.region)
    expect(addressBlock.at(0).text()).toContain(address.street)
    expect(addressBlock.at(0).text()).toContain(address.postalCode)
    expect(addressBlock.at(0).text()).toContain(address.streetAdditional)
    expect(addressBlock.at(0).text()).toContain(address.deliveryInstructions)
    // does not display edit version / clickable fields
    expect(wrapper.find(countryEdit).exists()).toBe(false)
    expect(wrapper.find(streetEdit).exists()).toBe(false)
    expect(wrapper.find(streetAdditionalEdit).exists()).toBe(false)
    expect(wrapper.find(cityEdit).exists()).toBe(false)
    expect(wrapper.find(regionEdit).exists()).toBe(false)
    expect(wrapper.find(postalCodeEdit).exists()).toBe(false)
    expect(wrapper.find(deliveryEdit).exists()).toBe(false)
    // emits valid
    expect(getLastEvent(wrapper, valid)).toBe(true)
  })
})

describe('Base Address component edit', () => {
  let wrapper: Wrapper<any>
  let address: AddressIF = null

  beforeEach(async () => {
    address = { ...emptyAddress }
    wrapper = createComponent(address, DefaultSchema, true, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the address in edit state', async () => {
    expect(wrapper.findComponent(BaseAddress).exists()).toBe(true)
    expect(wrapper.find(readOnlyAddressBlock).exists()).toBe(false)
    // displays address in edit mode
    expect(wrapper.find(countryEdit).exists()).toBe(true)
    expect(wrapper.find(streetEdit).exists()).toBe(true)
    expect(wrapper.find(streetAdditionalEdit).exists()).toBe(true)
    expect(wrapper.find(cityEdit).exists()).toBe(true)
    expect(wrapper.find(regionEdit).exists()).toBe(true)
    expect(wrapper.find(postalCodeEdit).exists()).toBe(true)
    expect(wrapper.find(deliveryEdit).exists()).toBe(true)
    expect(getLastEvent(wrapper, valid)).toBe(false)
  })
})

describe('Base Address component edit existing address', () => {
  let wrapper: Wrapper<any>
  let address: AddressIF = null

  beforeEach(async () => {
    address = { ...emptyAddress }
    address.city = 'Victoria'
    address.country = 'CA'
    address.postalCode = 'V8V 1S9'
    address.region = 'BC'
    address.street = '1234'
    address.streetAdditional = 'bla'
    address.deliveryInstructions = 'deliver'
    wrapper = createComponent(address, DefaultSchema, true, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('displays all address values in edit block', async () => {
    expect(wrapper.findComponent(BaseAddress).exists()).toBe(true)
    expect(wrapper.find(readOnlyAddressBlock).exists()).toBe(false)
    // displays address in edit mode
    expect(wrapper.find(countryEdit).exists()).toBe(true)
    expect(wrapper.find(streetEdit).exists()).toBe(true)
    expect(wrapper.find(streetAdditionalEdit).exists()).toBe(true)
    expect(wrapper.find(cityEdit).exists()).toBe(true)
    expect(wrapper.find(regionEdit).exists()).toBe(true)
    expect(wrapper.find(postalCodeEdit).exists()).toBe(true)
    expect(wrapper.find(deliveryEdit).exists()).toBe(true)

    const country = wrapper.find(countryEdit).props().value
    const street = wrapper.find(streetEdit).props().value
    const streetAdditional = wrapper.find(streetAdditionalEdit).props().value
    const city = wrapper.find(cityEdit).props().value
    const region = wrapper.find(regionEdit).props().value
    const postalCode = wrapper.find(postalCodeEdit).props().value
    const delivery = wrapper.find(deliveryEdit).props().value

    expect(country).toEqual(address.country)
    expect(street).toEqual(address.street)
    expect(streetAdditional).toEqual(address.streetAdditional)
    expect(city).toEqual(address.city)
    expect(region).toEqual(address.region)
    expect(postalCode).toEqual(address.postalCode)
    expect(delivery).toEqual(address.deliveryInstructions)

    expect(getLastEvent(wrapper, valid)).toBe(true)
  })
})
