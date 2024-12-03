import {
  AccountInfoIF,
  MhrHomeOwnerGroupIF,
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeLocationIF,
  MhrTransferApiIF,
  MhrTransferIF,
  MhrRegistrationHomeOwnerGroupIF,
  TransferTypeSelectIF,
  MhRegistrationSummaryIF
} from '@/interfaces'
import { useStore } from '@/store/store'
import {
  APIRegistrationTypes,
  ActionTypes,
  ApiHomeTenancyTypes,
  ApiTransferTypes,
  HomeCertificationOptions,
  HomeLocationTypes,
  HomeTenancyTypes,
  MhApiFrozenDocumentTypes,
  MhApiStatusTypes,
  RouteNames,
  UITransferTypes
} from '@/enums'
import {
  fetchMhRegistration,
  normalizeObject,
  parseAccountToSubmittingParty
} from '@/utils'
import { cloneDeep } from 'lodash'
import { useHomeOwners, useTransferOwners } from '@/composables'
import { computed, reactive, toRefs } from 'vue'
import { storeToRefs } from 'pinia'
import {
  ClientTransferTypes,
  LienMessages,
  QSLockedStateUnitNoteTypes,
  QualifiedSupplierTransferTypes,
  StaffTransferTypes
} from '@/resources'
import { useRouter } from 'vue-router'

export const useMhrInformation = () => {
  const {
    // Actions
    setMhrStatusType,
    setMhrTransferHomeOwnerGroups,
    setMhrTransferCurrentHomeOwnerGroups,
    setMhrLocation,
    setMhrUnitNotes,
    setMhrFrozenDocumentType,
    setMhrExemptDateTime,
    setIsManualLocation,
    setMhrHomeDescription,
    setMhrTransferDeclaredValue,
    setMhrTransferType,
    setMhrTransferDocumentId,
    setMhrTransferDate,
    setMhrTransferOwnLand,
    setMhrTransferAttentionReference,
    setMhrTransferConsideration,
    setMhrAccountSubmittingParty,
    setMhrInformationPermitData,
    setMhrTransportPermitPreviousLocation,
    setTransportPermitChangeAllowed
  } = useStore()
  const {
    // Getters
    isRoleStaffReg,
    isRoleQualifiedSupplier,
    isRoleQualifiedSupplierLawyersNotaries,
    isRoleStaffSbc,
    getStaffPayment,
    getMhrInformation,
    getMhrTransferDeclaredValue,
    getMhrTransferConsideration,
    getMhrTransferDate,
    getMhrTransferOwnLand,
    getMhrAccountSubmittingParty,
    getMhrTransferAttentionReference,
    getMhrTransferHomeOwnerGroups,
    getMhrTransferCurrentHomeOwnerGroups,
    getMhrTransferDocumentId,
    getMhrTransferType,
    getLienRegistrationType,
    getMhrRegistrationLocation,
    getMhrGenerateDocId
  } = storeToRefs(useStore())

  const {
    setShowGroups
  } = useHomeOwners(true)
  const {
    isTransferToExecOrAdmin,
    isTransferDueToDeath,
    getCurrentOwnerGroupIdByOwnerId,
    isTransferNonGiftBillOfSale,
    isTransferBillOfSale,
    isTransferWithoutBillOfSale
  } = useTransferOwners()

  const router = useRouter()

  /** Local State for custom computed properties. **/
  const localState = reactive({
    isFrozenMhr: computed((): boolean => {
      return getMhrInformation.value.statusType === MhApiStatusTypes.FROZEN
    }),
    isExemptMhr: computed((): boolean => {
      return getMhrInformation.value.statusType === MhApiStatusTypes.EXEMPT
    }),
    isCancelledMhr: computed((): boolean => {
      return getMhrInformation.value.statusType === MhApiStatusTypes.CANCELLED
    }),
    isFrozenMhrDueToAffidavit: computed((): boolean => {
      return localState.isFrozenMhr &&
        getMhrInformation.value?.frozenDocumentType === MhApiFrozenDocumentTypes.TRANS_AFFIDAVIT
    }),
    isFrozenMhrDueToUnitNote: computed((): boolean => {
      return (
        isRoleQualifiedSupplier.value &&
        localState.isFrozenMhr &&
        QSLockedStateUnitNoteTypes.includes(getMhrInformation.value?.frozenDocumentType)
      )
    }),
    /** Returns true when there is a lien present that would block a Qualified Supplier from ALL Registration Types **/
    hasQsBlockingLien: computed((): boolean => {
      return [
        APIRegistrationTypes.SECURITY_AGREEMENT_TAX,
        APIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT_TAX,
        APIRegistrationTypes.TRANSITION_MH_TAX
      ].includes(getLienRegistrationType.value)
    }),
    /** Returns true when there is a lien present that would block a Qualified Supplier from Transfers or Exemptions **/
    hasQsTransferOrExemptionBlockingLien: computed((): boolean => {
      return localState.hasQsBlockingLien ||
        [
          APIRegistrationTypes.SECURITY_AGREEMENT_GOV,
          APIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT_GOV,
          APIRegistrationTypes.TRANSITION_MH_GOV,
          APIRegistrationTypes.MARRIAGE_MH,
          APIRegistrationTypes.LAND_TAX_LIEN,
          APIRegistrationTypes.MAINTENANCE_LIEN,
          APIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
          APIRegistrationTypes.SALE_OF_GOODS
        ].includes(getLienRegistrationType.value)
    }),
    /** Returns true when there is a lien present that would block a Qualified Supplier from Transport Permits **/
    hasQsPermitBlockingLien: computed((): boolean => {
      return localState.hasQsBlockingLien ||
        [
          APIRegistrationTypes.LAND_TAX_LIEN,
          APIRegistrationTypes.MAINTENANCE_LIEN,
          APIRegistrationTypes.MANUFACTURED_HOME_NOTICE
        ].includes(getLienRegistrationType.value)
    }),
  })

  /** New Filings / Initializing **/
  const initMhrTransfer = (): MhrTransferIF => {
    return {
      mhrNumber: '',
      ownerGroups: [],
      currentOwnerGroups: [],
      submittingParty: {
        emailAddress: '',
        phoneNumber: ''
      },
      documentId: '',
      transferType: null,
      declaredValue: null,
      consideration: '',
      transferDate: '',
      ownLand: null,
      attentionReference: '',
      isAffidavitTransferCompleted: false
    }
  }

  /** Returns true when the lien type is includes in the blocked lien list **/
  const includesBlockingLien = (lienType: APIRegistrationTypes) => {
    return [
      APIRegistrationTypes.SECURITY_AGREEMENT_TAX,
      APIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT_TAX,
      APIRegistrationTypes.TRANSITION_MH_TAX,
      APIRegistrationTypes.SECURITY_AGREEMENT_GOV,
      APIRegistrationTypes.TRANSITION_SECURITY_AGREEMENT_GOV,
      APIRegistrationTypes.TRANSITION_MH_GOV,
      APIRegistrationTypes.MARRIAGE_MH,
      APIRegistrationTypes.LAND_TAX_LIEN,
      APIRegistrationTypes.MAINTENANCE_LIEN,
      APIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
      APIRegistrationTypes.SALE_OF_GOODS
    ].includes(lienType)
  }

  const parseMhrInformation = async (includeDetails = false): Promise<void> => {
    const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)

    // Assign the status/state for the base registration
    await setMhrStatusType(data?.status)

    const homeDetails = data?.description || {} // Safety check. Should always have description
    await parseMhrHomeDetails(homeDetails)

    // Store existing MHR Home Location info
    const currentLocationInfo = data?.location || {} // Safety check. Should always have location
    await parseMhrLocationInfo(currentLocationInfo)

    const currentOwnerGroups = data?.ownerGroups || [] // Safety check. Should always have ownerGroups
    await parseMhrHomeOwners(cloneDeep(currentOwnerGroups))

    const unitNotes = data?.notes || []
    await setMhrUnitNotes(unitNotes)

    const frozenDocumentType = data?.frozenDocumentType || ''
    await setMhrFrozenDocumentType(frozenDocumentType)

    data?.exemptDateTime && setMhrExemptDateTime(data?.exemptDateTime)

    // Set Transports Permit Data when it's present
    if(!!data?.permitStatus) await parseMhrPermitData(data)

    // previous location of the Transport Permit (used to cancel the permit)
    data?.previousLocation && parsePreviousLocation(data.previousLocation)

    // parse the flag for Transport Permit changes (eg QS can only cancel its own permits)
    data?.changePermit && setTransportPermitChangeAllowed(data.changePermit)

    // Parse transfer details conditionally.
    // Some situations call for it being pre-populated from base registration.
    includeDetails && parseTransferDetails(data)
  }

  const parseMhrHomeDetails = async (homeDetails: MhrRegistrationDescriptionIF): Promise<void> => {
    for (const [key, value] of Object.entries(homeDetails)) {
      setMhrHomeDescription({ key, value })
    }

    // Handle 'certificationOption' or 'noCertification' value mapping
    const certificationOption = (homeDetails?.csaNumber && HomeCertificationOptions.CSA) ||
      (homeDetails?.engineerName && HomeCertificationOptions.ENGINEER_INSPECTION) || null
    setMhrHomeDescription({
      key: 'certificationOption',
      value: certificationOption,
    })
    setMhrHomeDescription({
      key: 'hasNoCertification',
      value: certificationOption === null,
    })
  }

  const parseMhrHomeOwners = async (ownerGroups: Array<MhrHomeOwnerGroupIF>): Promise<void> => {
    const currentOwnerGroups = ownerGroups || [] // Safety check. Should always have ownerGroups

    // Store a snapshot of the existing OwnerGroups for baseline of current state
    await setMhrTransferCurrentHomeOwnerGroups(cloneDeep(ownerGroups))

    currentOwnerGroups.forEach((ownerGroup, index) => { ownerGroup.groupId = index + 1 })
    setShowGroups(currentOwnerGroups.length > 1)

    setMhrTransferHomeOwnerGroups(cloneDeep(currentOwnerGroups))
  }

  const parseSubmittingPartyInfo = (accountInfo: AccountInfoIF): void => {
    const submittingParty = parseAccountToSubmittingParty(accountInfo)

    setMhrAccountSubmittingParty(submittingParty)
  }

  const parseMhrLocationInfo = async (locationData: MhrRegistrationHomeLocationIF): Promise<void> => {
    // Clear any entries before assigning new values
    for (const [key] of Object.entries(getMhrRegistrationLocation.value)) {
      setMhrLocation({ key, value: '' })
    }

    for (const [key, value] of Object.entries(locationData)) {
      setMhrLocation({ key, value })
    }

    // Map and Apply an OTHER type when applicable
    if ([HomeLocationTypes.OTHER_RESERVE, HomeLocationTypes.OTHER_STRATA, HomeLocationTypes.OTHER_TYPE]
      .includes(locationData.locationType)) {
      setIsManualLocation(!locationData.pidNumber)
      setMhrLocation({ key: 'locationType', value: HomeLocationTypes.OTHER_LAND })
      setMhrLocation({ key: 'otherType', value: locationData.locationType })
    }
  }

  /** Set Transport permit data to state **/
  const parseMhrPermitData = async (mhrSummary: MhRegistrationSummaryIF): Promise<void> => {
    const permitStatus = mhrSummary?.permitStatus || ''
    await setMhrInformationPermitData({
      permitKey: 'Status',
      permitData: permitStatus
    })

    const permitDateTime = mhrSummary?.permitDateTime || ''
    await setMhrInformationPermitData({
      permitKey: 'DateTime',
      permitData: permitDateTime
    })

    const permitExpiryDateTime = mhrSummary?.permitExpiryDateTime || ''
    await setMhrInformationPermitData({
      permitKey: 'ExpiryDateTime',
      permitData: permitExpiryDateTime
    })

    const permitRegistrationNumber = mhrSummary?.permitRegistrationNumber || ''
    await setMhrInformationPermitData({
      permitKey: 'RegistrationNumber',
      permitData: permitRegistrationNumber
    })

    const permitLandStatusConfirmation = mhrSummary?.permitLandStatusConfirmation ?? null
    await setMhrInformationPermitData({
      permitKey: 'LandStatusConfirmation',
      permitData: permitLandStatusConfirmation
    })
  }

  const getUiTransferType = (): UITransferTypes => {
    return UITransferTypes[
      Object.keys(ApiTransferTypes).find(key =>
        ApiTransferTypes[key] as string === getMhrTransferType.value?.transferType
      )]
  }

  // Get information about the lien to help with styling and functionality
  const getLienInfo = (): { class: string, msg: string, isSubmissionAllowed: boolean } => {
    const routeName = router.currentRoute.value.name
    const isQSorSBC: boolean = isRoleQualifiedSupplier.value || isRoleStaffSbc.value

    if (routeName === RouteNames.MHR_INFORMATION &&
      (isRoleStaffReg.value || (!localState.hasQsTransferOrExemptionBlockingLien && isQSorSBC))) {
      return {
        class: 'warning-msg',
        msg: LienMessages.defaultWarning,
        isSubmissionAllowed: true
      }
    } else if ((isRoleStaffReg.value && routeName === RouteNames.EXEMPTION_DETAILS) ||
      (isRoleQualifiedSupplier.value && !localState.hasQsTransferOrExemptionBlockingLien &&
        [RouteNames.EXEMPTION_DETAILS, RouteNames.EXEMPTION_REVIEW].includes(routeName as RouteNames)
      )) {
      return {
        class: 'warning-msg',
        msg: LienMessages.exemptionsWarning,
        isSubmissionAllowed: true
      }
    } else if (isRoleQualifiedSupplier.value) {
      return {
        class: 'error-msg',
        msg: LienMessages.QSError,
        isSubmissionAllowed: false
      }
    } else if (isRoleStaffSbc.value) { // SBC default message
      return {
        class: 'error-msg',
        msg: LienMessages.SbcError,
        isSubmissionAllowed: false
      }
    }
  }

  /** Draft Filings **/
  /**
   * Parse a draft MHR Information into State.
   * @param draft The draft filing to parse.
   */
  const initDraftMhrInformation = async (draft: MhrTransferApiIF): Promise<void> => {

    // find correct transfer type array based on role
    const roleBasedTransferTypes = (): TransferTypeSelectIF[] => {
      switch (true) {
        case isRoleStaffReg.value:
          return StaffTransferTypes
        case isRoleQualifiedSupplierLawyersNotaries.value:
          return QualifiedSupplierTransferTypes
        default:
          return ClientTransferTypes
      }
    }

    // find transfer type from array based on draft reg type
    const draftTransferType: TransferTypeSelectIF = roleBasedTransferTypes()
      .find(type => type.transferType === draft.registrationType)

    // Set draft transfer type
    setMhrTransferType(draftTransferType)

    // Set draft transfer details
    parseTransferDetails(draft)

    setMhrTransferDocumentId(draft.documentId)

    // Set draft owner groups
    setShowGroups(draft.addOwnerGroups?.length > 1 || draft.deleteOwnerGroups?.length > 1)
    setMhrTransferHomeOwnerGroups([...draft?.addOwnerGroups])

    // Set submitting party
    setMhrAccountSubmittingParty(draft.submittingParty)

    // Set Attention
    setMhrTransferAttentionReference(draft.attentionReference)
  }

  const parseTransferDetails = (data: MhrTransferApiIF): void => {
    setMhrTransferDeclaredValue(data?.declaredValue || null)
    setMhrTransferConsideration(data?.consideration || '')
    setMhrTransferDate(data?.transferDate || null)
    setMhrTransferOwnLand(data?.ownLand)
  }

  // Parse previous location of home - user for transport permit cancellation
  const parsePreviousLocation = (previousLocation: MhrRegistrationHomeLocationIF): void => {

    const otherTypes = [HomeLocationTypes.OTHER_RESERVE, HomeLocationTypes.OTHER_STRATA, HomeLocationTypes.OTHER_TYPE]

    // otherType location is used in UI only
    if (otherTypes.includes(previousLocation.locationType)) {
      previousLocation.otherType = previousLocation.locationType
      previousLocation.locationType = HomeLocationTypes.OTHER_LAND
    }

    setMhrTransportPermitPreviousLocation(previousLocation);
  }

  /** Filing Submission Helpers **/

  /**
   * Parses and returns the owner groups for a manufactured home transfer.
   *
   * @param {boolean} [isDraft=false] - Indicates whether the parsing is for a draft.
   * @returns {MhrRegistrationHomeOwnerGroupIF[]} The parsed owner groups.
   */
  const parseOwnerGroups = (isDraft: boolean = false): MhrRegistrationHomeOwnerGroupIF[] => {
    const ownerGroups = []

    getMhrTransferHomeOwnerGroups.value.forEach(ownerGroup => {
      if (ownerGroup.action !== ActionTypes.REMOVED || isDraft) {
        ownerGroup.interestDenominator = ownerGroup.interestDenominator || 0
        ownerGroup.interestNumerator = ownerGroup.interestNumerator || 0
        const addedEditedOwners = ownerGroup.owners
          .filter(owner => owner.action !== ActionTypes.REMOVED)
          .map(owner => ({
            ...owner,
            ...(owner.individualName && { individualName: normalizeObject(owner.individualName) }),
            ...(owner.action == ActionTypes.CHANGED && { previousOwnerId: owner.ownerId })
          }))

        ownerGroups.push({
          ...ownerGroup,
          owners: isDraft ? ownerGroup.owners : addedEditedOwners,
          groupId: ownerGroup.groupId,
          type: ApiHomeTenancyTypes[
            Object.keys(HomeTenancyTypes).find(key => HomeTenancyTypes[key] as string === ownerGroup.type)
          ]
        })
      }
    })

    return isDraft ? ownerGroups : ownerGroups.filter(ownerGroup => ownerGroup.action !== ActionTypes.REMOVED)
  }

  const parseDueToDeathOwnerGroups = (isDraft: boolean = false): MhrRegistrationHomeOwnerGroupIF[] => {
    const ownerGroups = []
    getMhrTransferHomeOwnerGroups.value.forEach(ownerGroup => {
      if (ownerGroup.owners.some(owner =>
        owner.action === ActionTypes.REMOVED || owner.action === ActionTypes.CHANGED)) {
        ownerGroups.push({
          ...ownerGroup,
          owners: ownerGroup.owners
            .filter(owner => owner.action !== ActionTypes.REMOVED)
            .map(owner => ({
              ...owner,
              ...(owner.individualName && { individualName: normalizeObject(owner.individualName) }),
              ...(owner.action == ActionTypes.CHANGED && { previousOwnerId: owner.ownerId })
            })),
          type: ApiHomeTenancyTypes[
            Object.keys(HomeTenancyTypes).find(key => HomeTenancyTypes[key] as string === ownerGroup.type)
          ]
        })
      }
    })
    return isDraft ? getMhrTransferHomeOwnerGroups.value : ownerGroups
  }

  const parseDeletedDueToDeathOwnerGroups = (): MhrRegistrationHomeOwnerGroupIF[] => {
    const ownerGroups = []
    getMhrTransferHomeOwnerGroups.value.forEach(ownerGroup => {
      if (ownerGroup.owners.some(owner =>
        owner.action === ActionTypes.REMOVED || owner.action === ActionTypes.CHANGED)) {
        ownerGroups.push({
          ...ownerGroup,
          groupId: getCurrentOwnerGroupIdByOwnerId(ownerGroup.owners[0].ownerId),
          owners: ownerGroup.owners.filter(owner =>
            owner.action === ActionTypes.REMOVED || owner.action === ActionTypes.CHANGED).map(owner => {
            return owner.individualName ? { ...owner, individualName: normalizeObject(owner.individualName) } : owner
          }),
          // Determine group tenancy type
          type: (ownerGroup.owners.filter(owner => owner.action === ActionTypes.REMOVED).length > 1 ||
                (getMhrTransferType.value?.transferType === ApiTransferTypes.SURVIVING_JOINT_TENANT &&
                  ownerGroup.owners.some(owner => owner.action === ActionTypes.REMOVED)
                ))
                ? isTransferToExecOrAdmin.value
                  ? ApiHomeTenancyTypes.NA
                  : ApiHomeTenancyTypes.JOINT
                : getMhrTransferHomeOwnerGroups.value.length > 1
                  ? ApiHomeTenancyTypes.NA
                  : ApiHomeTenancyTypes.SOLE
        })
      }
    })

    return ownerGroups
  }

  const parseDeletedOwnerGroups = (): MhrRegistrationHomeOwnerGroupIF[] => {
    // Return the current state for Sale or Gift
    if (isTransferBillOfSale.value || isTransferWithoutBillOfSale.value) {
      return getMhrTransferCurrentHomeOwnerGroups.value
    }

    const ownerGroups = []
    getMhrTransferHomeOwnerGroups.value.forEach(ownerGroup => {
      if (ownerGroup.owners.some(owner => owner.action === ActionTypes.REMOVED)) {
        ownerGroups.push({
          ...ownerGroup,
          groupId: getCurrentOwnerGroupIdByOwnerId(ownerGroup.owners[0].ownerId),
          owners: ownerGroup.owners.map(owner => {
            return owner.individualName ? { ...owner, individualName: normalizeObject(owner.individualName) } : owner
          }),
          type: ApiHomeTenancyTypes.JOINT // Can only remove Joint Tenants outside SoG Transfers (ie death scenarios)
        })
      }
    })

    return ownerGroups
  }

  /**
   * Builds the API data payload for a manufactured home transfer filing.
   * @param {boolean} [isDraft=false] - Indicates whether the filing is a draft.
   * @returns {Promise<MhrTransferApiIF>} The API data payload for the manufactured home transfer.
   */
  const buildApiData = async (isDraft: boolean = false): Promise<MhrTransferApiIF> => {
    // Handles instances where declared value is a set number and readonly (ex SoG flow following an Affe filing)
    // When string captured by UI: cast to integer and remove commas if they exist
    const declaredValue = (typeof getMhrTransferDeclaredValue.value === 'string')
      ? parseInt(getMhrTransferDeclaredValue.value?.replace(/,/g, ''))
      : getMhrTransferDeclaredValue.value

    const data: MhrTransferApiIF = {
      draftNumber: getMhrInformation.value.draftNumber,
      mhrNumber: getMhrInformation.value.mhrNumber,
      declaredValue: declaredValue,
      consideration: getMhrTransferConsideration.value,
      transferDate: getMhrTransferDate.value,
      ownLand: getMhrTransferOwnLand.value,
      ...(getMhrTransferDocumentId.value && !getMhrGenerateDocId.value && {
        documentId: getMhrTransferDocumentId.value
      }),
      registrationType: (isTransferNonGiftBillOfSale.value || isTransferWithoutBillOfSale.value)
        ? ApiTransferTypes.SALE_OR_GIFT
        : getMhrTransferType.value?.transferType,
      ...((isTransferNonGiftBillOfSale.value || isTransferWithoutBillOfSale.value) && {
        transferDocumentType: getMhrTransferType.value?.transferType
      }),
      submittingParty: {
        businessName: getMhrAccountSubmittingParty.value.businessName,
        personName: getMhrAccountSubmittingParty.value.personName,
        address: getMhrAccountSubmittingParty.value.address,
        ...(getMhrAccountSubmittingParty.value.emailAddress && {
          emailAddress: getMhrAccountSubmittingParty.value.emailAddress
        }),
        ...(getMhrAccountSubmittingParty.value.phoneNumber && {
          phoneNumber: getMhrAccountSubmittingParty.value.phoneNumber?.replace(/[^A-Z0-9]/ig, '')
        }),
        ...(getMhrAccountSubmittingParty.value.phoneExtension && {
          phoneExtension: getMhrAccountSubmittingParty.value.phoneExtension
        }),
        ...(isDraft && getMhrAccountSubmittingParty.value.hasUsedPartyLookup && {
          hasUsedPartyLookup: true
        })
      },
      ...(isRoleQualifiedSupplier.value && !isRoleStaffReg.value && {
        clientReferenceId: getMhrTransferAttentionReference.value
      }),
      ...(isRoleStaffReg.value && !!getStaffPayment.value && {
        clientReferenceId: getStaffPayment.value.folioNumber
      }),
      ...(isRoleStaffReg.value && !!getMhrTransferAttentionReference.value && {
        attentionReference: getMhrTransferAttentionReference.value
      }),
      addOwnerGroups: isTransferDueToDeath.value
        ? parseDueToDeathOwnerGroups(isDraft)
        : parseOwnerGroups(isDraft),
      deleteOwnerGroups: isTransferDueToDeath.value
        ? parseDeletedDueToDeathOwnerGroups()
        : parseDeletedOwnerGroups()
    }

    return data
  }

  return {
    getUiTransferType,
    initMhrTransfer,
    buildApiData,
    parseTransferDetails,
    parseMhrInformation,
    initDraftMhrInformation,
    parseSubmittingPartyInfo,
    getLienInfo,
    includesBlockingLien,
    parseMhrPermitData,
    ...toRefs(localState)
  }
}
