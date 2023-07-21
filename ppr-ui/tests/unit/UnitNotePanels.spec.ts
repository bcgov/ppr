import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { UnitNoteContentInfo, UnitNoteHeaderInfo, UnitNotePanel, UnitNotePanels } from '../../src/components/unitNotes'
import { UnitNoteDocTypes, UnitNoteStatusTypes } from '../../src/enums'
import { mockUnitNotes } from './test-data'
import { BaseAddress } from '@/composables/address'
import { pacificDate } from '@/utils'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { UnitNoteIF } from '@/interfaces'

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

const verifyHeaderContent = (note: UnitNoteIF, header: Wrapper<any>) => {
  // Check the unit note type
  const typeText = header.find('h3').text()

  let statusText = ''
  if (note.status === UnitNoteStatusTypes.CANCELLED) {
    statusText = ' - Cancelled'
  } else if (note.status === UnitNoteStatusTypes.EXPIRED) {
    statusText = ' - Expired'
  }

  const expectedTypeText = (UnitNotesInfo[note.documentType]?.panelHeader ??
  UnitNotesInfo[note.documentType].header) + statusText
  expect(typeText).toBe(expectedTypeText)

  // Check the registration number and date
  const registrationInfo = header.find('.info-text')

  expect(registrationInfo.exists()).toBe(true)
  expect(registrationInfo.text()).toContain(`Registered on ${pacificDate(note.createDateTime, true)}`)
  expect(registrationInfo.text()).toContain(`Document Registration Number ${note.documentRegistrationNumber}`)
}

const verifyBodyContent = (note: UnitNoteIF, content: Wrapper<any>) => {
  // Check the effective date and time
  if (note.effectiveDateTime) {
    const effectiveDate = content.findAll('h3').at(0).text()
    const effectiveDateTime = content.findAll('.info-text.fs-14').at(0).text()
    expect(effectiveDate).toBe('Effective Date and Time')
    expect(effectiveDateTime).toBe(pacificDate(note.effectiveDateTime))
  }

  // Check the expiry date and time
  if (note.expiryDateTime) {
    const expiryDate = content.findAll('h3').at(1).text()
    const expiryDateTime = content.findAll('.info-text.fs-14').at(1).text()
    expect(expiryDate).toBe('Expiry Date and Time')
    expect(expiryDateTime).toBe(pacificDate(note.expiryDateTime))
  }

  // Check the remarks
  if (note.remarks) {
    const remarks = content.findAll('h3').at(2).text()
    const remarksText = content.findAll('.info-text.fs-14').at(2).text()
    expect(remarks).toBe('Remarks')
    expect(remarksText).toBe(note.remarks)
  }

  // Check the person giving notice table
  const noticeTable = content.find('#persons-giving-notice-table')
  expect(noticeTable.exists()).toBe(true)

  // Check the notice party data
  const noticeParty = note.givingNoticeParty
  if (noticeParty) {
    const noticePartyIcon = noticeTable.findComponent({ name: 'VIcon' })
    expect(noticePartyIcon.exists()).toBe(true)

    const mdiIconClass = Array.from(noticePartyIcon.element.classList)
      .find(className => className.startsWith('mdi-'))

    expect(mdiIconClass).toBe(content.vm.getNoticePartyIcon(noticeParty))

    const noticePartyName = noticeTable.find('.notice-party-name')
    expect(noticePartyName.exists()).toBe(true)
    expect(noticePartyName.text()).toContain(content.vm.getNoticePartyName(noticeParty))

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

    const unitNoteType = UnitNoteDocTypes.DECAL_REPLACEMENT
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

    // CONTINUED_NOTE_OF_CAUTION and EXTENSION_TO_NOTICE_OF_CAUTION are grouped per NOTICE_OF_CAUTION
    // Into a single panel so they should not be adding to the total number of panels.
    const expectedNumberOfPanels = mockUnitNotes.filter((note) => ![
      UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION,
      UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION
    ].includes(note.documentType)).length

    expect(panels.length).toBe(expectedNumberOfPanels)
  })

  it('calls cancelUnitNote when a unit note is cancelled', async () => {
    const wrapper = createComponent()
    const cancelUnitNoteMock = jest.fn()

    // Opens the drop down menu
    const panels = wrapper.findAll('.menu-drop-down-icon')
    await panels.at(0).trigger('click')
    await nextTick()

    const unitNotePanel = wrapper.findComponent(UnitNotePanel) as Wrapper<any>

    unitNotePanel.vm.cancelUnitNote = cancelUnitNoteMock
    const cancelUnitNoteItem = wrapper.findAll('.cancel-unit-note-list-item')
    await cancelUnitNoteItem.at(0).trigger('click')
    await nextTick()

    expect(cancelUnitNoteMock).toHaveBeenCalledWith(mockUnitNotes[0])
  })

  it('displays the unit note panels with the correct data', async () => {
    const wrapper: Wrapper<any> = createComponent()
    const panels = wrapper.findAll('.unit-note-panel')

    let noteIdx = 0
    let panelIdx = 0
    const additionalNoteIdx = []

    // Iterate over each unit note
    while (noteIdx < mockUnitNotes.length) {
      // If the note is not the primary note, it will be verified
      // when the primary note that its grouped with is verified.
      if (additionalNoteIdx.includes(noteIdx)) {
        noteIdx++
        continue
      }

      const note = mockUnitNotes[noteIdx]
      const panel = panels.at(panelIdx)

      // Check the panel header
      const header = panel.find('.v-expansion-panel-header')
      expect(header.exists()).toBe(true)

      verifyHeaderContent(note, header)

      // Check the panel actions
      const actions = header.find('.unit-note-header-action')
      expect(actions.exists()).toBe(true)

      // Expand panel
      const panelShowBtn = panel.find('.unit-note-menu-btn')
      await panelShowBtn.trigger('click')
      await nextTick()
      await nextTick()

      // Check the panel content
      const content = panel.findComponent(UnitNoteContentInfo)
      expect(content.exists()).toBe(true)

      verifyBodyContent(note, content)

      panelIdx++
      noteIdx++

      // Check the data for additionally grouped notes
      if ([UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION, UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION]
        .includes(note.documentType)) {
        // Verify additional grouped notes ending with the notice of caution
        let i = noteIdx
        let additionalNotePos = 1
        while (mockUnitNotes[i].documentType !== UnitNoteDocTypes.NOTICE_OF_CAUTION) {
          const additionalNote = mockUnitNotes[i]
          if ([UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION, UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION]
            .includes(additionalNote.documentType)) {
            additionalNoteIdx.push(i)
            const additionalHeader = panel.findAll(UnitNoteHeaderInfo).at(additionalNotePos)
            const additionalContent = panel.findAll(UnitNoteContentInfo).at(additionalNotePos)

            verifyHeaderContent(additionalNote, additionalHeader)
            verifyBodyContent(additionalNote, additionalContent)

            additionalNotePos++
          }
          i++
        }

        // Verify the notice of caution data
        additionalNoteIdx.push(i)
        const noticeOfCautionNote = mockUnitNotes[i]
        const noticeOfCautionHeader = panel.findAll(UnitNoteHeaderInfo).at(additionalNotePos)
        const noticeOfCautionContent = panel.findAll(UnitNoteContentInfo).at(additionalNotePos)

        verifyHeaderContent(noticeOfCautionNote, noticeOfCautionHeader)
        verifyBodyContent(noticeOfCautionNote, noticeOfCautionContent)
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

  it('displays continued and extension notice of caution buttons', async () => {
    const wrapper = createComponent()

    // Opens the drop down menu
    const panels = wrapper.findAll('.menu-drop-down-icon')
    // The first panel is a notice of caution
    await panels.at(0).trigger('click')
    await nextTick()

    const unitNotePanel = wrapper.findComponent(UnitNotePanel) as Wrapper<any>
    const buttons = unitNotePanel.findAll('.v-list-item')

    // Has 3 buttons: continued, extension, cancel
    expect(buttons.length).toBe(3)

    await buttons.at(0).trigger('click')
    await nextTick()

    expect(store.getMhrUnitNoteType).toBe(UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION)

    await buttons.at(1).trigger('click')
    await nextTick()

    expect(store.getMhrUnitNoteType).toBe(UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION)
  })
})
