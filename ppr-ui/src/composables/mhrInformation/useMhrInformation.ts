import { MhrTransferApiIF, MhrTransferIF, SubmittingPartyIF } from '@/interfaces'
import { useGetters } from 'vuex-composition-helpers'
import { readonly, ref } from '@vue/composition-api'
import { ActionTypes, ApiHomeTenancyTypes, HomeTenancyTypes, UIRegistrationTypes } from '@/enums'

// Validation flag for Transfer Details
const transferDetailsValid = ref(false)

// Validation flags for Review Confirm screen
const refNumValid = ref(true)

export const useMhrInformation = () => {
  const {
    getMhrTransferCurrentHomeOwners,
    getCurrentUser,
    getMhrInformation,
    getMhrTransferDeclaredValue,
    getMhrTransferConsideration,
    getMhrTransferDate,
    getMhrTransferOwnLand,
    getMhrTransferSubmittingParty,
    getMhrTransferAttentionReference,
    getMhrTransferHomeOwnerGroups
  } = useGetters<any>([
    'getMhrTransferCurrentHomeOwners',
    'getCurrentUser',
    'getMhrInformation',
    'getMhrTransferHomeOwners',
    'getMhrTransferDeclaredValue',
    'getMhrTransferConsideration',
    'getMhrTransferDate',
    'getMhrTransferOwnLand',
    'getMhrTransferSubmittingParty',
    'getMhrTransferAttentionReference',
    'getMhrTransferHomeOwnerGroups'
  ])

  const setTransferDetailsValid = (isValid: boolean) => {
    transferDetailsValid.value = isValid
  }

  const setRefNumValid = (isValid: boolean) => {
    refNumValid.value = isValid
  }

  const initMhrTransfer = (): MhrTransferIF => {
    return {
      mhrNumber: '',
      ownerGroups: [],
      submittingParty: {
        emailAddress: '',
        phoneNumber: ''
      },
      declaredValue: null,
      consideration: '',
      transferDate: '',
      ownLand: false,
      attentionReference: ''
    }
  }

  const parseOwnerGroups = (isDraft: boolean = false): any => {
    const ownerGroups = []

    getMhrTransferHomeOwnerGroups.value.forEach(ownerGroup => {
      if (ownerGroup.action !== ActionTypes.REMOVED || isDraft) {
        ownerGroups.push({
          ...ownerGroup,
          owners: isDraft ? ownerGroup.owners : ownerGroup.owners.filter(owner => owner.action !== ActionTypes.REMOVED),
          groupId: ownerGroup.groupId + 1, // Increment from baseline groupID to create a new group for API
          type:
            ApiHomeTenancyTypes[
              Object.keys(HomeTenancyTypes).find(key => (HomeTenancyTypes[key] as string) === ownerGroup.type)
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
      ownLand: getMhrTransferOwnLand.value,
      attentionReference: getMhrTransferAttentionReference.value,
      documentDescription: UIRegistrationTypes.TRANSFER_OF_SALE,
      submittingParty: {
        // Need to confirm if this needs to be a Business Name instead
        // because in UI, Submitting Party is a business not a person
        // but the API spec requires firstName, lastName
        personName: {
          first: getCurrentUser.value.firstname,
          last: getCurrentUser.value.lastname
        },
        address: getMhrTransferSubmittingParty.value.address,
        emailAddress: getMhrTransferSubmittingParty.value.emailAddress,
        phoneNumber: getMhrTransferSubmittingParty.value.phoneNumber,
        phoneExtension: getMhrTransferSubmittingParty.value.phoneExtension
        // Cleanup below after confirming that Submitting Party info is Account's Admin info
        // emailAddress: getCurrentUser.value.contacts[0].email,
        // phoneNumber: getCurrentUser.value.contacts[0].phone.replace(/[^0-9.]+/g, '') // Remove special chars
      } as SubmittingPartyIF,
      addOwnerGroups: await parseOwnerGroups(isDraft),
      deleteOwnerGroups: await parseRemovedOwnerGroups(),
      deathOfOwner: false
    }

    return data
  }

  return {
    isTransferDetailsValid: readonly(transferDetailsValid),
    isRefNumValid: readonly(refNumValid),
    setTransferDetailsValid,
    setRefNumValid,
    initMhrTransfer,
    buildApiData
  }
}
