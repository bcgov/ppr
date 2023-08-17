import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { UnitNoteContentInfo, UnitNoteHeaderInfo, UnitNotePanel, UnitNotePanels } from '../../src/components/unitNotes'
import { UnitNoteDocTypes, UnitNoteStatusTypes } from '../../src/enums'
import { mockUnitNotes, mockedUnitNotes2, mockedUnitNotes3, mockedUnitNotes4 } from './test-data'
import { BaseAddress } from '@/composables/address'
import { pacificDate } from '@/utils'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { UnitNoteIF } from '@/interfaces'
import { getTestId } from './utils'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (otherMockNotes?: UnitNoteIF[]): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount((UnitNotePanels as any), {
    localVue,
    store,
    vuetify,
    propsData: {
      unitNotes: otherMockNotes ?? mockUnitNotes,
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
  let headerIndex = 0
  if (note.effectiveDateTime) {
    const effectiveDate = content.findAll('h3').at(headerIndex).text()
    const effectiveDateTime = content.findAll('.info-text.fs-14').at(headerIndex).text()
    expect(effectiveDate).toBe('Effective Date and Time')
    expect(effectiveDateTime).toBe(pacificDate(note.effectiveDateTime, true))
    headerIndex++
  }

  // Check the expiry date and time
  if (note.expiryDateTime) {
    const expiryDate = content.findAll('h3').at(headerIndex).text()
    const expiryDateTime = content.findAll('.info-text.fs-14').at(headerIndex).text()
    expect(expiryDate).toBe('Expiry Date and Time')
    expect(expiryDateTime).toBe(pacificDate(note.expiryDateTime, true))
    headerIndex++
  }

  // Check the remarks
  if (note.remarks) {
    const remarks = content.findAll('h3').at(headerIndex).text()
    const remarksText = content.findAll('.info-text.fs-14').at(headerIndex).text()
    expect(remarks).toBe('Remarks')
    expect(remarksText).toBe(note.remarks)
    headerIndex++
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

  it('calls handleOptionSelection when a unit note cancel option is clicked', async () => {
    const wrapper = createComponent()
    const handleOptionSelection = jest.fn()

    // Opens the drop down menu
    const panels = wrapper.findAll('.menu-drop-down-icon')
    await panels.at(0).trigger('click')
    await nextTick()

    const unitNotePanel = wrapper.findComponent(UnitNotePanel) as Wrapper<any>

    unitNotePanel.vm.handleOptionSelection = handleOptionSelection
    const cancelUnitNoteOption = unitNotePanel.find(getTestId(`unit-note-option-${UnitNoteDocTypes.NOTE_CANCELLATION}`))
    await cancelUnitNoteOption.trigger('click')
    await nextTick()

    expect(handleOptionSelection).toHaveBeenCalledWith(UnitNoteDocTypes.NOTE_CANCELLATION, mockUnitNotes[0])
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

  it('displays the cancel unit note option for cancellable unit notes', async () => {
    const wrapper = createComponent(mockedUnitNotes2)
    const panels = wrapper.findAll('.unit-note-panel')

    // First panel is an active public note
    const panel = panels.at(0)
    const header = panel.find('.v-expansion-panel-header')
    const headerText = header.find('h3').text()

    expect(headerText).toBe('Public Note')

    // Opens the drop down menu
    panel.find('.menu-drop-down-icon').trigger('click')
    await nextTick()
    const buttons = panel.findAll('.v-list-item')
    expect(buttons.length).toBe(1)
    expect(buttons.at(0).text()).toBe('Cancel Note')

    // Second panel is a cancelled public note (no drop down menu)
    const panel2 = panels.at(1)
    const header2 = panel2.find('.v-expansion-panel-header')
    const headerText2 = header2.find('h3').text()

    expect(headerText2).toBe('Public Note - Cancelled')

    // No dropdown menu
    expect(panel2.find('.menu-drop-down-icon').exists()).toBe(false)

    // Third panel is a decal replacement note (no drop down menu)
    const panel3 = panels.at(2)
    const header3 = panel3.find('.v-expansion-panel-header')
    const headerText3 = header3.find('h3').text()

    expect(headerText3).toBe('Decal Replacement')

    // No dropdown menu
    expect(panel3.find('.menu-drop-down-icon').exists()).toBe(false)
  })

  it('displays the correct text when there is no person giving notice', async () => {
    const wrapper = createComponent(mockedUnitNotes3)
    // First panel is an active public note with no person giving notice
    const panel = wrapper.find('.unit-note-panel')

    // Expand panel
    const panelShowBtn = panel.find('.unit-note-menu-btn')
    await panelShowBtn.trigger('click')
    await nextTick()

    // Check the panel content
    const content = panel.findComponent(UnitNoteContentInfo)
    expect(content.exists()).toBe(true)

    expect(content.find('#persons-giving-notice-table').exists()).toBe(false)
    expect(content.find('#no-person-giving-notice').exists()).toBe(true)
  })

  it('displays the correctly when a continued notice of caution is filled with no expiry date', async () => {
    const wrapper = createComponent(mockedUnitNotes4)
    // An active continued notice of caution with no expiry date
    const panel = wrapper.find('.unit-note-panel')

    // Expand panel
    const panelShowBtn = panel.find('.unit-note-menu-btn')
    await panelShowBtn.trigger('click')
    await nextTick()

    // Check the panel content
    const content = panel.findComponent(UnitNoteContentInfo)
    expect(content.exists()).toBe(true)

    expect(content.find('#no-expiry').text()).toBe('N/A')
  })
})
