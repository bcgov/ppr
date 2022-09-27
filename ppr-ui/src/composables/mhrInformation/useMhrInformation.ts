import { MhrTransferApiIF, MhrTransferIF } from '@/interfaces'
import { useGetters } from 'vuex-composition-helpers'
import { useNewMhrRegistration } from '@/composables'

export const useMhrInformation = () => {
  const {
    getCurrentUser,
    getMhrTransferHomeOwners,
    getMhrInformation
  } = useGetters<any>([
    'getCurrentUser',
    'getMhrInformation',
    'getMhrTransferHomeOwners'
  ])

  const {
    cleanEmpty
  } = useNewMhrRegistration()

  const initMhrTransfer = (): MhrTransferIF => {
    return {
      mhrNumber: '',
      ownerGroups: [],
      submittingParty: {}
    }
  }

  const parseOwnerGroups = (): any => {
    const ownerGroups = []

    getMhrTransferHomeOwners.value.forEach(ownerGroup => {
      const { groupId, ...owners } = ownerGroup
      ownerGroups.push({
        owners: [owners],
        groupId: parseInt(groupId),
        type: 'SO'
      })
    })

    return ownerGroups
  }

  const buildApiData = () => {
    const data: MhrTransferApiIF = {
      mhrNumber: getMhrInformation.value.mhrNumber,
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
      deleteOwnerGroups: parseOwnerGroups(), // Api requires something here - Next iteration includes existing owners
      deathOfOwner: false
    }

    return data
  }

  return {
    initMhrTransfer,
    buildApiData
  }
}
