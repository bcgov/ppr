import { RegistrationBarTypeAheadList } from '@/components/registration'
import { RegistrationOtherDialog } from '@/components/dialogs'
import { RegistrationTypesMiscellaneousCC } from '@/resources'
import { RegistrationTypeIF } from '@/interfaces'
import { UIRegistrationTypes } from '@/enums'
import { createComponent, getLastEvent } from './utils'
import flushPromises from 'flush-promises'

// registration lists
const miscCrownChargeRegistrations: Array<RegistrationTypeIF> = RegistrationTypesMiscellaneousCC

// Events
const selected = 'selected'

// Input field selectors / buttons
const registrationTypeAhead = '.registrationTypeAhead'

describe('RegistrationBar rppr subscribed autocomplete tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(RegistrationBarTypeAheadList)
  })

  it('renders registration autocomplete type ahead box', async () => {
    expect(wrapper.findComponent(RegistrationBarTypeAheadList).exists()).toBe(true)
    // check autocomplete displayed
    expect(wrapper.find(registrationTypeAhead).exists()).toBe(true)
  })

  it('emits registration on select', async () => {
    wrapper.vm.selected = miscCrownChargeRegistrations[4]
    await flushPromises()
    expect(getLastEvent(wrapper, selected)).toStrictEqual(miscCrownChargeRegistrations[4])
  })

  it('gives dialog when *other* type is selected', async () => {
    const otherRegistration = miscCrownChargeRegistrations[miscCrownChargeRegistrations.length - 1]
    expect(otherRegistration.registrationTypeUI).toBe(UIRegistrationTypes.OTHER)
    wrapper.vm.selected = otherRegistration
    await flushPromises()
    expect(getLastEvent(wrapper, selected)).toBeNull()
    const dialog = wrapper.findComponent(RegistrationOtherDialog)
    expect(dialog.exists()).toBe(true)
    expect(dialog.vm.$props.display).toBe(true)
    dialog.vm.$emit('proceed', false)
    await flushPromises()
    expect(getLastEvent(wrapper, selected)).toBeNull()
    expect(dialog.vm.$props.display).toBe(false)
    expect(wrapper.vm.selected).toBeNull()
    wrapper.vm.selected = otherRegistration
    await flushPromises()
    dialog.vm.$emit('proceed', true)
    await flushPromises()
    expect(getLastEvent(wrapper, selected)).toStrictEqual(otherRegistration)
    expect(dialog.vm.$props.display).toBe(false)
  })
})
