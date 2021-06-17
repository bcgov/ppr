// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedSecuredParties1,
  mockedSecuredParties2
} from './test-data'

// Components
import { SecuredParties, EditParty } from '@/components/parties'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<Debtors> object with the given parameters.
 */
function createComponent (
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(SecuredParties, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Secured Party SA tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditParty).exists()).toBeFalsy()
  })
})

describe('Secured Party store tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      securedParties: mockedSecuredParties1
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders secured party table and headers', async () => {
    expect(wrapper.find('.party-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.text-start').length).toBe(5)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row').length

    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('SECURED PARTY COMPANY LTD.')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[2].textContent).toContain('test@company.com')
  })
})
