import { UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums/unitNoteDocTypes'
import { CancelUnitNoteIF, PartyIF, UnitNoteIF, UnitNotePanelIF, UnitNoteRegistrationIF } from '@/interfaces'
import { useStore } from '@/store/store'
import { deleteEmptyProperties, submitMhrUnitNote } from '@/utils'
import { storeToRefs } from 'pinia'
import { cloneDeep } from 'lodash'
import { computed } from 'vue'
import { AdminRegistrationNotes, UnitNotesInfo } from '@/resources'
import { useNewMhrRegistration } from '../mhrRegistration'

export const useMhrUnitNote = () => {
  const {
    getMhrUnitNote,
    getMhrUnitNotes,
    getMhrUnitNoteType,
    getMhrInformation
  } = storeToRefs(useStore())

  const {
    setMhrUnitNoteRegistration
  } = useStore()

  const {
    parseStaffPayment
  } = useNewMhrRegistration()

  // Build Unit Note payload data with all the submission rules
  const buildPayload = (unitNoteData: UnitNoteRegistrationIF): UnitNoteRegistrationIF => {
    // Person Giving Notice is optional for Decal Replacement (102), Public Note (NPUB), Confidential Note (NCON)
    // The givingNoticeParty obj would be removed if it contains no data
    deleteEmptyProperties(unitNoteData)

    if (unitNoteData.note.additionalRemarks) {
      unitNoteData.note.remarks =
        unitNoteData.note.additionalRemarks + (unitNoteData.note.remarks ? `\n${unitNoteData.note.remarks}` : '')
      // don't submit additional remarks because it's included with regular remarks
      delete unitNoteData.note.additionalRemarks
    }

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

    // Remove the hasNoPersonGivingNotice flag as its not used by the API
    if (unitNoteData.note.hasNoPersonGivingNotice) {
      delete unitNoteData.note.hasNoPersonGivingNotice
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
    // determine if it's admin registration based on document type
    const isAdminRegistration = !!AdminRegistrationNotes.includes(unitNoteData.note.documentType)
    return submitMhrUnitNote(getMhrInformation.value.mhrNumber, payloadData, isAdminRegistration, parseStaffPayment())
  }

  // Make optional Person Giving Notice fields for certain Unit Note types
  const isPersonGivingNoticeOptional = (): boolean => {
    return [UnitNoteDocTypes.DECAL_REPLACEMENT,
      UnitNoteDocTypes.PUBLIC_NOTE,
      UnitNoteDocTypes.NOTE_CANCELLATION,
      UnitNoteDocTypes.CONFIDENTIAL_NOTE].includes(getMhrUnitNoteType.value)
  }

  // Effective Date Time component not required for certain Unit Note types
  const hasEffectiveDateTime = (): boolean => {
    return ![UnitNoteDocTypes.DECAL_REPLACEMENT, UnitNoteDocTypes.PUBLIC_NOTE, UnitNoteDocTypes.CONFIDENTIAL_NOTE]
      .includes(getMhrUnitNoteType.value) && !isCancelUnitNote.value && !isRedemptionUnitNote.value
  }

  const hasEffectiveDateInPanel = (note): boolean => {
    // show Effective Date for all notes except the following
    return ![
      UnitNoteDocTypes.PUBLIC_NOTE,
      UnitNoteDocTypes.CONFIDENTIAL_NOTE,
      UnitNoteDocTypes.DECAL_REPLACEMENT
    ].includes(note.documentType)
  }

  // Expiry Date Time component not required for certain Unit Note types
  const hasExpiryDate = (): boolean => {
    return [UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION, UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION]
      .includes(getMhrUnitNoteType.value)
  }

  const isCancelUnitNote = computed((): boolean => getMhrUnitNoteType.value === UnitNoteDocTypes.NOTE_CANCELLATION)

  // Check if the provided Unit Note's Expiry date passed today or not
  // parameter 'today' need to be in the format of 'YYYY-MM-DD'
  const isExpiryDatePassed = (note: UnitNoteIF, today: string): boolean => {
    if ((note.documentType === UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION ||
      note.documentType === UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION) &&
      !!note.expiryDateTime) {
      const expiryDate = note.expiryDateTime.substring(0, 10)
      return new Date(expiryDate) < new Date(today)
    }
    return false
  }

  const isRedemptionUnitNote = computed(
    (): boolean => getMhrUnitNoteType.value === UnitNoteDocTypes.NOTICE_OF_REDEMPTION
  )

  // Show the Note that's being cancelled in brackets, otherwise show empty string
  const getCancelledUnitNoteHeader = (): string => {
    const cancelledUnitNote: CancelUnitNoteIF = getMhrUnitNote.value as CancelUnitNoteIF
    return isCancelUnitNote.value
      ? '(' + UnitNotesInfo[cancelledUnitNote?.cancelledDocumentType]?.header + ')'
      : ''
  }

  // Pre-populate a Unit Note with other's Note info and optionally overwrite the documentType
  // Used for the Notes that cancel out other Notes (e.g. NRED that cancels TAXN)
  const prefillUnitNote = (note: UnitNoteIF, newNoteType: UnitNoteDocTypes = null): UnitNoteIF => {
    const unitNote = {} as UnitNoteIF
    Object.assign(unitNote, note)

    // overwrite unit note type
    newNoteType && (unitNote.documentType = newNoteType)
    unitNote.documentId = ''
    unitNote.destroyed = false

    setMhrUnitNoteRegistration({ key: 'updateDocumentId', value: note.documentId })
    setMhrUnitNoteRegistration({ key: 'documentType', value: newNoteType })
    setMhrUnitNoteRegistration({ key: 'submittingParty', value: null })

    delete unitNote.documentDescription
    delete unitNote.documentRegistrationNumber
    delete unitNote.status
    delete unitNote.createDateTime

    return unitNote
  }

  // Used in Unit Note panels, add Redemption Note info to the cancelled Tax Sale note
  // Cancelled Tax Sale note has Redemption's Cancelled Date, Remarks and Person Giving Notice info
  const addRedemptionNoteInfo = (taxSaleNote: UnitNoteIF): UnitNoteIF => {
    const updatedTaxSaleNote: UnitNotePanelIF = cloneDeep(taxSaleNote)
    const redemptionNote = (getMhrUnitNotes.value as Array<CancelUnitNoteIF>).find((note: CancelUnitNoteIF) =>
      note.documentType === UnitNoteDocTypes.NOTICE_OF_REDEMPTION &&
      note.status === UnitNoteStatusTypes.ACTIVE &&
      note.cancelledDocumentRegistrationNumber === taxSaleNote.documentRegistrationNumber
    )

    updatedTaxSaleNote.cancelledDateTime = redemptionNote?.createDateTime
    updatedTaxSaleNote.remarks = redemptionNote?.remarks
    updatedTaxSaleNote.givingNoticeParty = redemptionNote?.givingNoticeParty

    return updatedTaxSaleNote
  }

  // Init a Cancel Unit Note from reg Unit Note
  const initCancelUnitNote = (note: UnitNoteIF): CancelUnitNoteIF => {
    const cancelUniNote = {} as CancelUnitNoteIF
    Object.assign(cancelUniNote, note)

    cancelUniNote.cancelledDocumentType = note.documentType
    cancelUniNote.cancelledDocumentDescription = note.documentDescription
    cancelUniNote.cancelledDocumentRegistrationNumber = note.documentRegistrationNumber
    cancelUniNote.documentType = UnitNoteDocTypes.NOTE_CANCELLATION
    cancelUniNote.documentId = ''
    cancelUniNote.destroyed = false
    cancelUniNote.hasNoPersonGivingNotice = note.givingNoticeParty ? false : true

    setMhrUnitNoteRegistration({ key: 'cancelDocumentId', value: note.documentId })
    setMhrUnitNoteRegistration({ key: 'submittingParty', value: null })
    setMhrUnitNoteRegistration({ key: 'documentType', value: UnitNoteDocTypes.NOTE_CANCELLATION })

    delete cancelUniNote.documentDescription
    delete cancelUniNote.documentRegistrationNumber
    delete cancelUniNote.status
    delete cancelUniNote.createDateTime

    return cancelUniNote
  }

  const initEmptyUnitNote = (): UnitNoteRegistrationIF => {
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
        additionalRemarks: '',
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
        hasNoPersonGivingNotice: false, // local property not sent to API
        destroyed: false
      }
    }
  }

  return {
    initEmptyUnitNote,
    initCancelUnitNote,
    prefillUnitNote,
    isCancelUnitNote,
    isRedemptionUnitNote,
    isExpiryDatePassed,
    getCancelledUnitNoteHeader,
    buildApiDataAndSubmit,
    isPersonGivingNoticeOptional,
    hasEffectiveDateTime,
    hasEffectiveDateInPanel,
    hasExpiryDate,
    addRedemptionNoteInfo
  }
}
