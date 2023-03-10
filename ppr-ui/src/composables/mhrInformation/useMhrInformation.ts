import {
  AccountInfoIF,
  MhrHomeOwnerGroupIF,
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeLocationIF,
  MhrTransferApiIF,
  MhrTransferIF, SubmittingPartyIF
} from '@/interfaces'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { readonly, ref } from '@vue/composition-api'
import {
  ActionTypes,
  ApiHomeTenancyTypes,
  ApiTransferTypes, HomeCertificationOptions, HomeLocationTypes,
  HomeTenancyTypes,
  UIRegistrationTypes,
  UITransferTypes
} from '@/enums'
import { fetchMhRegistration, getMhrTransferDraft } from '@/utils'
import { cloneDeep } from 'lodash'
import { useHomeOwners } from '@/composables'

export const useMhrInformation = () => {
  const {
    getMhrTransferCurrentHomeOwners,
    getMhrInformation,
    getMhrTransferDeclaredValue,
    getMhrTransferConsideration,
    getMhrTransferDate,
    getMhrTransferOwnLand,
    getMhrTransferSubmittingParty,
    getMhrTransferAttentionReference,
    getMhrTransferHomeOwnerGroups,
    getMhrTransferType
  } = useGetters<any>([
    'getMhrTransferCurrentHomeOwners',
    'getMhrInformation',
    'getMhrTransferHomeOwners',
    'getMhrTransferDeclaredValue',
    'getMhrTransferConsideration',
    'getMhrTransferDate',
    'getMhrTransferOwnLand',
    'getMhrTransferSubmittingParty',
    'getMhrTransferAttentionReference',
    'getMhrTransferHomeOwnerGroups',
    'getMhrTransferType'
  ])

  const {
    setMhrTransferHomeOwnerGroups,
    setMhrTransferCurrentHomeOwnerGroups,
    setMhrLocation,
    setIsManualLocation,
    setMhrHomeDescription,
    setMhrTransferDeclaredValue,
    setMhrTransferDate,
    setMhrTransferOwnLand,
    setMhrTransferConsideration,
    setMhrTransferSubmittingParty
  } = useActions<any>([
    'setMhrTransferHomeOwnerGroups',
    'setMhrTransferCurrentHomeOwnerGroups',
    'setMhrLocation',
    'setIsManualLocation',
    'setMhrHomeDescription',
    'setMhrTransferDate',
    'setMhrTransferOwnLand',
    'setMhrTransferConsideration',
    'setMhrTransferSubmittingParty'
  ])

  const {
    setShowGroups
  } = useHomeOwners(true)

  /** New Filings / Initializing **/

  const initMhrTransfer = (): MhrTransferIF => {
    return {
      mhrNumber: '',
      ownerGroups: [],
      submittingParty: {
        emailAddress: '',
        phoneNumber: ''
      },
      transferType: null,
      declaredValue: null,
      consideration: '',
      transferDate: '',
      ownLand: false,
      attentionReference: ''
    }
  }

  const parseMhrInformation = async (): Promise<void> => {
    const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)

    const homeDetails = data?.description || {} // Safety check. Should always have description
    await parseMhrHomeDetails(homeDetails)

    // Store existing MHR Home Location info
    const currentLocationInfo = data?.location || {} // Safety check. Should always have location
    await parseMhrLocationInfo(currentLocationInfo)

    const currentOwnerGroups = data?.ownerGroups || [] // Safety check. Should always have ownerGroups
    await parseMhrHomeOwners(cloneDeep(currentOwnerGroups))
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

    // Set owners to store
    if (getMhrInformation.value.draftNumber) {
      // Retrieve owners from draft if it exists
      const { registration } = await getMhrTransferDraft(getMhrInformation.value.draftNumber)

      // Set draft Transfer details to store
      parseDraftTransferDetails(registration as MhrTransferApiIF)

      setShowGroups(registration.addOwnerGroups.length > 1 || registration.deleteOwnerGroups.length > 1)
      setMhrTransferHomeOwnerGroups([...registration.addOwnerGroups])
    } else {
      // Set current owners if there is no draft
      setMhrTransferHomeOwnerGroups(cloneDeep(currentOwnerGroups))
    }
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

  const getUiTransferType = (apiTransferType: ApiTransferTypes): UITransferTypes => {
    return UITransferTypes[
      Object.keys(ApiTransferTypes).find(key => ApiTransferTypes[key] as string === apiTransferType)
    ]
  }

  /** Draft Filings **/

  const parseDraftTransferDetails = (draft: MhrTransferApiIF): void => {
    setMhrTransferDeclaredValue(draft.declaredValue || '')
    setMhrTransferConsideration(draft.consideration || '')
    setMhrTransferDate(draft.transferDate || null)
    setMhrTransferOwnLand(draft.ownLand || null)
  }

  /** Filing Submission Helpers **/

  const parseOwnerGroups = (isDraft: boolean = false): any => {
    const ownerGroups = []

    getMhrTransferHomeOwnerGroups.value.forEach(ownerGroup => {
      if (ownerGroup.action !== ActionTypes.REMOVED || isDraft) {
        ownerGroup.interestDenominator = ownerGroup.interestDenominator || 0
        ownerGroup.interestNumerator = ownerGroup.interestNumerator || 0
        ownerGroups.push({
          ...ownerGroup,
          owners: isDraft ? ownerGroup.owners : ownerGroup.owners.filter(owner => owner.action !== ActionTypes.REMOVED),
          groupId: ownerGroup.groupId + 1, // Increment from baseline groupID to create a new group for API
          type: ApiHomeTenancyTypes[
            Object.keys(HomeTenancyTypes).find(key => HomeTenancyTypes[key] as string === ownerGroup.type)
          ]
        })
      }
    })

    return isDraft ? ownerGroups : ownerGroups.filter(ownerGroup => ownerGroup.action !== ActionTypes.REMOVED)
  }

  const parseRemovedOwnerGroups = () => {
    return getMhrTransferCurrentHomeOwners.value
  }

  const buildApiData = async (isDraft: boolean = false): Promise<MhrTransferApiIF> => {
    const data: MhrTransferApiIF = {
      mhrNumber: getMhrInformation.value.mhrNumber,
      declaredValue: getMhrTransferDeclaredValue.value,
      consideration: getMhrTransferConsideration.value,
      transferDate: getMhrTransferDate.value,
      ownLand: getMhrTransferOwnLand.value || false,
      attentionReference: getMhrTransferAttentionReference.value,
      documentDescription: UIRegistrationTypes.TRANSFER_OF_SALE,
      registrationType: getMhrTransferType.value.transferType,
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
      addOwnerGroups: await parseOwnerGroups(isDraft),
      deleteOwnerGroups: await parseRemovedOwnerGroups()
    }

    return data
  }

  return {
    getUiTransferType,
    initMhrTransfer,
    buildApiData,
    parseDraftTransferDetails,
    parseMhrInformation,
    parseSubmittingPartyInfo
  }
}
