import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { UnitNotePanels } from '../../src/components/unitNotes'
import { UnitNoteDocTypes } from '../../src/enums'
import { mockUnitNotes } from './test-data'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount((UnitNotePanels as any), {
    localVue,
    store,
    vuetify,
	  propsData: { unitNotes: mockUnitNotes, disabled: false }
  })
}

describe('UnitNotePanels', () => {
  it('renders the component', () => {
    const wrapper = createComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('displays the "Add Unit Notes" button', () => {
    const wrapper = createComponent()
    const addButton = wrapper.find('#open-unit-notes-btn')
    expect(addButton.exists()).toBe(true)
    expect(addButton.text()).toBe('Add Unit Notes')
  })

  it('emits the correct event when a unit note is initialized', async () => {
    const wrapper = createComponent()
    const addButton = wrapper.find('#open-unit-notes-btn')
    addButton.trigger('click')
    await nextTick()

    const unitNoteType = UnitNoteDocTypes.NOTICE_OF_CAUTION
    const initUnitNoteMock = jest.fn()
    wrapper.vm.initUnitNote = initUnitNoteMock

    const unitNoteItem = wrapper.find('.unit-note-list-item')
    unitNoteItem.trigger('click')
    await nextTick()

    expect(initUnitNoteMock).toHaveBeenCalledWith(unitNoteType)
  })

  it('renders the correct number of unit note panels', () => {
    const wrapper = createComponent()
	  const panels = wrapper.findAll('.unit-note-panel')

    expect(panels.length).toBe(mockUnitNotes.length)
  })

  it('calls cancelUnitNote when a unit note is cancelled', async () => {
    const wrapper = createComponent()
	  const cancelUnitNoteMock = jest.fn()

	  const panels = wrapper.findAll('.menu-drop-down-icon')
	  await panels.at(0).trigger('click')
	  await nextTick()

    wrapper.vm.cancelUnitNote = cancelUnitNoteMock
    const cancelUnitNoteItem = wrapper.findAll('.cancel-unit-note-list-item')
    await cancelUnitNoteItem.at(0).trigger('click')
	  await nextTick()

	  expect(cancelUnitNoteMock).toHaveBeenCalledWith(mockUnitNotes[0])
  })
})
