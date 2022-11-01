import { useActions, useGetters } from 'vuex-composition-helpers'
import {
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeLocationIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationIF,
  NewMhrRegistrationApiIF,
  MhRegistrationSummaryIF,
  MhrDraftTransferApiIF
} from '@/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { APIMhrDescriptionTypes, APIStatusTypes, HomeTenancyTypes } from '@/enums'
import { getMhrDrafts, mhrRegistrationHistory } from '@/utils'
import { orderBy } from 'lodash'
export const useNewMhrRegistration = () => {
  const {
    getMhrRegistrationHomeDescription,
    getMhrRegistrationSubmittingParty,
    getMhrRegistrationDocumentId,
    getMhrAttentionReferenceNum,
    getMhrRegistrationLocation,
    getMhrRegistrationHomeOwnerGroups,
    getStaffPayment
  } = useGetters<any>([
    'getMhrRegistrationHomeDescription',
    'getMhrRegistrationSubmittingParty',
    'getMhrRegistrationDocumentId',
    'getMhrAttentionReferenceNum',
    'getMhrRegistrationLocation',
    'getMhrRegistrationHomeOwnerGroups',
    'getCertifyInformation',
    'getStaffPayment'
  ])
  const { setMhrTableHistory } = useActions<any>(['setMhrTableHistory'])

  const initNewMhr = (): MhrRegistrationIF => {
    return {
      documentId: '',
      clientReferenceId: '',
      declaredValue: '',
      submittingParty: {
        personName: {
          first: '',
          last: '',
          middle: ''
        },
        businessName: '',
        address: {
          street: '',
          city: '',
          region: '',
          country: '',
          postalCode: ''
        },
        emailAddress: '',
        phoneNumber: '',
        phoneExtension: ''
      },
      ownerGroups: [],
      attentionReferenceNum: '',
      location: {
        parkName: '',
        pad: '',
        address: {
          street: '',
          streetAdditional: '',
          city: '',
          region: '',
          country: '',
          postalCode: ''
        },
        leaveProvince: false,
        pidNumber: '',
        taxCertificate: false,
        dealerName: '',
        additionalDescription: '',
        locationType: null,
        otherType: null
      },
      description: {
        manufacturer: '',
        baseInformation: {
          year: null,
          circa: false,
          make: '',
          model: ''
        },
        sectionCount: null,
        sections: [],
        csaNumber: '',
        csaStandard: '',
        engineerName: '',
        engineerDate: '',
        certificationOption: null,
        rebuiltRemarks: '',
        otherRemarks: ''
      },
      notes: [
        {
          documentType: '',
          documentId: '',
          createDateTime: '',
          remarks: '',
          contactName: '',
          contactAddress: {
            street: '',
            city: '',
            region: '',
            postalCode: '',
            country: ''
          }
        }
      ]
    }
  }

  const parseSubmittingParty = () => {
    const submittingParty = cleanEmpty(getMhrRegistrationSubmittingParty.value)

    if (submittingParty.businessName) {
      delete submittingParty.personName
    }

    return submittingParty
  }

  const parseOwnerGroups = (): MhrRegistrationHomeOwnerGroupIF[] => {
    const ownerGroups: MhrRegistrationHomeOwnerGroupIF[] =
      Object.values(cleanEmpty(getMhrRegistrationHomeOwnerGroups.value))
    ownerGroups.forEach(ownerGroup => {
      ownerGroup.owners = Object.values(ownerGroup.owners)

      // @ts-ignore - TODO: Mhr-Submission - api asks for number, maybe fix this once step 3 is finished?
      ownerGroup.groupId = parseInt(ownerGroup.groupId)

      ownerGroup.type = Object.keys(HomeTenancyTypes).find(key => HomeTenancyTypes[key] as string === ownerGroup.type)
    })

    return ownerGroups
  }

  const parseDescription = (): MhrRegistrationDescriptionIF => {
    let description: MhrRegistrationDescriptionIF = getMhrRegistrationHomeDescription.value

    // Apply default manufacturer
    if (!description.manufacturer) {
      description.manufacturer = '*'
    }

    description = cleanEmpty(description)
    description.sections = Object.values(description.sections)
    description.sectionCount = description.sections.length
    return description
  }

  const parseLocation = (): MhrRegistrationHomeLocationIF => {
    const location: MhrRegistrationHomeLocationIF = cleanEmpty(getMhrRegistrationLocation.value)
    // location is always in BC
    location.address.country = 'CA'
    location.address.region = 'BC'

    // Work around require to satisfy schema validations. Currently, not collected by UI.
    location.address.postalCode = 'A1A 1A1'

    return location
  }

  // Staff Payment will be submitted as request parameters
  const parseStaffPayment = () => {
    const staffPayment = Object.create(cleanEmpty(getStaffPayment.value) as StaffPaymentIF)

    // do not need this in the request param
    delete staffPayment.option

    if (staffPayment.isPriority) {
      // change the key from isPriority to priority
      staffPayment.priority = staffPayment.isPriority
      delete staffPayment.isPriority
    }

    return staffPayment
  }

  const buildApiData = () => {
    const data: NewMhrRegistrationApiIF = {
      documentId: getMhrRegistrationDocumentId.value,
      submittingParty: parseSubmittingParty(),
      ownerGroups: parseOwnerGroups(),
      location: parseLocation(),
      description: parseDescription()
    }

    if (getMhrAttentionReferenceNum.value) {
      data.attentionReferenceNum = getMhrAttentionReferenceNum.value
    }

    return data
  }

  const fetchMhRegistrations = async (): Promise<void> => {
    const draftFilings = await getMhrDrafts()
    const myMhrHistory = await mhrRegistrationHistory()
    const filteredMhrHistory = addHistoryDraftsToMhr(myMhrHistory, draftFilings)
    setMhrTableHistory([...filteredMhrHistory])
  }

  function addHistoryDraftsToMhr (mhrHistory: MhRegistrationSummaryIF[], mhrDrafts: MhrDraftTransferApiIF[]):
    MhRegistrationSummaryIF[] {
    const sortedDraftFilings = orderBy(mhrDrafts, ['createDateTime'], ['desc'])

    const registerNewUnit = mhrHistory.filter(registrations =>
      registrations.registrationDescription === APIMhrDescriptionTypes.REGISTER_NEW_UNIT)
    const sortedMhrHistory = orderBy(registerNewUnit, ['createDateTime'], ['desc'])

    // add drafts to Registrations.
    sortedMhrHistory.forEach(transfer => {
      transfer.baseRegistrationNumber = transfer.mhrNumber
      var mhrDrafts = sortedDraftFilings.filter(sortedDrafts => sortedDrafts.mhrNumber === transfer.mhrNumber)
      if (mhrDrafts?.length > 0) {
        transfer.hasDraft = true
        transfer.changes = []
        mhrDrafts.forEach(draft => {
          const newDraft: MhRegistrationSummaryIF = {
            mhrNumber: transfer.mhrNumber,
            baseRegistrationNumber: transfer.mhrNumber,
            submittingParty: draft.submittingParty,
            clientReferenceId: transfer.clientReferenceId,
            createDateTime: draft.createDateTime,
            error: draft.error,
            registrationDescription: draft.registrationDescription,
            hasDraft: true,
            ownerNames: '',
            path: draft.path,
            statusType: APIStatusTypes.DRAFT,
            username: ''
          }
          transfer.changes.push(newDraft)
        })
      }
    })
    return sortedMhrHistory
  }
  /**
   * @function cleanEmpty
   *
   * Cleans the given object.
   * Deletes properties that has `null`, `undefined`, or `''` as values.
   *
   * @typeParam Type - type of object getting passed in
   * @param obj - The object to be cleaned up
   * @returns A new Object excluding `null`, `undefined`, or `''` values from the original Object.
   */
  function cleanEmpty<Type> (obj:Type): Type {
    const newObj = {}
    Object.keys(obj).forEach((key) => {
      if (obj[key] !== null && typeof obj[key] === 'object') { // getting deep into a nested object
        newObj[key] = cleanEmpty(obj[key])
      } else if (!!obj[key] || obj[key] === 0) { // add the key/value when it's not null, undefined, or empty string
        newObj[key] = obj[key]
      }
    })
    return newObj as Type
  }

  return {
    initNewMhr,
    buildApiData,
    parseStaffPayment,
    fetchMhRegistrations,
    cleanEmpty
  }
}
