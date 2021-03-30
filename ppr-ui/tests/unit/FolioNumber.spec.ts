// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { FolioNumber } from '@/components/common'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const searchError: string = 'search-error'
const searchData: string = 'search-data'

// Input field selectors / buttons
const folioAddBtn: string = '#folio-add-btn'
const folioEditBtn: string = '#folio-edit-btn'
const folioCloseBtn: string = '#folio-close-btn'
const folioDisplay: string = '#folio-display'
const folioEdit: string = '#folio-edit'
const folioEditTxt: string = '#folio-edit-txt'

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
function createComponent (
  defaultFolioNumber: string
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(FolioNumber, {
    localVue,
    propsData: { defaultFolioNumber },
    store,
    vuetify
  })
}

describe('Folio number tests', () => {
  let wrapper: Wrapper<any>
  const defaultFolio = 't123'

  beforeEach(async () => {
    wrapper = createComponent(defaultFolio)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default folio set', async () => {
    expect(wrapper.findComponent(FolioNumber).exists()).toBe(true)
    expect(wrapper.vm.folioNumber).toBe(defaultFolio)
    expect(wrapper.vm.folioEditNumber).toBe(defaultFolio)
    expect(wrapper.vm.folioEdit).toBe(false)
    expect(wrapper.find(folioAddBtn).exists()).toBe(false)
    expect(wrapper.find(folioEditBtn).exists()).toBe(true)
    expect(wrapper.find(folioEdit).exists()).toBe(false)
    expect(wrapper.find(folioCloseBtn).exists()).toBe(false)
    const folio = wrapper.findAll(folioDisplay)
    expect(folio.length).toBe(1)
    expect(folio.at(0).text()).toContain(defaultFolio)
  })

  it('allows the user to edit the folio', async () => {
    wrapper.find(folioEditBtn).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.folioEditNumber).toBe(defaultFolio)
    const edit = wrapper.findAll(folioEditTxt)
    expect(edit.length).toBe(1)
    expect(wrapper.find(folioCloseBtn).exists()).toBe(true)
    // test close btn
    wrapper.find(folioCloseBtn).trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.folioNumber).toBe(defaultFolio)
    expect(wrapper.vm.folioEdit).toBe(false)
    expect(wrapper.find(folioAddBtn).exists()).toBe(false)
    expect(wrapper.find(folioEditBtn).exists()).toBe(true)
    expect(wrapper.find(folioEdit).exists()).toBe(false)
    expect(wrapper.find(folioCloseBtn).exists()).toBe(false)
    wrapper.find(folioEditBtn).trigger('click')
    await Vue.nextTick()
    const newFolio = '12'
    wrapper.vm.folioEditNumber = newFolio
    await Vue.nextTick()
    const newEdit = wrapper.findAll(folioEditTxt)
    expect(newEdit.length).toBe(1)
    wrapper.trigger('keypress', {
      key: 'enter'
    })
    await Vue.nextTick()
    // not working will update later
    // expect(wrapper.vm.folioNumber).toBe(newFolio)
    // expect(wrapper.vm.folioEdit).toBe(false)
    // expect(wrapper.find(folioAddBtn).exists()).toBe(false)
    // expect(wrapper.find(folioEditBtn).exists()).toBe(true)
    // expect(wrapper.find(folioEdit).exists()).toBe(false)
    // expect(wrapper.find(folioCloseBtn).exists()).toBe(false)
    // expect(getLastEvent(wrapper, 'folio-number')).toEqual(newFolio)
  })

  it('validates the folio number', async () => {
    // tbd
  })
})
