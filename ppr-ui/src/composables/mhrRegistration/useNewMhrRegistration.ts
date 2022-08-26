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

  /**
   * @function cleanEmpty
   *
   * Cleans the given object.
   * Deletes properties that has `null`, `undefined`, or `''` as values.
   *
   * @typeParam Type - type of object getting passed in
   * @param obj - The object to be cleaned up
   * @returns A new Object excluding `null`, `undefined`, or `''` values from the original Object.
   */
  function cleanEmpty<Type> (obj:Type): Type {
    const newObj = {}
    Object.keys(obj).forEach((key) => {
      if (obj[key] !== null && typeof obj[key] === 'object') { // getting deep into a nested object
        newObj[key] = cleanEmpty(obj[key])
      } else if (!!obj[key] || obj[key] === 0) { // add the key/value when it's not null, undefined, or empty string
        newObj[key] = obj[key]
      }
    })
    return newObj as Type
  }

  const parseSubmittingParty = () => {
    const submittingParty = cleanEmpty(getMhrRegistrationSubmittingParty.value)

    if (submittingParty.businessName) {
      delete submittingParty.personName
    }

    /* TODO: Mhr-Submission - DELETE after Api bug has been fixed */
    if (submittingParty.personName) {
      const first = submittingParty.personName.firstName
      const middle = submittingParty.personName.middleName
      const last = submittingParty.personName.lastName
      submittingParty.businessName = [first, middle, last].reduce((x, y) => y ? x + ' ' + y : x)
    }
    /* DELETE after Api bug has been fixed */

    return submittingParty
  }

  const parseOwnerGroups = (): MhrRegistrationHomeOwnerGroupIF[] => {
    const ownerGroups: MhrRegistrationHomeOwnerGroupIF[] =
      Object.values(cleanEmpty(getMhrRegistrationHomeOwnerGroups.value))
    ownerGroups.forEach(ownerGroup => {
      ownerGroup.owners = Object.values(ownerGroup.owners)

      // @ts-ignore - TODO: Mhr-Submission - api asks for number, maybe fix this once step 3 is finished?
      ownerGroup.groupId = parseInt(ownerGroup.groupId)

      ownerGroup.type = 'SO'// TODO: Mhr-Submission - DELETE after step 3 has been completed
    })

    return ownerGroups
  }

  const parseDescription = (): MhrRegistrationDescriptionIF => {
    let description: MhrRegistrationDescriptionIF = getMhrRegistrationHomeDescription.value

    /* TODO: Mhr-Submission - DELETE after manufacturer set to required */
    if (!description.manufacturer) {
      description.manufacturer = '*'
    }
    /* DELETE after manufacturer set to required */

    description = cleanEmpty(description)
    description.sections = Object.values(description.sections)
    description.sectionCount = description.sections.length
    return description
  }

  const parseLocation = (): MhrRegistrationHomeLocationIF => {
    const location: MhrRegistrationHomeLocationIF = cleanEmpty(getMhrRegistrationLocation.value)

    // location is always in BC
    location.address.country = 'CA'
    location.address.region = 'BC'

    // TODO: Mhr-Submission - DELETE after postal code can be retrieved from UI
    location.address.postalCode = 'V8W 2H3'

    // TODO: Mhr-Submission - UPDATE after confirming how to parse street number
    location.address.street = location.address.street.replace('-', ' ')

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
      data.attentionReferenceNum = getMhrAttentionReferenceNum.value
    }

    return data
  }

  return {
    buildApiData
  }
}
