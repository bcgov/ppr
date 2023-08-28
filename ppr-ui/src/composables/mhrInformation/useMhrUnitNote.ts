import { UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums/unitNoteDocTypes'
import { PartyIF, UnitNoteRegistrationIF } from '@/interfaces'
import { useStore } from '@/store/store'
import { deleteEmptyProperties, submitMhrUnitNote } from '@/utils'
import { storeToRefs } from 'pinia'
import { cloneDeep } from 'lodash'

export const useMhrUnitNote = () => {
  const {
    getMhrUnitNoteType,
    getMhrInformation
  } = storeToRefs(useStore())

  // Build Unit Note payload data with all the submission rules
  const buildPayload = (unitNoteData: UnitNoteRegistrationIF): UnitNoteRegistrationIF => {
    // Person Giving Notice is optional for Decal Replacement (102), Public Note (NPUB), Confidential Note (NCON)
    // The givingNoticeParty obj would be removed if it contains no data
    deleteEmptyProperties(unitNoteData)

    if (unitNoteData.note.additionalRemarks) {
      unitNoteData.note.remarks = unitNoteData.note.additionalRemarks + ' ' + unitNoteData.note.remarks
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
    return ![UnitNoteDocTypes.DECAL_REPLACEMENT, UnitNoteDocTypes.PUBLIC_NOTE, UnitNoteDocTypes.CONFIDENTIAL_NOTE]
      .includes(getMhrUnitNoteType.value)
  }

  // Expiry Date Time component not required for certain Unit Note types
  const hasExpiryDate = (): boolean => {
    return [UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION, UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION]
      .includes(getMhrUnitNoteType.value)
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
    initUnitNote,
    buildApiDataAndSubmit,
    isPersonGivingNoticeOptional,
    hasEffectiveDateTime,
    hasExpiryDate
  }
}
