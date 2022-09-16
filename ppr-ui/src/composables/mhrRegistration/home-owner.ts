import {
  MhrRegistrationTotalOwnershipAllocationIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnersIF,
  MhrRegistrationFractionalOwnershipIF
} from '@/interfaces'
import '@/utils/use-composition-api'

import { ref, computed, readonly, watch, toRefs } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { HomeTenancyTypes } from '@/enums'
import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'
import { useMhrValidations } from '@/composables'
import { find, remove, set, findIndex, sumBy } from 'lodash'

const DEFAULT_GROUP_ID = '1'

// Show or hide grouping of the Owners in the table
const showGroups = ref(false)
// Set global edit mode to enable or disable all Edit and dropdown buttons
const isGlobalEditingMode = ref(false)
// Flag is any of the Groups has no Owners
const hasEmptyGroup = ref(false)

export function useHomeOwners (isPerson: boolean = false, isEditMode: boolean = false) {
  const {
    getMhrRegistrationHomeOwners,
    getMhrRegistrationHomeOwnerGroups,
    getMhrRegistrationValidationModel
  } = useGetters<any>([
    'getMhrRegistrationHomeOwners',
    'getMhrRegistrationHomeOwnerGroups',
    'getMhrRegistrationValidationModel'
  ])

  const { setMhrRegistrationHomeOwnerGroups } = useActions<any>(['setMhrRegistrationHomeOwnerGroups'])

  const { setValidation } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

  // Title for left side bar
  const getSideTitle = computed((): string => {
    if (isPerson) {
      return isEditMode ? 'Add a Person' : 'Edit Person'
    } else {
      return isEditMode ? 'Add a Business or Organization' : 'Edit Business'
    }
  })

  // Show or hide groups in the owner's table
  const setShowGroups = show => {
    showGroups.value = show
  }

  // Set global editing to enable or disable all Edit buttons
  const setGlobalEditingMode = isEditing => {
    isGlobalEditingMode.value = isEditing
  }

  const getHomeTenancyType = (): HomeTenancyTypes => {
    const numOfOwners = getMhrRegistrationHomeOwners.value?.length

    if (showGroups.value) {
      // At leas one group showing with one or more owners
      return HomeTenancyTypes.COMMON
    } else if (numOfOwners === 1 && getMhrRegistrationHomeOwners.value[0].address !== undefined) {
      // One owner without groups showing
      return HomeTenancyTypes.SOLE
    } else if (numOfOwners > 1) {
      // More than one owner without groups showing
      return HomeTenancyTypes.JOINT
    }
    return HomeTenancyTypes.NA
  }

  const getGroupTenancyType = (group: MhrRegistrationHomeOwnerGroupIF): HomeTenancyTypes => {
    const numOfOwnersInGroup = group.owners.length

    if (numOfOwnersInGroup === 1) {
      return HomeTenancyTypes.COMMON
    } else if (numOfOwnersInGroup > 1) {
      return HomeTenancyTypes.JOINT
    } else {
      return HomeTenancyTypes.NA
    }
  }

  /**
   * Get Ownership Allocation status object to conveniently show total allocation
   * and an allocation error status if exists
   */
  const getTotalOwnershipAllocationStatus = (): MhrRegistrationTotalOwnershipAllocationIF => {
    // Sum up all 'interestNumerator' values in different Home Owner groups with a help of sumBy() function from lodash
    const totalFractionalNominator = sumBy(getMhrRegistrationHomeOwnerGroups.value, 'interestNumerator')
    const fractionalDenominator = getMhrRegistrationHomeOwnerGroups.value[0]?.interestTotal || null

    return {
      totalAllocation: totalFractionalNominator + '/' + fractionalDenominator,
      hasTotalAllocationError: totalFractionalNominator !== fractionalDenominator
    }
  }

  const getNumberOfGroups = (): boolean => {
    return !getMhrRegistrationHomeOwnerGroups.value || getMhrRegistrationHomeOwnerGroups.value.length < 2
  }
  // WORKING WITH GROUPS

  // Generate dropdown items for the group selection
  const getGroupDropdownItems = (isAddingHomeOwner: Boolean, groupId: string): Array<any> => {
    // Make additional Group available in dropdown when adding a new home owner
    // or when there are more than one owner in the group

    let numOfAdditionalGroupsInDropdown = 0

    if (isAddingHomeOwner) {
      numOfAdditionalGroupsInDropdown = 1
    } else {
      numOfAdditionalGroupsInDropdown =
        find(getMhrRegistrationHomeOwnerGroups.value, { groupId: groupId })?.owners.length > 1 ? 1 : 0
    }

    if (showGroups.value) {
      return Array(getMhrRegistrationHomeOwnerGroups.value.length + numOfAdditionalGroupsInDropdown)
        .fill({})
        .map((v, i) => {
          return { text: 'Group ' + (i + 1), value: (i + 1).toString() }
        })
    } else {
      return [
        {
          text: 'Group 1',
          value: DEFAULT_GROUP_ID
        }
      ]
    }
  }

  const getGroupForOwner = (ownerId: string): MhrRegistrationHomeOwnerGroupIF => {
    return find(getMhrRegistrationHomeOwnerGroups.value, group => {
      return find(group.owners, { id: ownerId })
    })
  }

  const addOwnerToTheGroup = (owner: MhrRegistrationHomeOwnersIF, groupId: string) => {
    const homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]

    // Try to find a group to add the owner
    const groupToUpdate =
      homeOwnerGroups.find(
        (group: MhrRegistrationHomeOwnerGroupIF) => group.groupId === (groupId || DEFAULT_GROUP_ID)
      ) || ({} as MhrRegistrationHomeOwnerGroupIF)

    if (groupToUpdate.owners) {
      groupToUpdate.owners.push(owner)
    } else {
      // No groups exist, need to create a new one
      const newGroup = {
        groupId: groupId || DEFAULT_GROUP_ID,
        owners: [owner] as MhrRegistrationHomeOwnersIF[]
      } as MhrRegistrationHomeOwnerGroupIF
      homeOwnerGroups.push(newGroup)
    }

    setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  const editHomeOwner = (updatedOwner: MhrRegistrationHomeOwnersIF, newGroupId: string) => {
    const homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]
    const groupIdOfOwner = getGroupForOwner(updatedOwner.id).groupId

    const groupToUpdate = homeOwnerGroups.find(
      group => group.groupId === groupIdOfOwner
    ) as MhrRegistrationHomeOwnerGroupIF

    if (groupToUpdate.groupId === newGroupId) {
      // need to update owner in the same group
      const i = findIndex(groupToUpdate.owners, { id: updatedOwner.id })
      set(groupToUpdate, `owners[${i}]`, updatedOwner)
      setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
    } else {
      // need to move the owner to new group
      remove(groupToUpdate.owners, owner => owner.id === updatedOwner.id)
      addOwnerToTheGroup(updatedOwner, newGroupId)
    }
  }

  // Remove Owner from the Group it belongs to
  const removeOwner = (owner: MhrRegistrationHomeOwnersIF) => {
    const homeOwnerGroups = [
      ...getMhrRegistrationHomeOwnerGroups.value
    ] as MhrRegistrationHomeOwnerGroupIF[]

    // find group id that owner belongs to
    const groupIdOfOwner = getGroupForOwner(owner.id)?.groupId || DEFAULT_GROUP_ID

    // find group to remove the owner from
    const groupToUpdate = homeOwnerGroups.find(
      group => group.groupId === groupIdOfOwner
    ) as MhrRegistrationHomeOwnerGroupIF

    // remove the owner from the group
    remove(groupToUpdate.owners, o => o.id === owner.id)
    setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  // Delete group with its owners
  const deleteGroup = (groupId: string): void => {
    const homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]
    remove(homeOwnerGroups, group => group.groupId === groupId)

    homeOwnerGroups.forEach((group, index) => {
      group.groupId = (index + 1).toString()
    })

    setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  const setGroupFractionalInterest = (groupId: string, fractionalData: MhrRegistrationFractionalOwnershipIF): void => {
    const homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]

    const allGroupsTotals = homeOwnerGroups.map(group => group.interestTotal)

    // check if dominator is already the same for all Groups
    const isAlreadyLCM = allGroupsTotals.includes(fractionalData.interestTotal)

    if (homeOwnerGroups.length > 1 && !isAlreadyLCM) {
      // Calculate common fractions for Groups
      const { updatedGroups, updatedFractionalData } = updateGroupsWithCommonFractionalInterest(
        homeOwnerGroups,
        fractionalData
      )
      const groupToUpdate = find(updatedGroups, { groupId: groupId }) as MhrRegistrationHomeOwnerGroupIF
      Object.assign(groupToUpdate, { ...updatedFractionalData })
      setMhrRegistrationHomeOwnerGroups(updatedGroups)
    } else {
      const groupToUpdate = find(homeOwnerGroups, { groupId: groupId }) as MhrRegistrationHomeOwnerGroupIF
      Object.assign(groupToUpdate, { ...fractionalData })
      setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
    }
  }

  /**
   * Utility method to calculate and update groups with lowest common denominator.
   * Used when multiple Home Owner Groups have different fractional interest totals.
   * To calculate lowest common denominator: multiply all denominators together and then
   * calculate numerator based on that number
   * @param currentHomeOwnerGroups - existing groups to be updated
   * @param currentFractionalData - fractional data of the group that is about to be updated
   * @returns object consisting of: existing groups with new factorial values and updated factorial data
   */
  const updateGroupsWithCommonFractionalInterest = (
    currentHomeOwnerGroups: Array<any>,
    currentFractionalData
  ): { updatedGroups: MhrRegistrationHomeOwnerGroupIF[]; updatedFractionalData } => {
    // Lowest Common Multiplier aka Common Denominator
    // Starts with 1 so it can be multiplied by all denominators
    let LCM = 1

    // Calculate Lowest Common Multiplier for all group that already exists
    // by multiplying all total interests
    currentHomeOwnerGroups.every((group: MhrRegistrationHomeOwnerGroupIF) => {
      LCM = LCM * Number(group.interestTotal)
    })

    // Since new fractional data is not included in any groups yet,
    // it needs to be calculated as well for LCM,
    // but only if new fractional total is not LCM already
    // e.g. 1/25, new factorial 1/5 - no need to find a new LCM, as it is 25 already
    if (LCM % currentFractionalData.interestTotal !== 0) {
      LCM = LCM * currentFractionalData.interestTotal
    }

    // Update all fractional amounts for groups that already exist
    const updatedGroups = currentHomeOwnerGroups.map(group => {
      const newNumerator = (LCM / group.interestTotal) * group.interestNumerator
      group.interestNumerator = newNumerator
      group.interestTotal = LCM
      return group
    })

    const updatedFractionalData = currentFractionalData

    // Update current fractional data with new values
    updatedFractionalData.interestNumerator =
      (LCM / currentFractionalData.interestTotal) * currentFractionalData.interestNumerator
    updatedFractionalData.interestTotal = LCM

    return { updatedGroups, updatedFractionalData }
  }

  // Do not show groups in the owner's table when there are no groups (e.g. after Group deletion)
  watch(
    () => getMhrRegistrationHomeOwnerGroups.value,
    () => {
      // set step validation for home owners
      var isHomeOwnersValid = showGroups.value ? !getTotalOwnershipAllocationStatus().hasTotalAllocationError : true
      if (getMhrRegistrationHomeOwnerGroups.value.length === 0 || !getMhrRegistrationHomeOwnerGroups.value[0].owners) {
        isHomeOwnersValid = false
      }

      if (getMhrRegistrationHomeOwnerGroups.value.length === 0 ||
        ((getMhrRegistrationHomeOwnerGroups.value.length === 1 && !getMhrRegistrationHomeOwners.value.address) &&
          getMhrRegistrationHomeOwnerGroups.value[0].owners.length <= 1 && getMhrRegistrationHomeOwnerGroups.value[0].interestNumerator === null)) {
        setShowGroups(false)
      } else {
        // update group tenancy for all groups
        getMhrRegistrationHomeOwnerGroups.value.every(group => set((group.type = getGroupTenancyType(group))))
        // check if at least one Owner Group has no owners. Used to display an error for the table.
        hasEmptyGroup.value = !getMhrRegistrationHomeOwnerGroups.value.every(group => group.owners.length > 0)
      }

      setValidation(MhrSectVal.HOME_OWNERS_VALID, MhrCompVal.OWNERS_VALID, isHomeOwnersValid)
    }
  )

  return {
    showGroups: readonly(showGroups),
    isGlobalEditingMode: readonly(isGlobalEditingMode),
    hasEmptyGroup: readonly(hasEmptyGroup),
    getSideTitle,
    getHomeTenancyType,
    getTotalOwnershipAllocationStatus,
    addOwnerToTheGroup,
    editHomeOwner,
    removeOwner,
    getGroupDropdownItems,
    getGroupForOwner,
    setShowGroups,
    setGlobalEditingMode,
    deleteGroup,
    setGroupFractionalInterest,
    getNumberOfGroups
  }
}
