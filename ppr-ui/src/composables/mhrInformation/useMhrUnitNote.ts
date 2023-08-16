import { UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums/unitNoteDocTypes'
import { GroupedNotesIF, PartyIF, UnitNoteIF, UnitNoteRegistrationIF } from '@/interfaces'
import { useStore } from '@/store/store'
import { deleteEmptyProperties, submitMhrUnitNote } from '@/utils'
import { storeToRefs } from 'pinia'
import { cloneDeep } from 'lodash'
import { CancellableUnitNoteTypes, NoticeOfCautionDropDown } from '@/resources'

export const useMhrUnitNote = () => {
  const {
    getMhrUnitNoteType,
    getMhrInformation
  } = storeToRefs(useStore())

  // Build Unit Note payload data with all the submission rules
  const buildPayload = (unitNoteData: UnitNoteRegistrationIF): UnitNoteRegistrationIF => {
    // Person Giving Notice is optional for Decal Replacement (102), Public Note (NPUB), Confidential Note (NCON)
    // The givingNoticeParty obj would be removed if it contains no date
    deleteEmptyProperties(unitNoteData)

    if (unitNoteData.note.givingNoticeParty?.phoneNumber) {
      unitNoteData.note.givingNoticeParty.phoneNumber = unitNoteData.note.givingNoticeParty?.phoneNumber?.replace(/[^A-Z0-9]/ig, '')
    }

    if (unitNoteData.submittingParty.phoneNumber) {
      unitNoteData.submittingParty.phoneNumber = unitNoteData.submittingParty.phoneNumber?.replace(/[^A-Z0-9]/ig, '')
    }

    // Remove the hasUsedPartyLookup flag from submittingParty as its not used by the API
    if (unitNoteData.submittingParty.hasUsedPartyLookup) {
      delete unitNoteData.submittingParty.hasUsedPartyLookup
    }

    // status is not required
    delete unitNoteData.note.status

    // Unit note expiryDateTime can only be submitted for CAUC(optional), CAUE
    if (hasExpiryDate() && !!unitNoteData.note.expiryDateTime) {
      unitNoteData.note.expiryDateTime = unitNoteData.note.expiryDateTime.replace('Z', '')
    } else {
      delete unitNoteData.note.expiryDateTime
    }

    // Do not submit effectiveDateTime if form does not show the component (REG_102, NPUB)
    if (hasEffectiveDateTime() && !!unitNoteData.note.effectiveDateTime) {
      // cleanup dateTime to be accepted by API
      unitNoteData.note.effectiveDateTime = unitNoteData.note.effectiveDateTime.replace('Z', '')
    } else {
      delete unitNoteData.note.effectiveDateTime
    }

    return unitNoteData
  }

  // Submit Unit Note after building the payload data
  const buildApiDataAndSubmit = (unitNoteData: UnitNoteRegistrationIF) => {
    const payloadData = buildPayload(cloneDeep(unitNoteData))
    return submitMhrUnitNote(getMhrInformation.value.mhrNumber, payloadData)
  }

  // Make optional Person Giving Notice fields for certain Unit Note types
  const isPersonGivingNoticeOptional = (): boolean => {
    return [UnitNoteDocTypes.DECAL_REPLACEMENT,
      UnitNoteDocTypes.PUBLIC_NOTE,
      UnitNoteDocTypes.CONFIDENTIAL_NOTE].includes(getMhrUnitNoteType.value)
  }

  // Effective Date Time component not required for certain Unit Note types
  const hasEffectiveDateTime = (): boolean => {
    return ![UnitNoteDocTypes.DECAL_REPLACEMENT, UnitNoteDocTypes.PUBLIC_NOTE].includes(getMhrUnitNoteType.value)
  }

  // Expiry Date Time component not required for certain Unit Note types
  const hasExpiryDate = (): boolean => {
    return [UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION, UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION]
      .includes(getMhrUnitNoteType.value)
  }

  // Identify if a unit note is notice of caution or an extended/continued notice of caution
  const isNoticeOfCautionOrRelatedDocType = (note: UnitNoteIF): boolean => {
    return [UnitNoteDocTypes.NOTICE_OF_CAUTION,
      UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION,
      UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION].includes(note.documentType)
  }

  // Groups unit notes for the panels
  const groupUnitNotes = (unitNotes: UnitNoteIF[]): GroupedNotesIF[] => {
    // The notes should already be in order by creation date and time (filter preserves order)
    const noticeOfCautionNotes = unitNotes.filter((note) => isNoticeOfCautionOrRelatedDocType(note))

    let primaryUnitNote: UnitNoteIF = null
    let additionalUnitNotes: UnitNoteIF[] = []

    const groupedNoticeOfCautions: GroupedNotesIF[] = []

    // NOTICE_OF_CAUTION is used as an interval for grouping the notes
    // When a NOTICE_OF_CAUTION is encountered, the group is added
    // and a new group is started on the next iteration
    noticeOfCautionNotes.forEach((note) => {
      if (!primaryUnitNote) { primaryUnitNote = note } else { additionalUnitNotes.push(note) }

      if (note.documentType === UnitNoteDocTypes.NOTICE_OF_CAUTION) {
        groupedNoticeOfCautions.push({ primaryUnitNote, additionalUnitNotes })
        primaryUnitNote = null
        additionalUnitNotes = []
      }
    })

    const nonNoticeOfCautionUnitNotes = unitNotes.filter((note) => !isNoticeOfCautionOrRelatedDocType(note))

    const groupedUnitNotes: GroupedNotesIF[] = nonNoticeOfCautionUnitNotes.map((note) => {
      return { primaryUnitNote: note }
    })

    // Adds the notice of caution notes to the other unit notes and sort in descending creation time
    return groupedUnitNotes.concat(groupedNoticeOfCautions).sort((note1, note2) =>
      new Date(note2.primaryUnitNote.createDateTime).getTime() -
       new Date(note1.primaryUnitNote.createDateTime).getTime()
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

    return options
  }

  const initUnitNote = (): UnitNoteRegistrationIF => {
    return {
      clientReferenceId: '',
      attentionReference: '',
      submittingParty: {
        personName: {
          first: '',
          last: '',
          middle: ''
        },
        businessName: '',
        address: {
          street: '',
          streetAdditional: '',
          city: '',
          region: '',
          country: '',
          postalCode: ''
        },
        emailAddress: '',
        phoneNumber: '',
        phoneExtension: ''
      },
      note: {
        documentType: null,
        documentId: '',
        documentRegistrationNumber: '',
        documentDescription: '',
        createDateTime: '',
        effectiveDateTime: '',
        expiryDateTime: '',
        status: UnitNoteStatusTypes.ACTIVE,
        remarks: '',
        givingNoticeParty: {
          businessName: '',
          personName: {
            first: '',
            last: '',
            middle: ''
          },
          address: {
            street: '',
            streetAdditional: '',
            city: '',
            region: '',
            country: '',
            postalCode: ''
          },
          emailAddress: '',
          phoneNumber: ''
        } as PartyIF,
        destroyed: false
      }
    }
  }

  return {
    initUnitNote,
    buildApiDataAndSubmit,
    isPersonGivingNoticeOptional,
    hasEffectiveDateTime,
    hasExpiryDate,
    getNoteOptions,
    groupUnitNotes,
    isNoticeOfCautionOrRelatedDocType
  }
}
