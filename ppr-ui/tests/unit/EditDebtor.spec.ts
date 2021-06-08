// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import flushPromises from 'flush-promises'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedDebtors1,
  mockedDebtors2
} from './test-data'

// Components
import { EditDebtor } from '@/components/parties'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn'
const cancelButtonSelector: string = '#cancel-btn'
const removeButtonSelector: string = '#remove-btn'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent(
  activeIndex: Number,
  isBusiness: boolean,
  invalidSection: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(EditDebtor, {
    localVue,
    propsData: { activeIndex, isBusiness, invalidSection },
    store,
    vuetify
  })
}

describe('Debtor add individual tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(-1, false, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditDebtor).exists()).toBe(true)
    expect(wrapper.vm.currentDebtor.personName.first).toBe('')
  })

  it('shows buttons on the form and remove button is disabled', async () => {
    expect(wrapper.find(doneButtonSelector).exists()).toBe(true)
    expect(wrapper.find(cancelButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).exists()).toBe(true)
    expect(wrapper.find(removeButtonSelector).attributes('disabled')).toBe('disabled')
  })

  it('adds a debtor to the store', async () => {
    wrapper.find('#txt-first').setValue('JOE')
    wrapper.find('#txt-last').setValue('SCHMOE')
    wrapper.find('#txt-month').setValue(6)
    wrapper.find('#txt-day').setValue('25')
    wrapper.find('#txt-year').setValue(1980)
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()

    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(store.getters.getAddSecuredPartiesAndDebtors.debtors.length).toBe(1)
  })
})

describe('Debtor add business tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent(-1, true, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(EditDebtor).exists()).toBe(true)
    expect(wrapper.vm.currentDebtor.businessName).toBe('')
  })

  it('adds a debtor to the store', async () => {
    wrapper.find('#txt-name').setValue('TONYS TOOLS')
    wrapper.find(doneButtonSelector).trigger('click')
    await flushPromises()

    expect(wrapper.emitted().resetEvent).toBeTruthy()
    // store should have 1 item now
    expect(store.getters.getAddSecuredPartiesAndDebtors.debtors[1].businessName).toBe('TONYS TOOLS')
  })
})

describe('Debtor edit individual tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      debtors: mockedDebtors1
    })
    wrapper = createComponent(0, false, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders debtor when editing', async () => {
    expect(wrapper.findComponent(EditDebtor).exists()).toBe(true)
    expect(wrapper.vm.currentDebtor.personName.first).toEqual('TEST')
    expect(wrapper.vm.currentDebtor.personName.last).toEqual('INDIVIDUAL DEBTOR')
    expect(wrapper.vm.currentDebtor.birthDate).toEqual('1990-06-15T16:42:00-08:00')
  })

  it('Emits reset event', async () => {
    wrapper.find(cancelButtonSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.emitted().resetEvent).toBeTruthy()
  })
})

describe('Debtor edit business tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      debtors: mockedDebtors2
    })
    wrapper = createComponent(0, true, false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders debtor when editing', async () => {
    expect(wrapper.findComponent(EditDebtor).exists()).toBe(true)
    expect(wrapper.vm.currentDebtor.businessName).toEqual('SOMEBODYS BUSINESS')
  })
})
