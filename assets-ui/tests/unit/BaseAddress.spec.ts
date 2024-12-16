// Components
import { BaseAddress } from '@/composables/address'
import { AddressIF } from '@/interfaces'
import { createComponent, getLastEvent } from './utils'
import { DefaultSchema } from '@/composables/address/resources'

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

describe('Base Address component display', () => {
  let wrapper
  let address: AddressIF

  beforeEach(async () => {
    address = { ...emptyAddress }
    address.city = 'Victoria'
    address.country = 'CA'
    address.postalCode = 'V8V 1S9'
    address.region = 'BC'
    address.street = '1234'
    address.streetAdditional = 'bla'
    address.deliveryInstructions = 'deliver'
    wrapper = await createComponent(BaseAddress, {
      value: address,
      schema: DefaultSchema,
      editing: false,
      triggerErrors: false
    })
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
  let wrapper
  let address: AddressIF

  beforeEach(async () => {
    address = { ...emptyAddress }
    wrapper = await createComponent(BaseAddress, {
      value: address,
      schema: DefaultSchema,
      editing: true,
      triggerErrors: false
    })
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
  let wrapper
  let address: AddressIF

  beforeEach(async () => {
    address = { ...emptyAddress }
    address.city = 'Victoria'
    address.country = 'CA'
    address.postalCode = 'V8V 1S9'
    address.region = 'BC'
    address.street = '1234'
    address.streetAdditional = 'bla'
    address.deliveryInstructions = 'deliver'
    wrapper = await createComponent(BaseAddress, {
      value: address,
      schema: DefaultSchema,
      editing: true,
      triggerErrors: false
    })
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

    expect(wrapper.vm.addressLocal.country).toEqual(address.country)
    expect(wrapper.vm.addressLocal.street).toEqual(address.street)
    expect(wrapper.vm.addressLocal.streetAdditional).toEqual(address.streetAdditional)
    expect(wrapper.vm.addressLocal.city).toEqual(address.city)
    expect(wrapper.vm.addressLocal.region).toEqual(address.region)
    expect(wrapper.vm.addressLocal.postalCode).toEqual(address.postalCode)

    expect(getLastEvent(wrapper, valid)).toBe(true)
  })
})
