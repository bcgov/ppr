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

  const getGroupById = (groupId: number): MhrRegistrationHomeOwnerGroupIF =>
    getTransferOrRegistrationHomeOwnerGroups().find(group => group.groupId === groupId)

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
    let errorMsg, totalAllocationMsg
    const groups = getTransferOrRegistrationHomeOwnerGroups()
      .filter(group => group.action !== ActionTypes.REMOVED && !!group.interestNumerator && !!group.interestDenominator)
    const denominator = calcLcm(groups.map(group => group.interestDenominator))
    const nominators = groups.map(group => (group.interestNumerator / group.interestDenominator) * denominator)
    const totalNominator = nominators.reduce((a, b) => a + b, 0)

    // Determine allocation or error messaging
    if (totalNominator === denominator) totalAllocationMsg = 'Fully Allocated'
    else {
      totalAllocationMsg = simplifyFraction(totalNominator, denominator)
      errorMsg = `Total ownership interest is ${totalNominator > denominator ? 'over' : 'under'} allocated`
    }

    return {
      totalAllocation: totalAllocationMsg,
      hasTotalAllocationError: totalNominator !== denominator,
      allocationErrorMsg: errorMsg,
      hasMinimumGroupsError: groups.length < 2
    }
  }

  const hasMinimumGroups = (): boolean => {
    const groups = getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action !== ActionTypes.REMOVED)
    const hasNoGroups = [HomeTenancyTypes.SOLE, HomeTenancyTypes.JOINT].includes(getHomeTenancyType())
    return hasNoGroups || !groups || groups.length >= 2
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

  const undoGroupRemoval = (groupId: number = null, undoAllOwners: boolean = false): void => {
    let homeOwnerGroups = getMhrTransferHomeOwnerGroups.value
    // Set flag when there is undefined group interests
    const hasUndefinedGroups = hasUndefinedGroupInterest(homeOwnerGroups)

    homeOwnerGroups = homeOwnerGroups.reduce((homeOwners, group) => {
      if (group.groupId === groupId) {
        if (undoAllOwners) {
          const owners = group.owners.map(owner => { return { ...owner, action: null } })
          group = { ...group, owners: owners }
        }

        // Reset interest values when undefined groups exist and group removals are undone
        if (hasUndefinedGroups) {
          group = {
            ...group,
            interest: '',
            interestNumerator: null,
            interestDenominator: null,
            tenancySpecified: false
          }
        }

        const unmarkedGroup = {
          ...group,
          action: null
        }

        homeOwners.push(unmarkedGroup)
      } else homeOwners.push(group)

      return homeOwners
    }, [])

    setMhrTransferHomeOwnerGroups(homeOwnerGroups)
  }

  const hasRemovedAllHomeOwners = (homeOwners: MhrHomeOwnerGroupIF[]): boolean => {
    return homeOwners.every(group => group.action === ActionTypes.REMOVED)
  }

  const hasUndefinedGroupInterest = (homeOwnerGroups: MhrHomeOwnerGroupIF[]): boolean => {
    return homeOwnerGroups.some(group => !group.interestNumerator || !group.interestDenominator)
  }

  const setGroupFractionalInterest = (groupId: number, fractionalData: MhrRegistrationFractionalOwnershipIF): void => {
    const homeOwnerGroups = getTransferOrRegistrationHomeOwnerGroups()
    const groupToUpdate = find(homeOwnerGroups, { groupId: groupId }) as MhrRegistrationHomeOwnerGroupIF
    Object.assign(groupToUpdate, { ...fractionalData })
    const updatedOwnerGroups = [...homeOwnerGroups]

    setTransferOrRegistrationHomeOwnerGroups(updatedOwnerGroups)
  }

  /**
   * Utility method to calculate least common multiple.
   * @param numbers - an array of numbers to compute the lcm from.
   * @returns number - the least common multiple of the given numbers.
   */
  const calcLcm = (numbers: Array<number>): number => {
    const gcd = (a, b) => a ? gcd(b % a, a) : b
    const lcm = (a, b) => a * b / gcd(a, b)
    return numbers.length ? numbers.reduce(lcm) : null
  }

  /**
   * Utility method to simplify a fraction to its lowest terms.
   * @param numerator - the amount of parts taken of the denominator.
   * @param denominator - the total parts of the fraction.
   * @returns string - the lowest simplified terms of the fraction.
   */
  const simplifyFraction = (numerator, denominator): string => {
    const gcd = (a, b): number => {
      return b ? gcd(b, a % b) : a
    }

    return `${numerator / gcd(numerator, denominator)}/${denominator / gcd(numerator, denominator)}`
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
  watch([
    hasEmptyGroup,
    showGroups,
    getMhrRegistrationHomeOwners,
    getMhrRegistrationHomeOwnerGroups,
    isGlobalEditingMode],
  () => {
    let isHomeOwnersStepValid = true
    if (showGroups.value) {
      // groups must not be empty or have any fractional errors and add/edit form must be closed
      isHomeOwnersStepValid =
        !getTotalOwnershipAllocationStatus().hasMinimumGroupsError &&
        !getTotalOwnershipAllocationStatus().hasTotalAllocationError &&
        !hasEmptyGroup.value &&
        !isGlobalEditingMode.value
    } else {
      // must have at least one owner with proper id and add/edit form must be closed
      isHomeOwnersStepValid = !!getMhrRegistrationHomeOwners.value.find(owner => owner.ownerId) &&
                              !isGlobalEditingMode.value
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
    getGroupById,
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
    hasRemovedAllHomeOwners,
    hasUndefinedGroupInterest
  }
}
