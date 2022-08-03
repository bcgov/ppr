import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

import { HomeOwners } from '@/views'
import {
  AddEditHomeOwner,
  HomeOwnersTable
} from '@/components/mhrRegistration/HomeOwners'
import { mockedHomeSections } from './test-data/mock-home-sections'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

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
  return mount(HomeOwners, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Home Owners', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders Home Owners and its sub components', () => {
    expect(wrapper.findComponent(HomeOwners).exists()).toBe(true)
    // expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBe(false) // Hidden by default
    // expect(wrapper.findComponent(HomeOwnersTable).exists()).toBe(true)
  })
})
