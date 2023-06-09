import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { UnitNotePanels } from '../../src/components/unitNotes'
import { UnitNoteDocTypes } from '../../src/enums'
import { mockUnitNotes } from './test-data'
import { BaseAddress } from '@/composables/address'
import { pacificDate } from '@/utils'

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
    propsData: {
      unitNotes: mockUnitNotes,
      disabled: false
    }
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

  it('displays the unit note panels with the correct data', async () => {
    const wrapper: Wrapper<any> = createComponent()
    const panels = wrapper.findAll('.unit-note-panel')

    // Iterate over each unit note panel
    for (let i = 0; i < mockUnitNotes.length; i++) {
      const item = mockUnitNotes[i]
      const panel = panels.at(i)

      // Check the panel header
      const header = panel.find('.v-expansion-panel-header')
      expect(header.exists()).toBe(true)

      // Check the unit note type
      const typeText = header.find('h3').text()
      expect(typeText).toContain(wrapper.vm.getUnitNoteText(item.documentType))

      // Check the registration number and date
      const registrationInfo = header.find('.info-text')
      expect(registrationInfo.exists()).toBe(true)
      expect(registrationInfo.text()).toContain(`Registered on ${pacificDate(item.createDateTime)}`)
      expect(registrationInfo.text()).toContain(`Document Registration Number ${item.documentRegistrationNumber}`)

      // Check the panel actions
      const actions = header.find('.unit-note-header-action')
      expect(actions.exists()).toBe(true)

      // Expand panel
      const panelShowBtn = panel.find('.unit-note-menu-btn')
      await panelShowBtn.trigger('click')
      await nextTick()
      await nextTick()

      // Check the panel content
      const content = panel.find('.v-expansion-panel-content')
      expect(content.exists()).toBe(true)

      // Check the effective date and time
      if (item.effectiveDateTime) {
        const effectiveDate = content.findAll('h3').at(0).text()
        const effectiveDateTime = content.findAll('.info-text.fs-14').at(0).text()
        expect(effectiveDate).toBe('Effective Date and Time')
        expect(effectiveDateTime).toBe(pacificDate(item.effectiveDateTime))
      }

      // Check the expiry date and time
      if (item.expiryDateTime) {
        const expiryDate = content.findAll('h3').at(1).text()
        const expiryDateTime = content.findAll('.info-text.fs-14').at(1).text()
        expect(expiryDate).toBe('Expiry Date and Time')
        expect(expiryDateTime).toBe(pacificDate(item.expiryDateTime))
      }

      // Check the remarks
      if (item.remarks) {
        const remarks = content.findAll('h3').at(2).text()
        const remarksText = content.findAll('.info-text.fs-14').at(2).text()
        expect(remarks).toBe('Remarks')
        expect(remarksText).toBe(item.remarks)
      }

      // Check the person giving notice table
      const noticeTable = content.find('#persons-giving-notice-table')
      expect(noticeTable.exists()).toBe(true)

      // Check the notice party data
      const noticeParty = item.givingNoticeParty
      if (noticeParty) {
        const noticePartyIcon = noticeTable.findComponent({ name: 'VIcon' })
        expect(noticePartyIcon.exists()).toBe(true)

        const mdiIconClass = Array.from(noticePartyIcon.element.classList)
          .find(className => className.startsWith('mdi-'))
        expect(mdiIconClass).toBe(wrapper.vm.getNoticePartyIcon(noticeParty))

        const noticePartyName = noticeTable.find('.notice-party-name')
        expect(noticePartyName.exists()).toBe(true)
        expect(noticePartyName.text()).toContain(wrapper.vm.getNoticePartyName(noticeParty))

        // Check the notice party address, email, and phone number
        const noticePartyAddress = noticeTable.findComponent(BaseAddress)
        expect(noticePartyAddress.exists()).toBe(true)
        expect(noticePartyAddress.props('value')).toBe(noticeParty.address)

        const noticePartyEmail = noticeTable.find('td:nth-child(3)')
        expect(noticePartyEmail.exists()).toBe(true)
        expect(noticePartyEmail.text()).toBe(noticeParty.emailAddress)

        const noticePartyPhone = noticeTable.find('td:nth-child(4)')
        expect(noticePartyPhone.exists()).toBe(true)
        expect(noticePartyPhone.text()).toBe(noticeParty.phoneNumber)
      }
    }
  })

  it('displays the empty notes message when no unit notes are available', async () => {
    const wrapper = createComponent()
    wrapper.setData({ unitNotes: [] })
    await nextTick()

    const emptyMsg = wrapper.find('.empty-notes-msg')
    expect(emptyMsg.exists()).toBe(true)
    expect(emptyMsg.text()).toBe('A unit note has not been filed for this manufactured home.')
  })
})
