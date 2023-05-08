import {
  AccountInfoIF,
  MhrHomeOwnerGroupIF,
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeLocationIF,
  MhrTransferApiIF,
  MhrTransferIF,
  SubmittingPartyIF,
  MhrRegistrationHomeOwnerGroupIF
} from '@/interfaces'
import { useActions, useGetters } from 'vuex-composition-helpers'
import {
  ActionTypes,
  ApiHomeTenancyTypes,
  ApiTransferTypes,
  HomeCertificationOptions,
  HomeLocationTypes,
  HomeTenancyTypes,
  MhApiStatusTypes,
  UIRegistrationTypes,
  UITransferTypes
} from '@/enums'
import { fetchMhRegistration, normalizeObject } from '@/utils'
import { cloneDeep } from 'lodash'
import { useHomeOwners, useTransferOwners } from '@/composables'
import { computed, reactive, toRefs } from '@vue/composition-api'

export const useMhrInformation = () => {
  const {
    isRoleStaffReg,
    getStaffPayment,
    getMhrInformation,
    isRoleQualifiedSupplier,
    getMhrTransferDeclaredValue,
    getMhrTransferConsideration,
    getMhrTransferDate,
    getMhrTransferOwnLand,
    getMhrTransferSubmittingParty,
    getMhrTransferAttentionReference,
    getMhrTransferHomeOwnerGroups,
    getMhrTransferCurrentHomeOwnerGroups,
    getMhrTransferType
  } = useGetters<any>([
    'isRoleStaffReg',
    'getStaffPayment',
    'getMhrInformation',
    'isRoleQualifiedSupplier',
    'getMhrTransferHomeOwners',
    'getMhrTransferDeclaredValue',
    'getMhrTransferConsideration',
    'getMhrTransferDate',
    'getMhrTransferOwnLand',
    'getMhrTransferSubmittingParty',
    'getMhrTransferAttentionReference',
    'getMhrTransferHomeOwnerGroups',
    'getMhrTransferCurrentHomeOwnerGroups',
    'getMhrTransferType'
  ])

  const {
    setMhrStatusType,
    setMhrTransferHomeOwnerGroups,
    setMhrTransferCurrentHomeOwnerGroups,
    setMhrLocation,
    setIsManualLocation,
    setMhrHomeDescription,
    setMhrTransferDeclaredValue,
    setMhrTransferType,
    setMhrTransferDate,
    setMhrTransferOwnLand,
    setMhrAttentionReferenceNum,
    setMhrTransferConsideration,
    setMhrTransferSubmittingParty
  } = useActions<any>([
    'setMhrStatusType',
    'setMhrTransferHomeOwnerGroups',
    'setMhrTransferCurrentHomeOwnerGroups',
    'setMhrLocation',
    'setIsManualLocation',
    'setMhrHomeDescription',
    'setMhrTransferType',
    'setMhrTransferDate',
    'setMhrTransferOwnLand',
    'setMhrAttentionReferenceNum',
    'setMhrTransferDeclaredValue',
    'setMhrTransferConsideration',
    'setMhrTransferSubmittingParty'
  ])

  const {
    setShowGroups
  } = useHomeOwners(true)
  const {
    isTransferDueToDeath,
    getCurrentOwnerGroupIdByOwnerId
  } = useTransferOwners()

  /** Local State for custom computed properties. **/
  const localState = reactive({
    isFrozenMhr: computed((): boolean => {
      return getMhrInformation.value.statusType === MhApiStatusTypes.FROZEN
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
      transferType: null,
      declaredValue: null,
      consideration: '',
      transferDate: '',
      ownLand: false,
      attentionReference: '',
      isAffidavitTransferCompleted: false
    }
  }

  const parseMhrInformation = async (includeDetails = false): Promise<void> => {
    const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)

    // Assign frozen state when the base registration is frozen (for drafts)
    if (data.status === MhApiStatusTypes.FROZEN) {
      await setMhrStatusType(MhApiStatusTypes.FROZEN)
    }

    const homeDetails = data?.description || {} // Safety check. Should always have description
    await parseMhrHomeDetails(homeDetails)

    // Store existing MHR Home Location info
    const currentLocationInfo = data?.location || {} // Safety check. Should always have location
    await parseMhrLocationInfo(currentLocationInfo)

    const currentOwnerGroups = data?.ownerGroups || [] // Safety check. Should always have ownerGroups
    await parseMhrHomeOwners(cloneDeep(currentOwnerGroups))

    // Parse transfer details conditionally.
    // Some situations call for it being pre-populated from base registration.
    includeDetails && parseTransferDetails(data)
  }

  const parseMhrHomeDetails = async (homeDetails: MhrRegistrationDescriptionIF): Promise<void> => {
    for (const [key, value] of Object.entries(homeDetails)) {
      setMhrHomeDescription({ key: key, value: value })
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
    const submittingParty = {
      businessName: accountInfo.name,
      address: accountInfo.mailingAddress,
      emailAddress: accountInfo.accountAdmin.email,
      email: accountInfo.accountAdmin.email,
      phoneNumber: accountInfo.accountAdmin.phone,
      phoneExtension: accountInfo.accountAdmin.phoneExtension
    } as SubmittingPartyIF

    setMhrTransferSubmittingParty(submittingParty)
  }

  const parseMhrLocationInfo = async (locationData: MhrRegistrationHomeLocationIF): Promise<void> => {
    for (const [key, value] of Object.entries(locationData)) {
      setMhrLocation({ key: key, value: value })
    }

    // Map and Apply an OTHER type when applicable
    if ([HomeLocationTypes.OTHER_RESERVE, HomeLocationTypes.OTHER_STRATA, HomeLocationTypes.OTHER_TYPE]
      .includes(locationData.locationType)) {
      setIsManualLocation(!locationData.pidNumber)
      setMhrLocation({ key: 'locationType', value: HomeLocationTypes.OTHER_LAND })
      setMhrLocation({ key: 'otherType', value: locationData.locationType })
    }
  }

  const getUiTransferType = (): UITransferTypes => {
    return UITransferTypes[
      Object.keys(ApiTransferTypes).find(key =>
        ApiTransferTypes[key] as string === getMhrTransferType.value?.transferType
      )]
  }

  /** Draft Filings **/
  /**
   * Parse a draft MHR Information into State.
   * @param draft The draft filing to parse.
   */
  const initDraftMhrInformation = async (draft: MhrTransferApiIF): Promise<void> => {
    // Set draft transfer type
    setMhrTransferType({ transferType: draft.registrationType })

    // Set draft transfer details
    parseTransferDetails(draft)

    // Set draft owner groups
    setShowGroups(draft.addOwnerGroups.length > 1 || draft.deleteOwnerGroups.length > 1)
    setMhrTransferHomeOwnerGroups([...draft.addOwnerGroups])

    // Set submitting party
    setMhrTransferSubmittingParty(draft.submittingParty)

    // Set Attention
    setMhrAttentionReferenceNum(draft.attentionReference)
  }

  const parseTransferDetails = (data: MhrTransferApiIF): void => {
    setMhrTransferDeclaredValue(data.declaredValue || '')
    setMhrTransferConsideration(data.consideration || '')
    setMhrTransferDate(data.transferDate || null)
    setMhrTransferOwnLand(data.ownLand || null)
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
          owners: ownerGroup.owners.filter(owner => owner.action !== ActionTypes.REMOVED).map(owner => {
            return owner.individualName
              ? {
                ...owner,
                description: owner.suffix,
                individualName: normalizeObject(owner.individualName)
              } : {
                ...owner,
                description: owner.suffix
              }
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
          type: ownerGroup.owners.filter(owner => owner.action === ActionTypes.REMOVED).length > 1
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
      ownLand: getMhrTransferOwnLand.value || false,
      documentDescription: UIRegistrationTypes.TRANSFER_OF_SALE,
      registrationType: getMhrTransferType.value?.transferType,
      submittingParty: {
        businessName: getMhrTransferSubmittingParty.value.businessName,
        personName: getMhrTransferSubmittingParty.value.personName,
        address: getMhrTransferSubmittingParty.value.address,
        emailAddress: getMhrTransferSubmittingParty.value.emailAddress,
        ...(getMhrTransferSubmittingParty.value.phoneNumber && {
          phoneNumber: getMhrTransferSubmittingParty.value.phoneNumber?.replace(/[^A-Z0-9]/ig, '')
        }),
        ...(getMhrTransferSubmittingParty.value.phoneExtension && {
          phoneExtension: getMhrTransferSubmittingParty.value.phoneExtension
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
    ...toRefs(localState)
  }
}
