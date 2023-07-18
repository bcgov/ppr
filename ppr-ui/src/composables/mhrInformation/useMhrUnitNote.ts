import { UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums/unitNoteDocTypes'
import { PartyIF, UnitNoteRegistrationIF } from '@/interfaces'
import { useStore } from '@/store/store'
import { deleteEmptyProperties, submitMhrUnitNote } from '@/utils'
import { storeToRefs } from 'pinia'

export const useMhrUnitNote = (unitNoteType: UnitNoteDocTypes) => {
  const {
    getMhrInformation
  } = storeToRefs(useStore())

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

  // Build Unit Note payload data with all the submission rules
  const buildPayload = (unitNoteData: UnitNoteRegistrationIF): UnitNoteRegistrationIF => {
    deleteEmptyProperties(unitNoteData)

    if (!unitNoteData.attentionReference) {
      unitNoteData.attentionReference = unitNoteData.submittingParty.businessName
        ? unitNoteData.submittingParty.businessName
        : [unitNoteData.submittingParty.personName.first,
          (unitNoteData.submittingParty.personName.middle || null),
          unitNoteData.submittingParty.personName.last].join(' ')
    }

    if (unitNoteData.note.givingNoticeParty?.phoneNumber) {
      unitNoteData.note.givingNoticeParty.phoneNumber = unitNoteData.note.givingNoticeParty?.phoneNumber?.replace(/[^A-Z0-9]/ig, '')
    }

    if (unitNoteData.submittingParty.phoneNumber) {
      unitNoteData.submittingParty.phoneNumber = unitNoteData.submittingParty.phoneNumber?.replace(/[^A-Z0-9]/ig, '')
    }

    // status is not required
    delete unitNoteData.note.status
    unitNoteData.note.effectiveDateTime = unitNoteData.note.effectiveDateTime.replace('Z', '')

    // Unit note expiryDateTime can only be submitted for CAUC, CAUE
    if (![UnitNoteDocTypes.CONTINUED_NOTE_OF_CAUTION,
      UnitNoteDocTypes.EXTENSION_TO_NOTICE_OF_CAUTION].includes(unitNoteType)) {
      delete unitNoteData.note.expiryDateTime
    } else {
      unitNoteData.note.expiryDateTime = unitNoteData.note.expiryDateTime.replace('Z', '')
    }

    return unitNoteData
  }

  // Submit Unit Note after building the payload data
  const buildApiDataAndSubmit = (unitNoteData: UnitNoteRegistrationIF) => {
    const payloadData = buildPayload(unitNoteData)
    return submitMhrUnitNote(getMhrInformation.value.mhrNumber, payloadData)
  }

  return {
    initUnitNote,
    buildApiDataAndSubmit
  }
}
