// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedDebtors1,
  mockedDebtors2
} from './test-data'

// Components
import { Debtors, EditDebtor } from '@/components/parties'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons
const addIndividualSelector: string = '#btn-add-individual'
const addBusinessSelector: string = '#btn-add-business'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<Debtors> object with the given parameters.
 */
function createComponent(
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(Debtors, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Debtor SA tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(Debtors).exists()).toBe(true)
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditDebtor).exists()).toBeFalsy()
  })

  it('add debtor button shows the add form', async () => {
    expect(wrapper.find(addIndividualSelector).exists()).toBe(true)
    expect(wrapper.find(addBusinessSelector).exists()).toBe(true)
    wrapper.find(addIndividualSelector).trigger('click')
    await Vue.nextTick()
    expect(wrapper.findComponent(EditDebtor).exists()).toBeTruthy()
    expect(wrapper.findComponent(EditDebtor).isVisible()).toBe(true)
  })
})

describe('Collateral store tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      debtors: mockedDebtors1
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders debtor table and headers', async () => {
    expect(wrapper.find('.debtor-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.text-start').length).toBe(4)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .debtor-row').length

    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .debtor-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('TEST INDIVIDUAL DEBTOR')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[2].textContent).toContain('June 15, 1990')

  })
})
