import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import {
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeLocationIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationIF,
  MhrLocationInfoIF,
  NewMhrRegistrationApiIF,
  MhRegistrationSummaryIF,
  RegistrationSortIF,
  MhrDraftIF
} from '@/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { APIMhrTypes, HomeTenancyTypes, HomeLocationTypes, MhApiStatusTypes } from '@/enums'
import { createMhrDraft, getMhrDrafts, mhrRegistrationHistory, updateMhrDraft } from '@/utils'
import { orderBy } from 'lodash'
import { useHomeOwners } from '@/composables'

export const useNewMhrRegistration = () => {
  const {
    // Actions
    setMhrLocation,
    setMhrDraftNumber,
    setMhrTableHistory,
    setMhrHomeDescription,
    setMhrAttentionReferenceNum,
    setMhrRegistrationDocumentId,
    setMhrRegistrationSubmittingParty,
    setMhrRegistrationHomeOwnerGroups,
    setMhrRegistrationOwnLand
  } = useStore()
  const {
    // Getters
    isRoleStaffReg,
    getMhrRegistrationHomeDescription,
    getMhrRegistrationSubmittingParty,
    getMhrRegistrationDocumentId,
    getMhrAttentionReferenceNum,
    getMhrRegistrationLocation,
    getMhrRegistrationHomeOwnerGroups,
    getMhrRegistrationOwnLand,
    getStaffPayment,
    getMhrDraftNumber
  } = storeToRefs(useStore())
  const {
    setShowGroups,
    getHomeTenancyType
  } = useHomeOwners()

  const initNewMhr = (): MhrRegistrationIF => {
    return {
      draftNumber: '',
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
      attentionReference: '',
      isManualLocationInfo: false,
      ownLand: false,
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
        otherType: null,
        legalDescription: '',
        lot: '',
        parcel: '',
        block: '',
        districtLot: '',
        partOf: '',
        section: '',
        township: '',
        range: '',
        meridian: '',
        landDistrict: '',
        plan: '',
        bandName: '',
        reserveNumber: '',
        exceptionPlan: ''
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
      }
    }
  }

  /**
   * Parse a draft MHR into State.
   * @param draft The draft filing to parse.
   */
  const initDraftMhr = async (draft: MhrRegistrationIF): Promise<void> => {
    // Set description
    for (const [key, val] of Object.entries(initNewMhr().description)) {
      draft.description[key]
        ? setMhrHomeDescription({ key: key, value: draft.description[key] })
        : setMhrHomeDescription({ key: key, value: val }) // set missing description values to default
    }
    // Set Submitting Party
    setMhrRegistrationSubmittingParty(draft.submittingParty)
    // Set Document Id
    setMhrRegistrationDocumentId(draft.documentId)
    // Set Land Ownership
    setMhrRegistrationOwnLand(draft.ownLand)
    // Set attention
    setMhrAttentionReferenceNum(draft.attentionReference)
    // Set HomeOwners
    setMhrRegistrationHomeOwnerGroups(draft.ownerGroups)
    // Show groups for Tenants in Common
    setShowGroups(getHomeTenancyType() === HomeTenancyTypes.COMMON)
    // Set Home Location
    for (const [key, val] of Object.entries(draft.location)) {
      setMhrLocation({ key: key, value: val })

      // Map radio button options for Other Land Types
      if (
        [HomeLocationTypes.OTHER_RESERVE, HomeLocationTypes.OTHER_STRATA, HomeLocationTypes.OTHER_TYPE].includes(val)
      ) {
        setMhrLocation({ key: 'otherType', value: val })
        setMhrLocation({ key: 'locationType', value: HomeLocationTypes.OTHER_LAND })
      }
    }
  }

  const resetLocationInfoFields = (location: MhrLocationInfoIF): MhrLocationInfoIF => {
    Object.entries(location).forEach(([key]) => {
      location[key] = ''
    })
    return location
  }

  const parseSubmittingParty = () => {
    const submittingParty = cleanEmpty(getMhrRegistrationSubmittingParty.value)

    if (submittingParty.businessName) {
      delete submittingParty.personName
    }

    return submittingParty
  }

  const parseOwnerGroups = (): MhrRegistrationHomeOwnerGroupIF[] => {
    const ownersGroups: MhrRegistrationHomeOwnerGroupIF[] =
      getMhrRegistrationHomeOwnerGroups.value.map(group => {
        group.owners.forEach(owner => {
          owner.description = owner.suffix
        })

        return group
      })

    const parsedOwnerGroups = Object.values(cleanEmpty(ownersGroups))
    parsedOwnerGroups.forEach((ownerGroup: MhrRegistrationHomeOwnerGroupIF) => {
      ownerGroup.owners = Object.values(ownerGroup.owners)

      // @ts-ignore - TODO: Mhr-Submission - api asks for number, maybe fix this once step 3 is finished?
      ownerGroup.groupId = parseInt(ownerGroup.groupId)

      ownerGroup.type = Object.keys(HomeTenancyTypes).find(key => HomeTenancyTypes[key] as string === ownerGroup.type)
    })

    return parsedOwnerGroups
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

    // otherType is not required by API and locationType should have otherType's value (#14751)
    if (location.otherType) {
      location.locationType = location.otherType
      const { otherType, ...parsedLocation } = location
      return parsedLocation
    }

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

  const buildApiData = (): NewMhrRegistrationApiIF => {
    const data: NewMhrRegistrationApiIF = {
      documentId: getMhrRegistrationDocumentId.value,
      ownLand: getMhrRegistrationOwnLand.value,
      submittingParty: parseSubmittingParty(),
      ownerGroups: parseOwnerGroups(),
      location: parseLocation(),
      description: parseDescription(),
      ...(isRoleStaffReg.value && !!getStaffPayment.value && {
        clientReferenceId: getStaffPayment.value.folioNumber
      })
    }

    if (getMhrAttentionReferenceNum.value) {
      data.attentionReference = getMhrAttentionReferenceNum.value
    }

    if (getMhrDraftNumber.value) {
      data.draftNumber = getMhrDraftNumber.value
    }

    return data
  }

  const fetchMhRegistrations = async (sortOptions: RegistrationSortIF = null): Promise<void> => {
    const draftFilings = await getMhrDrafts()
    const myMhrHistory = await mhrRegistrationHistory(true, sortOptions)
    const filteredMhrHistory = addHistoryDraftsToMhr(myMhrHistory, draftFilings, sortOptions)
    setMhrTableHistory(filteredMhrHistory)
  }

  const mhrDraftHandler = async (): Promise<MhrDraftIF> => {
    const draft = getMhrDraftNumber.value
      ? await updateMhrDraft(getMhrDraftNumber.value, APIMhrTypes.MANUFACTURED_HOME_REGISTRATION, buildApiData())
      : await createMhrDraft(APIMhrTypes.MANUFACTURED_HOME_REGISTRATION, buildApiData())

    // Set draftNumber to state to prevent duplicate drafts
    if (draft) setMhrDraftNumber(draft.draftNumber)

    return draft
  }

  function addHistoryDraftsToMhr (
    mhrHistory: MhRegistrationSummaryIF[],
    mhrDrafts: MhrDraftIF[],
    sortOptions: RegistrationSortIF = null):
    MhRegistrationSummaryIF[] {
    let mhrTableData = []
    // Collect MH Transfer and Registration Drafts
    const sortedDraftFilings = orderBy(mhrDrafts, ['createDateTime'], ['desc'])
    let mhRegDrafts = []

    if (!sortOptions?.status || sortOptions?.status === MhApiStatusTypes.DRAFT) {
      mhRegDrafts = mhrDrafts.filter(draft =>
        !draft.mhrNumber && draft.registrationType === APIMhrTypes.MANUFACTURED_HOME_REGISTRATION
      )
    }

    // add Transfer drafts to parent registrations.
    mhrHistory.forEach(transfer => {
      transfer.baseRegistrationNumber = transfer.mhrNumber

      // Prepare existing changes
      const existingChanges = []
      if (transfer.changes) {
        transfer.changes.forEach(transferChanges => {
          const newDraft: MhRegistrationSummaryIF = transferChanges
          newDraft.baseRegistrationNumber = transferChanges.mhrNumber
          newDraft.documentId = transferChanges.documentId
          newDraft.draftNumber = transferChanges.documentRegistrationNumber
          existingChanges.push(newDraft)
        })
        transfer.changes = existingChanges
      }

      const mhrDrafts = sortedDraftFilings.filter(sortedDrafts => sortedDrafts.mhrNumber === transfer.mhrNumber)
      if (mhrDrafts?.length > 0) {
        transfer.hasDraft = true
        if (!transfer.changes) transfer.changes = []
        mhrDrafts.forEach(draft => {
          const newDraft: MhRegistrationSummaryIF = {
            mhrNumber: transfer.mhrNumber,
            baseRegistrationNumber: transfer.mhrNumber,
            draftNumber: draft.draftNumber,
            submittingParty: draft.submittingParty,
            clientReferenceId: transfer.clientReferenceId,
            createDateTime: draft.createDateTime,
            error: draft.error,
            registrationDescription: draft.registrationDescription,
            hasDraft: false,
            ownerNames: '',
            path: draft.path,
            statusType: MhApiStatusTypes.DRAFT,
            username: '',
            documentId: draft.draftNumber
          }
          if (sortOptions?.status === MhApiStatusTypes.DRAFT) {
            mhrTableData.push(newDraft)
          } else {
            transfer.changes.push(newDraft)
          }
        })
        transfer.changes = orderBy(transfer.changes, ['createDateTime'], ['desc'])
      }
    })
    if (sortOptions?.status !== MhApiStatusTypes.DRAFT) mhrTableData = mhrHistory
    return [...mhRegDrafts, ...mhrTableData]
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
    initDraftMhr,
    mhrDraftHandler,
    resetLocationInfoFields,
    buildApiData,
    parseStaffPayment,
    fetchMhRegistrations,
    cleanEmpty
  }
}
