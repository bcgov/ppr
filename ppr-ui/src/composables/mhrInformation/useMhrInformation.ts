import { MhrTransferApiIF, MhrTransferIF } from '@/interfaces'
import { useGetters } from 'vuex-composition-helpers'
import { readonly, ref } from '@vue/composition-api'
import { ActionTypes, ApiHomeTenancyTypes, HomeTenancyTypes } from '@/enums'

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
    'getMhrTransferAttentionReference',
    'getMhrTransferHomeOwnerGroups'
  ])

  const setRefNumValid = (isValid: boolean) => {
    refNumValid.value = isValid
  }

  const initMhrTransfer = (): MhrTransferIF => {
    return {
      mhrNumber: '',
      ownerGroups: [],
      submittingParty: {},
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
      ownLand: getMhrTransferOwnLand.value,
      attentionReference: getMhrTransferAttentionReference.value,
      documentDescription: 'SALE OR GIFT',
      submittingParty: {
        personName: {
          first: getCurrentUser.value.firstname,
          last: getCurrentUser.value.lastname
        },
        address: {
          street: '222 SUMMER STREET',
          city: 'VICTORIA',
          region: 'BC',
          country: 'CA',
          postalCode: 'V8W 2V8'
        },
        emailAddress: getCurrentUser.value.contacts[0].email,
        phoneNumber: getCurrentUser.value.contacts[0].phone.replace(/[^0-9.]+/g, '') // Remove special chars
      },
      addOwnerGroups: await parseOwnerGroups(isDraft),
      deleteOwnerGroups: await parseRemovedOwnerGroups(),
      deathOfOwner: false
    }

    return data
  }

  return {
    isRefNumValid: readonly(refNumValid),
    setRefNumValid,
    initMhrTransfer,
    buildApiData
  }
}
