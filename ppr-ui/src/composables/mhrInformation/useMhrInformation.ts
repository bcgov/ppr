import { MhrTransferApiIF, MhrTransferIF } from '@/interfaces'
import { useGetters } from 'vuex-composition-helpers'
import { readonly, ref } from '@vue/composition-api'
import { ActionTypes, ApiHomeTenancyTypes, HomeTenancyTypes } from '@/enums'

// Validation flag for Transfer Details
const transferDetailsValid = ref(false)

export const useMhrInformation = () => {
  const {
    getCurrentUser,
    getMhrTransferHomeOwners,
    getMhrInformation,
    getMhrTransferDeclaredValue,
    getMhrTransferConsideration,
    getMhrTransferDate,
    getMhrTransferOwnLand,
    getMhrTransferHomeOwnerGroups
  } = useGetters<any>([
    'getCurrentUser',
    'getMhrInformation',
    'getMhrTransferHomeOwners',
    'getMhrTransferDeclaredValue',
    'getMhrTransferConsideration',
    'getMhrTransferDate',
    'getMhrTransferOwnLand',
    'getMhrTransferHomeOwnerGroups'
  ])

  const setTransferDetailsValid = (isValid: boolean) => {
    transferDetailsValid.value = isValid
  }

  const initMhrTransfer = (): MhrTransferIF => {
    return {
      mhrNumber: '',
      ownerGroups: [],
      submittingParty: {},
      declaredValue: null,
      consideration: '',
      transferDate: '',
      ownLand: false
    }
  }

  const parseOwnerGroups = (): any => {
    const ownerGroups = []

    getMhrTransferHomeOwners.value.forEach(ownerGroup => {
      const { groupId, ...owners } = ownerGroup
      const groupType = getMhrTransferHomeOwnerGroups.value.find(group => group.groupId === ownerGroup.groupId)?.type
      const apiGroupType = ApiHomeTenancyTypes[
        Object.keys(HomeTenancyTypes).find(key => HomeTenancyTypes[key] as string === groupType)
      ]

      ownerGroups.push({
        owners: [owners].filter(owner => owner.action !== ActionTypes.REMOVED),
        groupId: parseInt(groupId),
        type: apiGroupType
      })
    })

    return ownerGroups.filter(group => group.owners.length !== 0)
  }

  const parseRemovedOwnerGroups = (): any => {
    const ownerGroups = []

    getMhrTransferHomeOwners.value.forEach(ownerGroup => {
      const { groupId, ...owners } = ownerGroup
      const groupType = getMhrTransferHomeOwnerGroups.value.find(group => group.groupId === ownerGroup.groupId)?.type
      const apiGroupType = ApiHomeTenancyTypes[
        Object.keys(HomeTenancyTypes).find(key => HomeTenancyTypes[key] as string === groupType)
      ]

      ownerGroups.push({
        owners: [owners].filter(owner => owner.action === ActionTypes.REMOVED),
        groupId: parseInt(groupId),
        type: apiGroupType
      })
    })

    return ownerGroups.filter(group => group.owners.length !== 0)
  }

  const buildApiData = (): MhrTransferApiIF => {
    const data: MhrTransferApiIF = {
      mhrNumber: getMhrInformation.value.mhrNumber,
      declaredValue: getMhrTransferDeclaredValue.value,
      consideration: getMhrTransferConsideration.value,
      transferDate: getMhrTransferDate.value,
      ownLand: getMhrTransferOwnLand.value,
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
      addOwnerGroups: parseOwnerGroups(),
      deleteOwnerGroups: parseRemovedOwnerGroups(),
      deathOfOwner: false
    }

    return data
  }

  return {
    isTransferDetailsValid: readonly(transferDetailsValid),
    setTransferDetailsValid,
    initMhrTransfer,
    buildApiData
  }
}
