import {
  MhrRegistrationTotalOwnershipAllocationIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF,
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

export function useHomeOwners (isMhrTransfer: boolean = false) {
  const {
    getMhrRegistrationHomeOwners,
    getMhrRegistrationHomeOwnerGroups,
    getMhrRegistrationValidationModel,
    getMhrTransferHomeOwnerGroups
  } = useGetters<any>([
    'getMhrRegistrationHomeOwners',
    'getMhrRegistrationHomeOwnerGroups',
    'getMhrRegistrationValidationModel',
    'getMhrTransferHomeOwnerGroups'
  ])

  const {
    setMhrRegistrationHomeOwnerGroups,
    setMhrTransferHomeOwnerGroups
  } = useActions<any>([
    'setMhrRegistrationHomeOwnerGroups',
    'setMhrTransferHomeOwnerGroups'
  ])

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
      // Added second condition, because when an owner exists as a Sole Ownership, editing and clicking Done,
      // will change status to Tenants in Common unless above logic is in place..
      return HomeTenancyTypes.SOLE
    } else if (numOfOwners > 1) {
      // More than one owner without groups showing
      return HomeTenancyTypes.JOINT
    }
    return HomeTenancyTypes.NA
  }

  const getGroupTenancyType = (group: MhrRegistrationHomeOwnerGroupIF): HomeTenancyTypes => {
    const numOfOwnersInGroup = group.owners.length

    if (group.interestNumerator) {
      return HomeTenancyTypes.COMMON
    } else if (numOfOwnersInGroup > 1) {
      return HomeTenancyTypes.JOINT
    } else if (numOfOwnersInGroup === 1) {
      return HomeTenancyTypes.SOLE
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
      hasTotalAllocationError: totalFractionalNominator !== fractionalDenominator,
      hasMinimumGroupsError: getMhrRegistrationHomeOwnerGroups.value.length < 2
    }
  }

  const hasMinimumGroups = (): boolean => {
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

  const getGroupForOwner = (ownerId: string, isTransfer = false): MhrRegistrationHomeOwnerGroupIF => {
    const homeOwners = isTransfer ? getMhrTransferHomeOwnerGroups.value : getMhrRegistrationHomeOwnerGroups.value

    return find(homeOwners, group => {
      return find(group.owners, { id: ownerId })
    })
  }

  const addOwnerToTheGroup = (owner: MhrRegistrationHomeOwnerIF, groupId: string, isTransfer = false) => {
    const homeOwnerGroups = isTransfer
      ? [...getMhrTransferHomeOwnerGroups.value]
      : [...getMhrRegistrationHomeOwnerGroups.value]

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
        owners: [owner] as MhrRegistrationHomeOwnerIF[]
      } as MhrRegistrationHomeOwnerGroupIF
      homeOwnerGroups.push(newGroup)
    }

    isTransfer
      ? setMhrTransferHomeOwnerGroups(homeOwnerGroups)
      : setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  const editHomeOwner = (updatedOwner: MhrRegistrationHomeOwnerIF, newGroupId: string, isTransfer = false) => {
    const homeOwnerGroups = isTransfer
      ? [...getMhrTransferHomeOwnerGroups.value]
      : [...getMhrRegistrationHomeOwnerGroups.value]
    const groupIdOfOwner = getGroupForOwner(updatedOwner.id, isTransfer).groupId

    const groupToUpdate = homeOwnerGroups.find(
      group => group.groupId === groupIdOfOwner
    ) as MhrRegistrationHomeOwnerGroupIF

    if (groupToUpdate.groupId === newGroupId) {
      // need to update owner in the same group
      const i = findIndex(groupToUpdate.owners, { id: updatedOwner.id })
      set(groupToUpdate, `owners[${i}]`, updatedOwner)

      isTransfer
        ? setMhrTransferHomeOwnerGroups(homeOwnerGroups)
        : setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
    } else {
      // need to move the owner to new group
      remove(groupToUpdate.owners, owner => owner.id === updatedOwner.id)
      addOwnerToTheGroup(updatedOwner, newGroupId, isTransfer)
    }
  }

  // Remove Owner from the Group it belongs to
  const removeOwner = (owner: MhrRegistrationHomeOwnerIF, isTransfer = false) => {
    const homeOwnerGroups = isTransfer
      ? [...getMhrTransferHomeOwnerGroups.value]
      : [...getMhrRegistrationHomeOwnerGroups.value]

    // find group id that owner belongs to
    const groupIdOfOwner = getGroupForOwner(owner.id, isTransfer)?.groupId || DEFAULT_GROUP_ID

    // find group to remove the owner from
    const groupToUpdate = homeOwnerGroups.find(
      group => group.groupId === groupIdOfOwner
    ) as MhrRegistrationHomeOwnerGroupIF

    // remove the owner from the group
    remove(groupToUpdate.owners, o => o.id === owner.id)
    isTransfer
      ? setMhrTransferHomeOwnerGroups(homeOwnerGroups)
      : setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  // Delete group with its owners
  const deleteGroup = (groupId: string, isTransfer = false): void => {
    const homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[] = isTransfer
      ? [...getMhrTransferHomeOwnerGroups.value]
      : [...getMhrRegistrationHomeOwnerGroups.value]

    remove(homeOwnerGroups, group => group.groupId === groupId)
    homeOwnerGroups.forEach((group, index) => {
      group.groupId = (index + 1).toString()
    })

    isTransfer
      ? setMhrTransferHomeOwnerGroups(homeOwnerGroups)
      : setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
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
      if (getMhrRegistrationHomeOwnerGroups.value.length === 0) {
        setShowGroups(false)
      } else {
        // update group tenancy for all groups
        getMhrRegistrationHomeOwnerGroups.value.every(group => set((group.type = getGroupTenancyType(group))))
        // check if at least one Owner Group has no owners. Used to display an error for the table.
        hasEmptyGroup.value = !getMhrRegistrationHomeOwnerGroups.value.every(group => group.owners.length > 0)
      }
    }
  )

  // Set Validations for Home Owners
  watch([hasEmptyGroup, showGroups, getMhrRegistrationHomeOwners, getMhrRegistrationHomeOwnerGroups], () => {
    let isHomeOwnersStepValid = true
    if (showGroups.value) {
      // groups must not be empty or have any fractional errors
      isHomeOwnersStepValid =
        !getTotalOwnershipAllocationStatus().hasMinimumGroupsError &&
        !getTotalOwnershipAllocationStatus().hasTotalAllocationError &&
        !hasEmptyGroup.value
    } else {
      // must have at least one owner with proper id
      isHomeOwnersStepValid = !!getMhrRegistrationHomeOwners.value.find(owner => owner.id)
    }
    setValidation(MhrSectVal.HOME_OWNERS_VALID, MhrCompVal.OWNERS_VALID, isHomeOwnersStepValid)
  })

  return {
    showGroups: readonly(showGroups),
    isGlobalEditingMode: readonly(isGlobalEditingMode),
    hasEmptyGroup: readonly(hasEmptyGroup),
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
    hasMinimumGroups
  }
}
