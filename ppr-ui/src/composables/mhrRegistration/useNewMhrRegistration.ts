import { useGetters } from 'vuex-composition-helpers'
import {
  getMhrAttentionReferenceNum,
  getMhrRegistrationDocumentId,
  getMhrRegistrationHomeDescription, getMhrRegistrationHomeOwnerGroups, getMhrRegistrationLocation,
  getMhrRegistrationSubmittingParty
} from '@/store/getters'
import {
  MhrRegistrationDescriptionIF,
  MhrRegistrationHomeLocationIF,
  MhrRegistrationHomeOwnerGroupIF,
  NewMhrRegistrationApiIF
} from '@/interfaces'

export const useNewMhrRegistration = () => {
  const {
    getMhrRegistrationHomeDescription,
    getMhrRegistrationSubmittingParty,
    getMhrRegistrationDocumentId,
    getMhrAttentionReferenceNum,
    getMhrRegistrationLocation,
    getMhrRegistrationHomeOwnerGroups
  } = useGetters<any>([
    'getMhrRegistrationHomeDescription',
    'getMhrRegistrationSubmittingParty',
    'getMhrRegistrationDocumentId',
    'getMhrAttentionReferenceNum',
    'getMhrRegistrationLocation',
    'getMhrRegistrationHomeOwnerGroups'
  ])

  function cleanEmpty<Type> (obj:Type): Type {
    const newObj = {}
    Object.keys(obj).forEach((key) => {
      if (obj[key] !== null && typeof obj[key] === 'object') newObj[key] = cleanEmpty(obj[key])
      else if (!!obj[key] || obj[key] === 0) newObj[key] = obj[key]
    })
    return newObj as Type
  }

  const parseSubmittingParty = () => {
    const submittingParty = getMhrRegistrationSubmittingParty.value

    if (submittingParty.businessName) {
      delete submittingParty.personName
    } else {
      delete submittingParty.businessName
      if (!submittingParty.personName.middle) {
        delete submittingParty.personName.middle
      }
    }
    if (!submittingParty.emailAddress) {
      delete submittingParty.emailAddress
    }
    if (!submittingParty.phoneNumber) {
      delete submittingParty.phoneNumber
    }
    if (!submittingParty.phoneExtension) {
      delete submittingParty.phoneExtension
    }

    return submittingParty
  }

  const parseOwnerGroups = (): MhrRegistrationHomeOwnerGroupIF[] => {
    const ownerGroups: MhrRegistrationHomeOwnerGroupIF[] =
      Object.values(cleanEmpty(getMhrRegistrationHomeOwnerGroups.value))
    ownerGroups.forEach(ownerGroup => {
      ownerGroup.owners = Object.values(ownerGroup.owners)

      // @ts-ignore - TODO: api asks for number, maybe fix this in future ticket?
      ownerGroup.groupId = parseInt(ownerGroup.groupId)

      ownerGroup.type = 'SO'// TODO: for testing only, DELETE AFTERWARDS
    })

    return ownerGroups
  }

  const parseDescription = (): MhrRegistrationDescriptionIF => {
    const description: MhrRegistrationDescriptionIF = cleanEmpty(getMhrRegistrationHomeDescription.value)

    description.manufacturer = '*' // TODO: for testing only, DELETE AFTERWARDS
    description.sections = Object.values(description.sections)
    description.sectionCount = description.sections.length
    return description
  }

  const parseLocation = (): MhrRegistrationHomeLocationIF => {
    const location: MhrRegistrationHomeLocationIF = cleanEmpty(getMhrRegistrationLocation.value)

    /* TODO: for testing only, DELETE AFTERWARDS */
    location.address.country = 'CA'
    location.address.region = 'BC'
    location.address.postalCode = 'V8N 0A1'
    /* for testing only, DELETE AFTERWARDS */

    return location
  }

  const buildApiData = () => {
    const data: NewMhrRegistrationApiIF = {
      documentId: getMhrRegistrationDocumentId.value,
      submittingParty: parseSubmittingParty(),
      ownerGroups: parseOwnerGroups(),
      location: parseLocation(),
      description: parseDescription()
    }

    if (getMhrAttentionReferenceNum.value) {
      data.clientReferenceId = getMhrAttentionReferenceNum.value
    }

    return data
  }

  return {
    buildApiData
  }
}
