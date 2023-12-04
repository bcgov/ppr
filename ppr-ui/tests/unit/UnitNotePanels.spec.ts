import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { UnitNoteContentInfo, UnitNoteHeaderInfo, UnitNotePanel, UnitNotePanels } from '../../src/components/unitNotes'
import { AuthRoles, ProductCode, UnitNoteDocTypes, UnitNoteStatusTypes } from '../../src/enums'
import {
  mockedCancelledTaxSaleNote,
  mockedNoticeOfRedemption,
  mockedResidentialExemptionOrder,
  mockedUnitNotes,
  mockedUnitNotes2,
  mockedUnitNotes3,
  mockedUnitNotes4,
  mockedUnitNotes5,
  mockedUnitNotesCancelled
} from './test-data'
import { BaseAddress } from '@/composables/address'
import { localTodayDate, pacificDate, shortPacificDate } from '@/utils'
import {
  ResidentialExemptionQSDropDown,
  ResidentialExemptionStaffDropDown,
  UnitNotesInfo,
  cancelledWithRedemptionNote
} from '@/resources/unitNotes'
import { CancelUnitNoteIF, UnitNoteIF, UnitNotePanelIF } from '@/interfaces'
import { getTestId } from './utils'
import { useMhrUnitNote } from '@/composables'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (otherMockNotes?: Array<UnitNoteIF | CancelUnitNoteIF>): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount((UnitNotePanels as any), {
    localVue,
    store,
    vuetify,
    propsData: {
      unitNotes: otherMockNotes ?? mockedUnitNotes,
      disabled: false
    }
  })
}

const verifyHeaderContent = (note: UnitNotePanelIF, header: Wrapper<any>) => {
  // Check the unit note type
  const typeText = header.find('h3').text()
  const today = localTodayDate()
  let statusText = ''
  if (note.status === UnitNoteStatusTypes.EXPIRED ||
      useMhrUnitNote().isExpiryDatePassed(note, today)) {
    statusText = ' (Expired)'
  } else if (note.status === UnitNoteStatusTypes.CANCELLED) {
    statusText = ' (Cancelled)'
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

const verifyBodyContent = (note: UnitNotePanelIF, content: Wrapper<any>, cancelNote?: CancelUnitNoteIF) => {
  // Check the effective date
  // For some of the Notes it does not show up in the panel
  let headerIndex = 0
  if (note.effectiveDateTime) {
    if (useMhrUnitNote().hasEffectiveDateInPanel(note)) {
      expect(content.find(getTestId('effective-date-info')).exists()).toBeTruthy()
      const effectiveDate = content.findAll('h3').at(headerIndex).text()
      const effectiveDateTime = content.findAll('.info-text.fs-14').at(headerIndex).text()
      expect(effectiveDate).toBe('Effective Date')
      expect(effectiveDateTime).toBe(shortPacificDate(note.effectiveDateTime))
      headerIndex++
    } else {
      expect(content.find(getTestId('effective-date-info')).exists()).toBeFalsy()
    }
  }

  // Check the expiry date and time
  if (note.expiryDateTime) {
    const expiryDate = content.findAll('h3').at(headerIndex).text()
    const expiryDateTime = content.findAll('.info-text.fs-14').at(headerIndex).text()
    expect(expiryDate).toBe('Expiry Date')
    expect(expiryDateTime).toBe(shortPacificDate(note.expiryDateTime))
    headerIndex++
  }

  if (note.cancelledDateTime) {
    const cancelledDate = content.findAll('h3').at(headerIndex).text()
    const cancelledDateTime = content.findAll('.info-text.fs-14').at(headerIndex).text()
    expect(cancelledDate).toBe('Cancelled Date and Time')
    expect(cancelledDateTime).toBe(pacificDate(cancelNote.createDateTime, true))
    headerIndex++
  }

  // Check the remarks
  if (note.remarks || cancelNote?.remarks) {
    const remarks = content.findAll('h3').at(headerIndex).text()
    const remarksText = content.findAll('.info-text.fs-14').at(headerIndex).text()
    expect(remarks).toBe('Remarks')
    expect(remarksText).toBe(cancelNote?.remarks || note.remarks)
    headerIndex++
  }

  // Check the person giving notice table
  const noticeTable = content.find('#persons-giving-notice-table')
  expect(noticeTable.exists()).toBe(true)

  // Check the notice party data
  const noticeParty = cancelNote?.givingNoticeParty ? note.givingNoticeParty : cancelNote?.givingNoticeParty
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
    expect(noticePartyEmail.text()).toBe(noticeParty.emailAddress || '(Not Entered)')

    const noticePartyPhone = noticeTable.find('td:nth-child(4)')
    expect(noticePartyPhone.exists()).toBe(true)
    expect(noticePartyPhone.text()).toBe(noticeParty.phoneNumber || '(Not Entered)')
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
    const expectedNumberOfPanels = mockedUnitNotes.filter((note) => ![
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

    expect(handleOptionSelection).toHaveBeenCalledWith(UnitNoteDocTypes.NOTE_CANCELLATION, mockedUnitNotes[0])
  })

  it('calls handleOptionSelection when File Notice of Redemption option is clicked', async () => {
    const wrapper = createComponent(mockedUnitNotes5)
    const handleOptionSelection = jest.fn()

    // Opens the drop down menu
    const panels = wrapper.findAll('.menu-drop-down-icon')
    await panels.at(0).trigger('click')
    await nextTick()

    const unitNotePanel = wrapper.findComponent(UnitNotePanel) as Wrapper<any>

    unitNotePanel.vm.handleOptionSelection = handleOptionSelection
    const noticeOfRedemptionOption = unitNotePanel.find(
      getTestId(`unit-note-option-${UnitNoteDocTypes.NOTICE_OF_REDEMPTION}`)
    )
    await noticeOfRedemptionOption.trigger('click')
    await nextTick()

    expect(handleOptionSelection).toHaveBeenCalledWith(UnitNoteDocTypes.NOTICE_OF_REDEMPTION, mockedUnitNotes5[0])
  })

  it('displays the unit note panels with the correct data', async () => {
    const wrapper: Wrapper<any> = createComponent()
    const panels = wrapper.findAll('.unit-note-panel')

    let noteIdx = 0
    let panelIdx = 0
    const additionalNoteIdx = []

    // Iterate over each unit note
    while (noteIdx < mockedUnitNotes.length) {
      // If the note is not the primary note, it will be verified
      // when the primary note that its grouped with is verified.
      if (additionalNoteIdx.includes(noteIdx)) {
        noteIdx++
        continue
      }

      const note = mockedUnitNotes[noteIdx]
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
        while (mockedUnitNotes[i].documentType !== UnitNoteDocTypes.NOTICE_OF_CAUTION) {
          const additionalNote = mockedUnitNotes[i]
          if ([UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION, UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION]
            .includes(additionalNote.documentType)) {
            additionalNoteIdx.push(i)
            const additionalHeader = panel.findAllComponents(UnitNoteHeaderInfo).at(additionalNotePos)
            const additionalContent = panel.findAllComponents(UnitNoteContentInfo).at(additionalNotePos)

            verifyHeaderContent(additionalNote, additionalHeader)
            verifyBodyContent(additionalNote, additionalContent)

            additionalNotePos++
          }
          i++
        }

        // Verify the notice of caution data
        additionalNoteIdx.push(i)
        const noticeOfCautionNote = mockedUnitNotes[i]
        const noticeOfCautionHeader = panel.findAllComponents(UnitNoteHeaderInfo).at(additionalNotePos)
        const noticeOfCautionContent = panel.findAllComponents(UnitNoteContentInfo).at(additionalNotePos)

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
    expect(emptyMsg.text()).toBe('A Unit Note has not been filed for this manufactured home.')
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

    expect(headerText2).toBe('Public Note (Cancelled)')

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
    expect(content.find('#separated-remarks').text()).toContain('Continued until further order of the court.\n')
  })

  it('correctly displays a cancelled unit note panel', async () => {
    const wrapper = createComponent(mockedUnitNotesCancelled)
    const panel = wrapper.find('.unit-note-panel')
    const note = mockedUnitNotesCancelled.find((note) => note.status === UnitNoteStatusTypes.CANCELLED)
    const cancellingNote = mockedUnitNotesCancelled
      .find((cancelNote) => note.documentRegistrationNumber ===
      (cancelNote as CancelUnitNoteIF)?.cancelledDocumentRegistrationNumber)

    // Check the panel header
    const header = panel.find('.v-expansion-panel-header')
    expect(header.exists()).toBe(true)

    verifyHeaderContent(note, header)

    // Check that there is no drop down menu
    expect(panel.find('.menu-drop-down-icon').exists()).toBe(false)

    // Expand panel
    const panelShowBtn = panel.find('.unit-note-menu-btn')
    await panelShowBtn.trigger('click')
    await nextTick()
    await nextTick()

    // Check the panel content
    const content = panel.findComponent(UnitNoteContentInfo)
    expect(content.exists()).toBe(true)

    verifyBodyContent(note, content, cancellingNote as CancelUnitNoteIF)
  })

  it('should not show Notice of Redemptions unit notes', async () => {
    const mixedNotes: UnitNoteIF[] =
      [...mockedUnitNotes2, mockedNoticeOfRedemption, ...mockedUnitNotes3, mockedCancelledTaxSaleNote]

    const wrapper = createComponent(mixedNotes)
    const panels = wrapper.findAllComponents(UnitNotePanel)

    expect(panels).toHaveLength(mixedNotes.length - 1)

    const cancelledTaxNotePanel = panels.filter(
      panel => panel.find('h3').text().includes(cancelledWithRedemptionNote)
    ).at(0)

    expect(cancelledTaxNotePanel.exists()).toBeTruthy()
    expect(cancelledTaxNotePanel.text()).toContain(
      `${UnitNotesInfo[UnitNoteDocTypes.NOTICE_OF_TAX_SALE].header} ${cancelledWithRedemptionNote}`
    )
  })

  it('should show correct view for Staff and QS for Residential Exemption note', async () => {
    const mixedNotes: UnitNoteIF[] =
    [...mockedUnitNotes4, mockedResidentialExemptionOrder]

    let wrapper = createComponent(mixedNotes)
    wrapper.setProps({ hasActiveExemption: true })

    // set Qualified Supplier role
    await store.setAuthRoles([AuthRoles.MHR_TRANSFER_SALE])
    await store.setUserProductSubscriptionsCodes([ProductCode.MANUFACTURER])

    wrapper.find('#open-unit-notes-btn').trigger('click')
    await nextTick()

    // check dropdown for Qualified Supplier
    expect(wrapper.vm.addUnitNoteDropdown).toBe(ResidentialExemptionQSDropDown)

    // set Staff role
    await store.setAuthRoles([AuthRoles.STAFF, AuthRoles.PPR_STAFF])

    wrapper = createComponent(mixedNotes)
    wrapper.setProps({ hasActiveExemption: true })

    wrapper.find('#open-unit-notes-btn').trigger('click')
    await nextTick()
    await nextTick()

    // check dropdown for Staff
    expect(wrapper.vm.addUnitNoteDropdown).toBe(ResidentialExemptionStaffDropDown)

    const resExemptionPanel = wrapper.findAllComponents(UnitNotePanel).at(1)
    expect(resExemptionPanel.find('h3').text()).toBe(UnitNotesInfo[UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER].header)

    // expand Res Exemption panel
    resExemptionPanel.find('.unit-note-menu-btn').trigger('click')
    await nextTick()
    await nextTick()

    const resExemptionContentInfo = resExemptionPanel.findComponent(UnitNoteContentInfo)

    // check visible and hidden sections of the panel info
    expect(resExemptionContentInfo.find(getTestId('effective-date-info')).exists()).toBe(false)
    expect(resExemptionContentInfo.find(getTestId('remarks-info')).exists()).toBe(true)
    expect(resExemptionContentInfo.find(getTestId('person-giving-notice-info')).exists()).toBe(false)
  })
})
