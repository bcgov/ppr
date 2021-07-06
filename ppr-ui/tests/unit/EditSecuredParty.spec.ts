// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import flushPromises from 'flush-promises'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { mockedSecuredParties1, mockedSecuredParties2 } from './test-data'

// Components
import { EditParty } from '@/components/parties'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn'
const cancelButtonSelector: string = '#cancel-btn'
const removeButtonSelector: string = '#remove-btn'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  activeIndex: Number,
  invalidSection: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(EditParty, {
    localVue,
    propsData: { activeIndex, invalidSection },
    store,
    vuetify
  })
}

describe('Secured Party add individual tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(-1, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditParty).exists()).toBe(true)
    // radio button value is blank
    expect(wrapper.vm.partyBusiness).toBe('')
  })

  it('shows buttons on the form and remove button is disabled', async () => {
    expect(wrapper.find(doneButtonSelector).exists()).toBe(true)
    expect(wrapper.find(cancelButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).attributes('disabled')).toBe(
      'disabled'
    )
  })

  it('adds a secured party to the store', async () => {
    const radioInput = wrapper.findAll('input[type="radio"]')
    const radioIsIndividual = radioInput.at(0)

    await radioIsIndividual.trigger('click')
    wrapper.find('#txt-first').setValue('JOE')
    wrapper.find('#txt-last').setValue('SCHMOE')
    wrapper.find('#txt-email').setValue('joe@apples.com')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()

    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(
      store.getters.getAddSecuredPartiesAndDebtors.securedParties.length
    ).toBe(1)
  })
})

describe('Secured Party add business tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(-1, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditParty).exists()).toBe(true)
    expect(wrapper.vm.currentSecuredParty.businessName).toBe('')
  })

  it('adds a secured party business to the store', async () => {
    const radioInput = wrapper.findAll('input[type="radio"]')
    const radioIsBusiness = radioInput.at(1)

    await radioIsBusiness.trigger('click')
    await Vue.nextTick()
    wrapper.find('#txt-name').setValue('TONYS TOOLS')
    await Vue.nextTick()
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()
    
    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(
      store.getters.getAddSecuredPartiesAndDebtors.securedParties[1]
        .businessName
    ).toBe('TONYS TOOLS')
  })
})

describe('Secured Party edit individual tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      securedParties: mockedSecuredParties2
    })
    wrapper = createComponent(0, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders secured party when editing', async () => {
    expect(wrapper.findComponent(EditParty).exists()).toBe(true)
    expect(wrapper.vm.currentSecuredParty.personName.first).toEqual('TEST')
    expect(wrapper.vm.currentSecuredParty.personName.last).toEqual(
      'INDIVIDUAL PARTY'
    )
    expect(wrapper.vm.currentSecuredParty.emailAddress).toEqual(
      'test@person.com'
    )
  })

  it('Emits reset event', async () => {
    wrapper.find(cancelButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.emitted().resetEvent).toBeTruthy()
  })
})
