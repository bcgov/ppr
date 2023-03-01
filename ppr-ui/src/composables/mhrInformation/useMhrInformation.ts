import { MhrTransferApiIF, MhrTransferIF } from '@/interfaces'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { readonly, ref } from '@vue/composition-api'
import {
  ActionTypes,
  ApiHomeTenancyTypes,
  ApiTransferTypes,
  HomeTenancyTypes,
  UIRegistrationTypes,
  UITransferTypes
} from '@/enums'

// Validation flags for Review Confirm screen
const refNumValid = ref(true)

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
    setMhrTransferDeclaredValue,
    setMhrTransferConsideration,
    setMhrTransferDate,
    setMhrTransferOwnLand
  } = useActions([
    'setMhrTransferDeclaredValue',
    'setMhrTransferConsideration',
    'setMhrTransferDate',
    'setMhrTransferOwnLand'
  ])

  const setRefNumValid = (isValid: boolean) => {
    refNumValid.value = isValid
  }

  const getUiTransferType = (apiTransferType: ApiTransferTypes): UITransferTypes => {
    return UITransferTypes[
      Object.keys(ApiTransferTypes).find(key => ApiTransferTypes[key] as string === apiTransferType)
    ]
  }

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

  const parseDraftTransferDetails = (draft: MhrTransferApiIF): void => {
    setMhrTransferDeclaredValue(draft.declaredValue || '')
    setMhrTransferConsideration(draft.consideration || '')
    setMhrTransferDate(draft.transferDate || null)
    setMhrTransferOwnLand(draft.ownLand || null)
  }

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
    isRefNumValid: readonly(refNumValid),
    setRefNumValid,
    getUiTransferType,
    initMhrTransfer,
    buildApiData,
    parseDraftTransferDetails
  }
}
