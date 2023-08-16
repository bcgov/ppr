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
import { APIMhrTypes, HomeTenancyTypes, HomeLocationTypes, MhApiStatusTypes, HomeCertificationOptions } from '@/enums'
import {
  cleanEmpty,
  createMhrDraft,
  fromDisplayPhone,
  getMhrDrafts,
  getMhrManufacturerInfo,
  mhrRegistrationHistory,
  updateMhrDraft
} from '@/utils'
import { orderBy } from 'lodash'
import { useHomeOwners } from '@/composables'

export const useNewMhrRegistration = () => {
  const {
    // Actions
    setFolioOrReferenceNumber,
    setMhrLocation,
    setMhrDraftNumber,
    setMhrTableHistory,
    setMhrHomeDescription,
    setMhrAttentionReference,
    setMhrRegistrationDocumentId,
    setMhrRegistrationSubmittingParty,
    setMhrRegistrationHomeOwnerGroups,
    setMhrRegistrationOwnLand
  } = useStore()
  const {
    // Getters
    isRoleStaffReg,
    isMhrManufacturerRegistration,
    getFolioOrReferenceNumber,
    getMhrRegistrationHomeDescription,
    getMhrRegistrationSubmittingParty,
    getMhrRegistrationDocumentId,
    getMhrAttentionReference,
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
        hasNoCertification: null,
        rebuiltRemarks: '',
        otherRemarks: ''
      }
    }
  }

  const initNewManufacturerMhr = async (): Promise<void> => {
    const data = await getMhrManufacturerInfo()
    setMhrHomeDescription({ key: 'manufacturer', value: data.description.manufacturer })
    setMhrHomeDescription({ key: 'certificationOption', value: HomeCertificationOptions.CSA })

    // Add id to owners to ensure home owners table functionality works.
    let defaultID = 1
    data.ownerGroups.forEach((group: MhrRegistrationHomeOwnerGroupIF) => {
      group.owners.forEach((owner) => { owner.ownerId = defaultID++ })
    })

    setMhrRegistrationHomeOwnerGroups(data.ownerGroups)
    for (const [key, val] of Object.entries(data.location)) {
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
    setMhrAttentionReference(draft.attentionReference)
    // Set folio or reference number
    setFolioOrReferenceNumber(draft.clientReferenceId)
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
    let submittingParty = cleanEmpty(getMhrRegistrationSubmittingParty.value)

    if (submittingParty.businessName) {
      delete submittingParty.personName
    }
    // Format phone numbers to digits only for submission
    if (submittingParty.phoneNumber) {
      submittingParty = { ...submittingParty, phoneNumber: fromDisplayPhone(submittingParty.phoneNumber) }
    }

    return submittingParty
  }

  const parseOwnerGroups = (): MhrRegistrationHomeOwnerGroupIF[] => {
    const ownersGroups: MhrRegistrationHomeOwnerGroupIF[] = getMhrRegistrationHomeOwnerGroups.value

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

    description = cleanEmpty(description)
    description.sections = Object.values(description.sections)
    description.sectionCount = description.sections.length
    return description
  }

  const parseLocation = (): MhrRegistrationHomeLocationIF => {
    const location: MhrRegistrationHomeLocationIF = cleanEmpty(getMhrRegistrationLocation.value)

    // Work around require to satisfy schema validations. Currently, not collected by UI.
    if (!location.address.postalCode) location.address.postalCode = 'A1A 1A1'

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
      ownLand: getMhrRegistrationOwnLand.value,
      submittingParty: parseSubmittingParty(),
      ownerGroups: parseOwnerGroups(),
      location: parseLocation(),
      description: parseDescription(),
      ...(isRoleStaffReg.value && !!getStaffPayment.value && {
        clientReferenceId: getStaffPayment.value.folioNumber
      }),
      ...(!isMhrManufacturerRegistration.value && {
        documentId: getMhrRegistrationDocumentId.value
      }),
      ...(isMhrManufacturerRegistration.value && !!getFolioOrReferenceNumber.value && {
        clientReferenceId: getFolioOrReferenceNumber.value
      })
    }

    if (getMhrAttentionReference.value) {
      data.attentionReference = getMhrAttentionReference.value
    }

    if (getMhrDraftNumber.value) {
      data.draftNumber = getMhrDraftNumber.value
    }

    return data
  }

  const fetchMhRegistrations = async (sortOptions: RegistrationSortIF = null): Promise<void> => {
    const draftFilings = await getMhrDrafts(sortOptions)
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

  return {
    initNewMhr,
    initNewManufacturerMhr,
    initDraftMhr,
    mhrDraftHandler,
    resetLocationInfoFields,
    buildApiData,
    parseStaffPayment,
    fetchMhRegistrations,
    cleanEmpty
  }
}
