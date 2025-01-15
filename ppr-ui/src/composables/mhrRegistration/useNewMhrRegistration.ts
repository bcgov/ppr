import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import type {
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeLocationIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationIF,
  MhrLocationInfoIF,
  NewMhrRegistrationApiIF,
  MhRegistrationSummaryIF,
  RegistrationSortIF,
  MhrDraftIF
  , StaffPaymentIF
} from '@/interfaces'
import {
  APIMhrTypes,
  HomeTenancyTypes,
  HomeLocationTypes,
  MhApiStatusTypes,
  HomeCertificationOptions
} from '@/enums'
import {
  cleanEmpty,
  fromDisplayPhone
} from '@/utils'
import {
  createMhrDraft,
  getMhrDrafts,
  getMhrManufacturerInfo,
  mhrRegistrationHistory,
  updateMhrDraft
} from '@/utils/mhr-api-helper'
import { debounce, orderBy } from 'lodash'
import { useHomeOwners, useMhrCorrections } from '@/composables'

export const useNewMhrRegistration = (isMhrCorrections: boolean = false) => {
  const {
    // Actions
    setEmptyMhr,
    setFolioOrReferenceNumber,
    setMhrLocation,
    setMhrLocationAllFields,
    setMhrDraftNumber,
    setMhrTableHistory,
    resetMhrInformation,
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
    isMhrReRegistration,
    getFolioOrReferenceNumber,
    getMhrRegistrationHomeDescription,
    getMhrRegistrationSubmittingParty,
    getMhrRegistrationDocumentId,
    getMhrAttentionReference,
    getMhrRegistrationLocation,
    getMhrRegistrationHomeOwnerGroups,
    getMhrRegistrationOwnLand,
    getStaffPayment,
    getMhrDraftNumber,
    getRegistrationType,
    getMhrInformation,
    getMhrGenerateDocId
  } = storeToRefs(useStore())
  const {
    setShowGroups,
    getHomeTenancyType
  } = useHomeOwners(false, isMhrCorrections)

  const { isMhrCorrection } = useMhrCorrections()

  const initNewMhr = (resetMhrInfo = false): MhrRegistrationIF => {
    if (resetMhrInfo) resetMhrInformation()

    return {
      draftNumber: '',
      documentId: '',
      registrationType: null,
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
          region: null,
          country: null,
          postalCode: ''
        },
        emailAddress: '',
        phoneNumber: '',
        phoneExtension: ''
      },
      ownerGroups: [],
      attentionReference: '',
      isManualLocationInfo: false,
      ownLand: null,
      location: {
        parkName: '',
        pad: '',
        address: {
          street: '',
          streetAdditional: '',
          city: '',
          region: null,
          country: null,
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
      setMhrLocation({ key, value: val })

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
   * @param mhrData The mhr data to parse into store.
   * @param isCorrection flag prompting unique data handling for corrections only
   */
  const initDraftOrCurrentMhr = async (mhrData: MhrRegistrationIF, isCorrection = false): Promise<void> => {

    if (isCorrection) await setEmptyMhr({ ...initNewMhr() })

    // Set description
    for (const [key, val] of Object.entries(initNewMhr().description)) {
      mhrData?.description[key]
        ? setMhrHomeDescription({ key, value: mhrData.description[key] })
        : setMhrHomeDescription({ key, value: val }) // set missing description values to default
    }

    // Handle 'certificationOption' or 'noCertification' value mapping
    const certificationOption = (mhrData.description?.csaNumber && HomeCertificationOptions.CSA)
      || (mhrData.description?.engineerName && HomeCertificationOptions.ENGINEER_INSPECTION) || null
    setMhrHomeDescription({
      key: 'certificationOption',
      value: certificationOption,
    })
    setMhrHomeDescription({
      key: 'hasNoCertification',
      value: certificationOption === null,
    })

    // Set Submitting Party
    isCorrection
      ? setMhrRegistrationSubmittingParty({})
      : setMhrRegistrationSubmittingParty(mhrData.submittingParty)

    // Set Document Id
    isCorrection
      ? setMhrRegistrationDocumentId('')
      : setMhrRegistrationDocumentId(mhrData.documentId)

    // Set Land Ownership
    setMhrRegistrationOwnLand(mhrData.ownLand)

    // Set attention
    isCorrection
      ? setMhrAttentionReference('')
      : setMhrAttentionReference(mhrData.attentionReference)

    // Set folio or reference number
    setFolioOrReferenceNumber(mhrData.clientReferenceId)

    // Set HomeOwners
    isCorrection && mhrData.ownerGroups.forEach(
      (ownerGroup, index) => { ownerGroup.groupId = index + 1 }
    )
    setMhrRegistrationHomeOwnerGroups(mhrData.ownerGroups)

    // Show groups for Tenants in Common
    setShowGroups(getHomeTenancyType() === HomeTenancyTypes.COMMON)
    // Set Home Location
    const homeLocation = {} as MhrRegistrationHomeLocationIF

    for (const [key, val] of Object.entries(mhrData.location)) {
      homeLocation[key] = val
      // Map radio button options for Other Land Types
      if (
        [HomeLocationTypes.OTHER_RESERVE, HomeLocationTypes.OTHER_STRATA, HomeLocationTypes.OTHER_TYPE].includes(val)
      ) {
        homeLocation.otherType = val
        homeLocation.locationType = HomeLocationTypes.OTHER_LAND
      }
    }
    setMhrLocationAllFields(homeLocation)
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
    if (!location.address.postalCode) location.address.postalCode = ''

    // otherType is not required by API and locationType should have otherType's value (#14751)
    if (location.otherType) {
      location.locationType = location.otherType
      const { ...parsedLocation } = location
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
      submittingParty: parseSubmittingParty(),
      ownerGroups: parseOwnerGroups(),
      location: parseLocation(),
      description: parseDescription(),
      ...(!isMhrManufacturerRegistration.value && {
        ownLand: getMhrRegistrationOwnLand.value
      }),
      ...(isRoleStaffReg.value && !!getStaffPayment.value && {
        clientReferenceId: getStaffPayment.value.folioNumber
      }),
      ...(!isMhrManufacturerRegistration.value && !getMhrGenerateDocId.value && {
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

    // add additional props to payload for Mhr Corrections
    if (isMhrCorrection.value || isMhrReRegistration.value) {
      data.documentType = getRegistrationType.value?.registrationTypeAPI
      data.mhrNumber = getMhrInformation.value.mhrNumber
    }

    return data
  }

  const fetchMhRegistrations = debounce(async (sortOptions: RegistrationSortIF = null): Promise<void> => {
    const draftFilings = await getMhrDrafts(sortOptions)
    const myMhrHistory = await mhrRegistrationHistory(true, sortOptions)
    const filteredMhrHistory = addHistoryDraftsToMhr(myMhrHistory, draftFilings, sortOptions)
    setMhrTableHistory(filteredMhrHistory)
  }, 10)

  const mhrDraftHandler = async (): Promise<MhrDraftIF> => {

    const draftType = (isMhrCorrection.value || isMhrReRegistration.value)
      ? APIMhrTypes.REGISTRY_STAFF_ADMIN
      : APIMhrTypes.MANUFACTURED_HOME_REGISTRATION

    const draft = getMhrDraftNumber.value
      ? await updateMhrDraft(getMhrDraftNumber.value, draftType, buildApiData())
      : await createMhrDraft(draftType, buildApiData())

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
      mhRegDrafts = mhrDrafts?.filter(draft =>
        !draft.mhrNumber && [APIMhrTypes.MANUFACTURED_HOME_REGISTRATION, APIMhrTypes.REGISTRY_STAFF_ADMIN]
          .includes(draft.registrationType as APIMhrTypes)
      )
    }

    // add Transfer drafts to parent registrations.
    mhrHistory?.forEach(transfer => {
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
            outOfDate: draft.outOfDate,
            baseRegistrationNumber: transfer.mhrNumber,
            draftNumber: draft.draftNumber,
            submittingParty: draft.submittingParty,
            clientReferenceId: transfer.clientReferenceId,
            createDateTime: draft.createDateTime,
            lastUpdateDateTime: draft?.lastUpdateDateTime,
            error: draft.error,
            registrationType: draft.registrationType,
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
        transfer.changes = orderBy(transfer.changes, [
          (o) => o.statusType !== 'DRAFT',
          (o) => o.lastUpdateDateTime || o.createDateTime,
          (o) => o.createDateTime
        ], ['asc', 'desc', 'desc'])
      }
    })
    if (sortOptions?.status !== MhApiStatusTypes.DRAFT) mhrTableData = mhrHistory
    return [...mhRegDrafts, ...mhrTableData]
  }

  return {
    initNewMhr,
    initNewManufacturerMhr,
    initDraftOrCurrentMhr,
    mhrDraftHandler,
    resetLocationInfoFields,
    buildApiData,
    parseStaffPayment,
    fetchMhRegistrations,
  }
}
