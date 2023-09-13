import { UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums/unitNoteDocTypes'
import { CancelUnitNoteIF, UnitNoteIF, UnitNotePanelIF } from '@/interfaces'
import { CancellableUnitNoteTypes, NoticeOfCautionDropDown, NoticeOfTaxSaleDropDown } from '@/resources'

/**
 * Contains logic specific to rendering the unit note panels
*/
export const useMhrUnitNotePanel = () => {
  /**
   * Adds details to unit notes based on cancel notes and remove cancelled notes
   * @param unitNotes
   * @returns UnitNoteIF
   */

  // Identify if a unit note is notice of caution or an extended/continued notice of caution
  const isNoticeOfCautionOrRelatedDocType = (note: UnitNoteIF): boolean => {
    return [UnitNoteDocTypes.NOTICE_OF_CAUTION,
      UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION,
      UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION].includes(note.documentType)
  }

  const handleCancelledUnitNotes = (unitNotes: UnitNoteIF[]): UnitNotePanelIF[] => {
    // Uses the cancelledDocumentRegistrationNumber to map a unit note to its cancel note
    const cancelUnitNotesMap = new Map<string, CancelUnitNoteIF>()

    // Since notes are in order from most recent creation date and time,
    // the cancel notes should be added to map before the corresponding note is encountered
    unitNotes.forEach((note: UnitNotePanelIF) => {
      if (note.documentType === UnitNoteDocTypes.NOTE_CANCELLATION) {
        cancelUnitNotesMap.set((note as CancelUnitNoteIF).cancelledDocumentRegistrationNumber, note as CancelUnitNoteIF)
      } else if (cancelUnitNotesMap.has(note.documentRegistrationNumber)) {
        // Adds cancelledDateTime and overrides remarks and givingNoticeParty
        const cancelNote = cancelUnitNotesMap.get(note.documentRegistrationNumber)
        note.remarks = cancelNote.remarks
        note.cancelledDateTime = cancelNote.createDateTime
        note.givingNoticeParty = cancelNote.givingNoticeParty
      }
    })

    // Removes the cancel notes from the unit notes
    return unitNotes.filter((note) => note.documentType !== UnitNoteDocTypes.NOTE_CANCELLATION) as UnitNotePanelIF[]
  }

  /**
   * Groups the notice of caution notes for the panels
   * @param unitNotes
   * @returns GroupedNotesIF[]
   */
  const handleNoticeOfCautionNotes = (unitNotes: UnitNotePanelIF[]): UnitNotePanelIF[] => {
    // The notes should already be in order by creation date and time (filter preserves order)
    const noticeOfCautionNotes = unitNotes.filter((note) => isNoticeOfCautionOrRelatedDocType(note))

    let primaryUnitNote: UnitNotePanelIF = null
    let additionalUnitNotes: UnitNotePanelIF[] = []

    const groupedNoticeOfCautionNotes: UnitNotePanelIF[] = []

    // NOTICE_OF_CAUTION is used as an interval for grouping the notes
    // When a NOTICE_OF_CAUTION is encountered, the group is added
    // and a new group is started on the next iteration
    noticeOfCautionNotes.forEach((note) => {
      if (!primaryUnitNote) { primaryUnitNote = note } else { additionalUnitNotes.push(note) }

      if (note.documentType === UnitNoteDocTypes.NOTICE_OF_CAUTION) {
        primaryUnitNote.additionalUnitNotes = additionalUnitNotes
        groupedNoticeOfCautionNotes.push(primaryUnitNote)
        primaryUnitNote = null
        additionalUnitNotes = []
      }
    })

    return groupedNoticeOfCautionNotes
  }

  // Takes a set of unit notes and applies UI changes to enable rendering of panels
  const createPanelUnitNotes = (unitNotes: UnitNoteIF[]): UnitNotePanelIF[] => {
    // Adds details to unit notes based on cancel notes and remove cancelled notes
    const panelUnitNotes = handleCancelledUnitNotes(unitNotes)
    const groupedNoticeOfCautions: UnitNotePanelIF[] = handleNoticeOfCautionNotes(panelUnitNotes)

    const nonNoticeOfCautionUnitNotes = panelUnitNotes.filter(
      // Notice of Redemption notes are not displayed in panels
      note => !isNoticeOfCautionOrRelatedDocType(note) && note.documentType !== UnitNoteDocTypes.NOTICE_OF_REDEMPTION
    )

    // Adds the notice of caution notes to the other unit notes and sort in descending creation time
    return nonNoticeOfCautionUnitNotes.concat(groupedNoticeOfCautions).sort((note1, note2) =>
      new Date(note2.createDateTime).getTime() -
       new Date(note1.createDateTime).getTime()
    )
  }

  // Provides document types based on the given unit note that configure the unit note dropdown options
  const getNoteOptions = (unitNote: UnitNoteIF): UnitNoteDocTypes[] => {
    const options = []

    if (unitNote.status === UnitNoteStatusTypes.CANCELLED) {
      return options
    }

    if (isNoticeOfCautionOrRelatedDocType(unitNote)) {
      options.push(...NoticeOfCautionDropDown)
    }

    if (CancellableUnitNoteTypes.includes(unitNote.documentType)) {
      options.push(UnitNoteDocTypes.NOTE_CANCELLATION)
    }

    if (unitNote.documentType === UnitNoteDocTypes.NOTICE_OF_TAX_SALE) {
      options.push(...NoticeOfTaxSaleDropDown)
    }

    return options
  }

  return {
    createPanelUnitNotes,
    getNoteOptions,
    isNoticeOfCautionOrRelatedDocType
  }
}
