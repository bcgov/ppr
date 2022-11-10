import {
  MhrHomeOwnerGroupIF,
  MhrRegistrationFractionalOwnershipIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF,
  MhrRegistrationTotalOwnershipAllocationIF
} from '@/interfaces'
import '@/utils/use-composition-api'

import { readonly, ref, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { ActionTypes, HomeTenancyTypes } from '@/enums'
import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'
import { useMhrValidations } from '@/composables'
import { find, findIndex, remove, set, sumBy } from 'lodash'

const DEFAULT_GROUP_ID = 1

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
    getMhrTransferHomeOwnerGroups,
    getMhrTransferHomeOwners
  } = useGetters<any>([
    'getMhrRegistrationHomeOwners',
    'getMhrRegistrationHomeOwnerGroups',
    'getMhrRegistrationValidationModel',
    'getMhrTransferHomeOwnerGroups',
    'getMhrTransferHomeOwners'
  ])

  const {
    setMhrRegistrationHomeOwnerGroups,
    setMhrTransferHomeOwnerGroups
  } = useActions<any>([
    'setMhrRegistrationHomeOwnerGroups',
    'setMhrTransferHomeOwnerGroups'
  ])

  // Get Transfer or Registration Home Owners
  const getTransferOrRegistrationHomeOwners = (): MhrRegistrationHomeOwnerIF[] =>
    isMhrTransfer ? getMhrTransferHomeOwners.value : getMhrRegistrationHomeOwners.value

  const getTransferOrRegistrationHomeOwnerGroups = (): MhrRegistrationHomeOwnerGroupIF[] =>
    isMhrTransfer ? getMhrTransferHomeOwnerGroups.value : getMhrRegistrationHomeOwnerGroups.value

  const setTransferOrRegistrationHomeOwnerGroups = (homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[]) =>
    isMhrTransfer ? setMhrTransferHomeOwnerGroups(homeOwnerGroups) : setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)

  const { setValidation } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

  // Show or hide groups in the owner's table
  const setShowGroups = show => {
    showGroups.value = show
  }

  // Set global editing to enable or disable all Edit buttons
  const setGlobalEditingMode = isEditing => {
    isGlobalEditingMode.value = isEditing
  }

  const getHomeTenancyType = (): HomeTenancyTypes => {
    // Groups
    const groups = getTransferOrRegistrationHomeOwnerGroups().filter(owner => owner.action !== ActionTypes.REMOVED)
    const commonCondition = isMhrTransfer ? groups.length > 1 : showGroups.value

    // Special case where a defined Group is orphaned using remove functionality, we want to preserve the Group Type.
    const isSingleInvalidGroup = !!groups[0]?.interestNumerator && !!groups[0]?.interestDenominator

    // Owners
    const owners = getTransferOrRegistrationHomeOwners().filter(owner => owner.action !== ActionTypes.REMOVED)
    const numOfOwners = owners.length

    if (commonCondition || isSingleInvalidGroup) {
      // At leas one group showing with one or more owners
      return HomeTenancyTypes.COMMON
    } else if (numOfOwners === 1 && owners[0]?.address) {
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
    const numOfOwnersInGroup = group.owners.filter(owner => owner.action !== ActionTypes.REMOVED).length

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
    const groups = getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action !== ActionTypes.REMOVED)

    // Sum up all 'interestNumerator' values in different Home Owner groups with a help of sumBy() function from lodash
    const totalFractionalNominator = sumBy(groups, 'interestNumerator')
    const fractionalDenominator = groups[0]?.interestDenominator || null

    return {
      totalAllocation: totalFractionalNominator + '/' + fractionalDenominator,
      hasTotalAllocationError: totalFractionalNominator !== fractionalDenominator,
      hasMinimumGroupsError: groups.length < 2
    }
  }

  const hasMinimumGroups = (): boolean => {
    return !getTransferOrRegistrationHomeOwnerGroups() || getTransferOrRegistrationHomeOwnerGroups().length < 2
  }
  // WORKING WITH GROUPS

  // Generate dropdown items for the group selection
  const getGroupDropdownItems = (isAddingHomeOwner: Boolean, groupId: number): Array<any> => {
    // Make additional Group available in dropdown when adding a new home owner
    // or when there are more than one owner in the group

    let numOfAdditionalGroupsInDropdown = 0

    const homeOwnerGroups = getTransferOrRegistrationHomeOwnerGroups()
    const removedOwners = homeOwnerGroups.filter(group => group.action === ActionTypes.REMOVED)

    if (isAddingHomeOwner) {
      numOfAdditionalGroupsInDropdown = 1
    } else {
      numOfAdditionalGroupsInDropdown =
        find(homeOwnerGroups, { groupId: groupId })?.owners.length > 1 ? 1 : 0
    }

    if (showGroups.value) {
      const dropDownItems = Array(homeOwnerGroups.length + numOfAdditionalGroupsInDropdown)
        .fill({})
        .map((v, i) => {
          return { text: 'Group ' + (i + 1), value: (i + 1) }
        })

      // Only return groups that have NOT been REMOVED
      return dropDownItems.filter(item => !removedOwners.find(group => group.groupId === item.value))
    } else {
      return [
        {
          text: 'Group 1',
          value: DEFAULT_GROUP_ID
        }
      ]
    }
  }

  const getGroupForOwner = (ownerId: number): MhrRegistrationHomeOwnerGroupIF => {
    const homeOwners = getTransferOrRegistrationHomeOwnerGroups()

    return find(homeOwners, group => {
      return find(group.owners, { ownerId: ownerId })
    })
  }

  const addOwnerToTheGroup = (owner: MhrRegistrationHomeOwnerIF, groupId: number) => {
    let homeOwnerGroups

    if (isMhrTransfer) {
      homeOwnerGroups = [...getMhrTransferHomeOwnerGroups.value]
      owner = { ...owner, action: ActionTypes.ADDED }
    } else {
      homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]
    }
    // For Mhr Transfers with Removed Groups, assign a sequential groupId
    const transferDefaultId = homeOwnerGroups.find(group => group.action !== ActionTypes.REMOVED)?.groupId ||
      homeOwnerGroups.filter(group => group.action === ActionTypes.REMOVED).length + 1
    const fallBackId = isMhrTransfer ? transferDefaultId : DEFAULT_GROUP_ID

    // Try to find a group to add the owner
    const groupToUpdate =
      homeOwnerGroups.find(
        (group: MhrRegistrationHomeOwnerGroupIF) => group.groupId === (groupId || fallBackId)
      ) || ({} as MhrRegistrationHomeOwnerGroupIF)

    if (groupToUpdate.owners && groupToUpdate.action !== ActionTypes.REMOVED) {
      groupToUpdate.owners.push(owner)
    } else {
      // No groups exist, need to create a new one
      const newGroup = {
        groupId: groupId || fallBackId,
        owners: [owner] as MhrRegistrationHomeOwnerIF[]
      } as MhrRegistrationHomeOwnerGroupIF

      // Apply an ADDED action for new groups in Transfers
      if (isMhrTransfer) newGroup.action = ActionTypes.ADDED

      homeOwnerGroups.push(newGroup)
    }

    isMhrTransfer
      ? setMhrTransferHomeOwnerGroups(homeOwnerGroups)
      : setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  const editHomeOwner = (updatedOwner: MhrRegistrationHomeOwnerIF, newGroupId: number) => {
    const homeOwnerGroups = isMhrTransfer
      ? [...getMhrTransferHomeOwnerGroups.value]
      : [...getMhrRegistrationHomeOwnerGroups.value]
    const groupIdOfOwner = getGroupForOwner(updatedOwner.ownerId).groupId

    const groupToUpdate = homeOwnerGroups.find(
      group => group.groupId === groupIdOfOwner
    ) as MhrRegistrationHomeOwnerGroupIF

    if (groupToUpdate.groupId === newGroupId) {
      // need to update owner in the same group
      const i = findIndex(groupToUpdate.owners, { ownerId: updatedOwner.ownerId })
      set(groupToUpdate, `owners[${i}]`, updatedOwner)

      isMhrTransfer
        ? setMhrTransferHomeOwnerGroups(homeOwnerGroups)
        : setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
    } else {
      // need to move the owner to new group
      remove(groupToUpdate.owners, owner => owner.ownerId === updatedOwner.ownerId)
      addOwnerToTheGroup(updatedOwner, newGroupId)
    }
  }

  // Remove Owner from the Group it belongs to
  const removeOwner = (owner: MhrRegistrationHomeOwnerIF) => {
    const homeOwnerGroups = isMhrTransfer
      ? [...getMhrTransferHomeOwnerGroups.value]
      : [...getMhrRegistrationHomeOwnerGroups.value]

    // find group id that owner belongs to
    const groupIdOfOwner = getGroupForOwner(owner.ownerId)?.groupId || DEFAULT_GROUP_ID

    // find group to remove the owner from
    const groupToUpdate = homeOwnerGroups.find(
      group => group.groupId === groupIdOfOwner
    ) as MhrRegistrationHomeOwnerGroupIF

    // remove the owner from the group
    remove(groupToUpdate.owners, o => o.ownerId === owner.ownerId)
    isMhrTransfer
      ? setMhrTransferHomeOwnerGroups(homeOwnerGroups)
      : setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  // Delete group with its owners
  const deleteGroup = (groupId: number): void => {
    const homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[] = isMhrTransfer
      ? [...getMhrTransferHomeOwnerGroups.value]
      : [...getMhrRegistrationHomeOwnerGroups.value]

    remove(homeOwnerGroups, group => group.groupId === groupId)
    homeOwnerGroups.forEach((group, index) => {
      group.groupId = (index + 1)
    })

    isMhrTransfer
      ? setMhrTransferHomeOwnerGroups(homeOwnerGroups)
      : setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  const markGroupForRemoval = (groupId: number = null, removeAll: boolean = false): void => {
    // Filter all ADDED groups when removing all groups
    const ownerGroups = removeAll
      ? getMhrTransferHomeOwnerGroups.value.filter(group => group.action !== ActionTypes.ADDED)
      : getMhrTransferHomeOwnerGroups.value

    // Apply Removed action to all owners being marked for removal (single or all)
    const homeOwners = ownerGroups.reduce((homeOwners, group) => {
      if (group.groupId === groupId || removeAll) {
        const removedGroup = {
          ...group,
          action: ActionTypes.REMOVED,
          owners: group.owners.filter(owner => owner.action !== ActionTypes.ADDED)
            .map(owner => {
              return { ...owner, action: ActionTypes.REMOVED }
            })
        }
        homeOwners.push(removedGroup)
      } else homeOwners.push(group)

      return homeOwners
    }, [])

    setMhrTransferHomeOwnerGroups(homeOwners)
  }

  const undoGroupRemoval = (groupId: number = null): void => {
    const homeOwners = getMhrTransferHomeOwnerGroups.value.reduce((homeOwners, group) => {
      if (group.groupId === groupId) {
        const unmarkedGroup = {
          ...group,
          action: null
        }
        homeOwners.push(unmarkedGroup)
      } else homeOwners.push(group)

      return homeOwners
    }, [])

    setMhrTransferHomeOwnerGroups(homeOwners)
  }

  const hasRemovedAllHomeOwners = (homeOwners: MhrHomeOwnerGroupIF[]): boolean => {
    return homeOwners.every(group => group.action === ActionTypes.REMOVED || group.action === ActionTypes.ADDED)
  }

  const setGroupFractionalInterest = (groupId: number, fractionalData: MhrRegistrationFractionalOwnershipIF): void => {
    const homeOwnerGroups = getTransferOrRegistrationHomeOwnerGroups()

    const allGroupsTotals = homeOwnerGroups.map(group => group.interestDenominator)

    // check if dominator is already the same for all Groups
    const isAlreadyLCM = allGroupsTotals.includes(fractionalData.interestDenominator)

    if (homeOwnerGroups.length > 1 && !isAlreadyLCM) {
      // Calculate common fractions for Groups
      const { updatedGroups, updatedFractionalData } = updateGroupsWithCommonFractionalInterest(
        homeOwnerGroups,
        fractionalData
      )
      const groupToUpdate = find(updatedGroups, { groupId: groupId }) as MhrRegistrationHomeOwnerGroupIF
      Object.assign(groupToUpdate, { ...updatedFractionalData })
      setTransferOrRegistrationHomeOwnerGroups(updatedGroups)
    } else {
      const groupToUpdate = find(homeOwnerGroups, { groupId: groupId }) as MhrRegistrationHomeOwnerGroupIF
      Object.assign(groupToUpdate, { ...fractionalData })
      setTransferOrRegistrationHomeOwnerGroups(homeOwnerGroups)
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
      LCM = LCM * Number(group.interestDenominator)
    })

    // Since new fractional data is not included in any groups yet,
    // it needs to be calculated as well for LCM,
    // but only if new fractional total is not LCM already
    // e.g. 1/25, new factorial 1/5 - no need to find a new LCM, as it is 25 already
    if (LCM % currentFractionalData.interestDenominator !== 0) {
      LCM = LCM * currentFractionalData.interestDenominator
    }

    // Update all fractional amounts for groups that already exist
    const updatedGroups = currentHomeOwnerGroups.map(group => {
      const newNumerator = (LCM / group.interestDenominator) * group.interestNumerator
      group.interestNumerator = newNumerator
      group.interestDenominator = LCM
      return group
    })

    const updatedFractionalData = currentFractionalData

    // Update current fractional data with new values
    updatedFractionalData.interestNumerator =
      (LCM / currentFractionalData.interestDenominator) * currentFractionalData.interestNumerator
    updatedFractionalData.interestDenominator = LCM

    return { updatedGroups, updatedFractionalData }
  }

  // Do not show groups in the owner's table when there are no groups (e.g. after Group deletion)
  watch(
    () => getTransferOrRegistrationHomeOwnerGroups(),
    () => {
      if (getTransferOrRegistrationHomeOwnerGroups().length === 0) {
        setShowGroups(false)
      } else {
        // update group tenancy for all groups
        getTransferOrRegistrationHomeOwnerGroups().every(group => set((group.type = getGroupTenancyType(group))))
        // check if at least one Owner Group has no owners. Used to display an error for the table.
        hasEmptyGroup.value = !getTransferOrRegistrationHomeOwnerGroups().every(group => group.owners.length > 0)
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
      isHomeOwnersStepValid = !!getMhrRegistrationHomeOwners.value.find(owner => owner.ownerId)
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
    hasMinimumGroups,
    getGroupTenancyType,
    getTransferOrRegistrationHomeOwners,
    getTransferOrRegistrationHomeOwnerGroups,
    markGroupForRemoval,
    undoGroupRemoval,
    hasRemovedAllHomeOwners
  }
}
