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
import { fetchMhRegistration, normalizeObject, parseAccountToSubmittingParty } from '@/utils'
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
    setMhrInformationPermitData
  } = useStore()
  const {
    // Getters
    isRoleStaffReg,
    isRoleQualifiedSupplier,
    isRoleQualifiedSupplierLawyersNotaries,
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
    getLienRegistrationType
  } = storeToRefs(useStore())

  const {
    setShowGroups
  } = useHomeOwners(true)
  const {
    isTransferDueToDeath,
    getCurrentOwnerGroupIdByOwnerId
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
    })
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

  const parseMhrInformation = async (includeDetails = false): Promise<void> => {
    const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)

    // Assign frozen state when the base registration is frozen (for drafts)
    if (data?.status === MhApiStatusTypes.FROZEN) {
      await setMhrStatusType(MhApiStatusTypes.FROZEN)
    }

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

    // Set Transports Permit Data when it's present
    if(!!data?.permitStatus) await parseMhrPermitData(data)

    // Parse transfer details conditionally.
    // Some situations call for it being pre-populated from base registration.
    includeDetails && parseTransferDetails(data)
  }

  const parseMhrHomeDetails = async (homeDetails: MhrRegistrationDescriptionIF): Promise<void> => {
    for (const [key, value] of Object.entries(homeDetails)) {
      setMhrHomeDescription({ key, value })
    }

    setMhrHomeDescription({
      key: 'certificationOption',
      value: homeDetails.csaNumber ? HomeCertificationOptions.CSA : HomeCertificationOptions.ENGINEER_INSPECTION
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
  }

  const getUiTransferType = (): UITransferTypes => {
    return UITransferTypes[
      Object.keys(ApiTransferTypes).find(key =>
        ApiTransferTypes[key] as string === getMhrTransferType.value?.transferType
      )]
  }

  // Get information about the lien to help with styling and functionality
  const getLienInfo = (): { class: string, msg: string, isSubmissionAllowed: boolean } => {
    const isLienRegistrationTypeSA = getLienRegistrationType.value === APIRegistrationTypes.SECURITY_AGREEMENT
    const routeName = router.currentRoute.value.name

    if ((isRoleStaffReg.value && routeName === RouteNames.MHR_INFORMATION) ||
        (isRoleQualifiedSupplier.value && isLienRegistrationTypeSA && routeName === RouteNames.MHR_INFORMATION)) {
      return {
        class: 'warning-msg',
        msg: LienMessages.defaultWarning,
        isSubmissionAllowed: true
      }
    } else if ((isRoleStaffReg.value && routeName === RouteNames.EXEMPTION_DETAILS) ||
      (isRoleQualifiedSupplier.value && routeName === RouteNames.EXEMPTION_DETAILS && isLienRegistrationTypeSA)) {
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
    setShowGroups(draft.addOwnerGroups.length > 1 || draft.deleteOwnerGroups.length > 1)
    setMhrTransferHomeOwnerGroups([...draft.addOwnerGroups])

    // Set submitting party
    setMhrAccountSubmittingParty(draft.submittingParty)

    // Set Attention
    setMhrTransferAttentionReference(draft.attentionReference)
  }

  const parseTransferDetails = (data: MhrTransferApiIF): void => {
    setMhrTransferDeclaredValue(data?.declaredValue || null)
    setMhrTransferConsideration(data?.consideration || '')
    setMhrTransferDate(data?.transferDate || null)
    setMhrTransferOwnLand(data?.ownLand || null)
  }

  /** Filing Submission Helpers **/

  const parseOwnerGroups = (isDraft: boolean = false): MhrRegistrationHomeOwnerGroupIF[] => {
    const ownerGroups = []

    getMhrTransferHomeOwnerGroups.value.forEach(ownerGroup => {
      if (ownerGroup.action !== ActionTypes.REMOVED || isDraft) {
        ownerGroup.interestDenominator = ownerGroup.interestDenominator || 0
        ownerGroup.interestNumerator = ownerGroup.interestNumerator || 0
        const addedEditedOwners = ownerGroup.owners.filter(owner => owner.action !== ActionTypes.REMOVED)
          .map(owner => {
            return owner.individualName ? { ...owner, individualName: normalizeObject(owner.individualName) } : owner
          })

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
      if (ownerGroup.owners.some(owner => owner.action === ActionTypes.REMOVED)) {
        ownerGroups.push({
          ...ownerGroup,
          owners: ownerGroup.owners.filter(owner => owner.action !== ActionTypes.REMOVED)
            .map(owner => {
              return owner.individualName ? { ...owner, individualName: normalizeObject(owner.individualName) } : owner
            }),
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
      if (ownerGroup.owners.some(owner => owner.action === ActionTypes.REMOVED)) {
        ownerGroups.push({
          ...ownerGroup,
          groupId: getCurrentOwnerGroupIdByOwnerId(ownerGroup.owners[0].ownerId),
          owners: ownerGroup.owners.filter(owner => owner.action === ActionTypes.REMOVED).map(owner => {
            return owner.individualName ? { ...owner, individualName: normalizeObject(owner.individualName) } : owner
          }),
          // Determine group tenancy type
          type: (ownerGroup.owners.filter(owner => owner.action === ActionTypes.REMOVED).length > 1 ||
            getMhrTransferType.value?.transferType === ApiTransferTypes.SURVIVING_JOINT_TENANT)
            ? ApiHomeTenancyTypes.JOINT
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
    if (getMhrTransferType.value?.transferType === ApiTransferTypes.SALE_OR_GIFT) {
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

  const buildApiData = async (isDraft: boolean = false): Promise<MhrTransferApiIF> => {
    const data: MhrTransferApiIF = {
      draftNumber: getMhrInformation.value.draftNumber,
      mhrNumber: getMhrInformation.value.mhrNumber,
      declaredValue: getMhrTransferDeclaredValue.value,
      consideration: getMhrTransferConsideration.value,
      transferDate: getMhrTransferDate.value,
      ownLand: getMhrTransferOwnLand.value,
      ...(getMhrTransferDocumentId.value && {
        documentId: getMhrTransferDocumentId.value
      }),
      registrationType: getMhrTransferType.value?.transferType,
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
    ...toRefs(localState)
  }
}
