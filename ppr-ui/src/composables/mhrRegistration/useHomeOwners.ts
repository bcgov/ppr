import { computed, reactive, readonly, ref, toRefs, watch } from 'vue'
import {
  MhrHomeOwnerGroupIF,
  MhrRegistrationFractionalOwnershipIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF,
  MhrRegistrationTotalOwnershipAllocationIF
} from '@/interfaces'
import { useStore } from '@/store/store'
import { ActionTypes, ApiTransferTypes, HomeOwnerPartyTypes, HomeTenancyTypes } from '@/enums'
import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'
import { useMhrValidations } from '@/composables'
import { find, findIndex, remove, set, uniq } from 'lodash'
import { storeToRefs } from 'pinia'
import { deepChangesComparison } from '@/utils'

const DEFAULT_GROUP_ID = 1

// Show or hide grouping of the Owners in the table
const showGroups = ref(false)
// Flag is any of the Groups has no Owners
const hasEmptyGroup = ref(false)

export function useHomeOwners (isMhrTransfer: boolean = false, isMhrCorrection: boolean = false) {
  // Composable Scoped State
  const localState = reactive({
    isGlobalEditingFlag: false,
  })

  const {
    // Actions
    setMhrRegistrationHomeOwnerGroups,
    setMhrTransferHomeOwnerGroups
  } = useStore()
  const {
    // Getters
    getMhrBaseline,
    getMhrRegistrationHomeOwners,
    getMhrRegistrationHomeOwnerGroups,
    getMhrRegistrationValidationModel,
    getMhrTransferHomeOwnerGroups,
    getMhrTransferHomeOwners,
    getMhrTransferCurrentHomeOwnerGroups,
    getMhrTransferType
  } = storeToRefs(useStore())

  // Get Transfer or Registration Home Owners
  const getTransferOrRegistrationHomeOwners = (): MhrRegistrationHomeOwnerIF[] =>
    isMhrTransfer ? getMhrTransferHomeOwners.value : getMhrRegistrationHomeOwners.value

  const getTransferOrRegistrationHomeOwnerGroups = (): MhrRegistrationHomeOwnerGroupIF[] =>
    isMhrTransfer ? getMhrTransferHomeOwnerGroups.value : getMhrRegistrationHomeOwnerGroups.value

  /**
   * Return the owner group snapshot by id.
   * @param groupId The group identifier
   */
  const getGroupById = (groupId: number): MhrRegistrationHomeOwnerGroupIF =>
    getTransferOrRegistrationHomeOwnerGroups().find(group => group.groupId === groupId)

  /**
   * Return the CURRENT owner group snapshot by id.
   * @param groupId The group identifier
   */
  const getCurrentGroupById = (groupId: number): MhrRegistrationHomeOwnerGroupIF => {
    return isMhrTransfer
      ? getMhrTransferCurrentHomeOwnerGroups.value[groupId - 1]
      : getMhrBaselineOwnerGroupById(groupId)
  }

  const setTransferOrRegistrationHomeOwnerGroups = (homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[]) =>
    isMhrTransfer ? setMhrTransferHomeOwnerGroups(homeOwnerGroups) : setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)

  const { setValidation } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

  // Show or hide groups in the owner's table
  const setShowGroups = show => {
    showGroups.value = show
  }

  // Set global editing to enable or disable all Edit buttons
  const setGlobalEditingMode = isEditing => {
    localState.isGlobalEditingFlag = isEditing
  }

  // Returns reactive global edit mode flag to enable or disable all Edit and dropdown buttons
  const isGlobalEditingMode = computed(() => {
    return localState.isGlobalEditingFlag
  })

  /** Returns the Home Tenancy Type based on the CURRENT state of the HomeOwners */
  const getHomeTenancyType = (): HomeTenancyTypes => {
    // check if there are any groups with mixed owner types for Sale or Gift transfers
    if (((isMhrTransfer && getMhrTransferType.value?.transferType === ApiTransferTypes.SALE_OR_GIFT) ||
        isMhrCorrection) && getTransferOrRegistrationHomeOwnerGroups().length === 1) {
      // git first group since there is only one group in this case
      const ownerTypes = getTransferOrRegistrationHomeOwnerGroups()[0].owners
        .filter(owner => owner.action !== ActionTypes.REMOVED)
        .map(owner => owner.partyType)

      const hasMixedOwners = (isMhrCorrection || ownerTypes.length === 1)
        ? false
        : uniq(ownerTypes).length > 1

      if (hasMixedOwners) {
        return HomeTenancyTypes.NA
      }
    }

    // Groups
    const groups = getTransferOrRegistrationHomeOwnerGroups().filter(groups => groups.action !== ActionTypes.REMOVED)

    // Variable to track if owners has a valid combination of Executor/Trustee/Admin (ETA) Owners
    const hasETA = getTransferOrRegistrationHomeOwnerGroups().some(group => hasExecutorTrusteeAdmin(group))
    const commonCondition = (isMhrTransfer || isMhrCorrection) ? groups.length > 1 : showGroups.value

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
    } else if (numOfOwners > 1 && !hasETA) {
      // More than one owner without groups showing
      return HomeTenancyTypes.JOINT
    }
    return HomeTenancyTypes.NA
  }

  const getGroupTenancyType = (group: MhrRegistrationHomeOwnerGroupIF): HomeTenancyTypes => {
    const numOfOwnersInGroup = group.owners.filter(owner => owner.action !== ActionTypes.REMOVED).length
    const hasETA = hasExecutorTrusteeAdmin(group)

    if (numOfOwnersInGroup > 1 && !hasETA) {
      return HomeTenancyTypes.JOINT
    } else if (getHomeTenancyType() === HomeTenancyTypes.SOLE) {
      return HomeTenancyTypes.SOLE
    } else {
      return HomeTenancyTypes.NA
    }
  }

  const hasExecutorTrusteeAdmin = (group: MhrRegistrationHomeOwnerGroupIF): boolean => {
    const executorTrusteeAdmin = [
      HomeOwnerPartyTypes.EXECUTOR,
      HomeOwnerPartyTypes.TRUSTEE,
      HomeOwnerPartyTypes.ADMINISTRATOR
    ]
    return group.owners.some(owner => executorTrusteeAdmin.includes(owner.partyType) &&
      owner.action !== ActionTypes.REMOVED)
  }

  /**
   * Get Ownership Allocation status object to conveniently show total allocation
   * and an allocation error status if exists
   */
  const getTotalOwnershipAllocationStatus = computed((): MhrRegistrationTotalOwnershipAllocationIF => {
    let errorMsg, totalAllocationMsg
    const groups = getTransferOrRegistrationHomeOwnerGroups()
      .filter(group => group.action !== ActionTypes.REMOVED && !!group.interestNumerator && !!group.interestDenominator)
    const denominator = calcLcm(groups.map(group => group.interestDenominator))
    const nominators = groups.map(group => (group.interestNumerator / group.interestDenominator) * denominator)
    const totalNominator = nominators.reduce((a, b) => a + b, 0)
    const hasTotalAllocationError = totalNominator !== denominator ||
      hasUndefinedGroupInterest(
        getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action !== ActionTypes.REMOVED)
      )

    // Determine allocation or error messaging
    if (!hasTotalAllocationError) totalAllocationMsg = 'Fully Allocated'
    else {
      totalAllocationMsg = simplifyFraction(totalNominator, denominator)
      errorMsg = `Total ownership interest is ${totalNominator > denominator ? 'over' : 'under'} allocated`
    }

    return {
      totalAllocation: totalAllocationMsg,
      hasTotalAllocationError,
      allocationErrorMsg: errorMsg,
      hasMinimumGroupsError: groups.length < 2
    }
  })

  const hasMinimumGroups = (): boolean => {
    const groups = getTransferOrRegistrationHomeOwnerGroups().filter(group => group.action !== ActionTypes.REMOVED)
    const hasNoGroups = [HomeTenancyTypes.SOLE, HomeTenancyTypes.JOINT].includes(getHomeTenancyType())
    return hasNoGroups || !groups || groups.length >= 2 ||
      (!showGroups.value && groups.length === 1)
  }

  const hasMixedOwnersInGroup = (groupId: number): boolean => {
    if (isMhrCorrection) return false
    const owners = getGroupById(groupId)?.owners
    if (owners?.length < 2) return false
    const partyType = owners?.[0].partyType
    return owners?.some(owner => owner.partyType !== partyType)
  }
  // WORKING WITH GROUPS

  const hasMixedOwnersInAGroup = (): boolean => {
    if (isMhrCorrection) return false
    return getTransferOrRegistrationHomeOwnerGroups().some(group => hasMixedOwnersInGroup(group.groupId) === true)
  }

  // Generate dropdown items for the group selection
  const getGroupDropdownItems = (isAddingHomeOwner: boolean, groupId: number): Array<any> => {
    // Make additional Group available in dropdown when adding a new home owner
    // or when there are more than one owner in the group

    let numOfAdditionalGroupsInDropdown = 0

    const homeOwnerGroups = getTransferOrRegistrationHomeOwnerGroups() as MhrRegistrationHomeOwnerGroupIF[]
    const removedOwners = homeOwnerGroups.filter(group => group.action === ActionTypes.REMOVED)
    const activeOwners = homeOwnerGroups.filter(group => group.action !== ActionTypes.REMOVED)

    if (isAddingHomeOwner && (showGroups.value || isMhrTransfer)) {
      numOfAdditionalGroupsInDropdown = 1
    } else {
      numOfAdditionalGroupsInDropdown =
        find(homeOwnerGroups, { groupId })?.owners.length > 1 ? 1 : 0
    }

    const dropDownItems = Array(homeOwnerGroups.length + numOfAdditionalGroupsInDropdown)
      .fill({})
      .map((v, i) => {
        const groupNumber = (activeOwners.findIndex(group => group.groupId === i + 1) + 1) || activeOwners.length + 1
        return { title: 'Group ' + groupNumber, value: (i + 1) }
      })

    // Remove first group option when there is existing SO/JT
    if (!showGroups.value && homeOwnerGroups.length && isMhrTransfer) dropDownItems.shift()

    // Handle Edit Defaults
    if (!dropDownItems.length) return [{ title: 'Group 1', value: DEFAULT_GROUP_ID }]

    // Only return groups that have NOT been REMOVED
    return dropDownItems.filter(item => {
      return !removedOwners.find(group => group.groupId === item.value)
    })
  }

  const getGroupForOwner = (ownerId: number): MhrRegistrationHomeOwnerGroupIF => {
    const homeOwners = getTransferOrRegistrationHomeOwnerGroups()

    return find(homeOwners, group => {
      return find(group.owners, { ownerId })
    })
  }

  const addOwnerToTheGroup = (owner: MhrRegistrationHomeOwnerIF, groupId: number) => {
    let homeOwnerGroups

    if (isMhrTransfer) {
      homeOwnerGroups = [...getMhrTransferHomeOwnerGroups.value]
      owner = { ...owner, action: ActionTypes.ADDED }
    } else {
      homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]
      if (isMhrCorrection) owner = { ...owner, action: ActionTypes.ADDED }
    }
    // For Mhr Transfers with Removed Groups, assign a sequential groupId
    // If WILL flow, add new executor to existing group instead of incrementing the group
    let transferDefaultId = groupId
    if (getMhrTransferType.value?.transferType !== ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL &&
      getMhrTransferType.value?.transferType !== ApiTransferTypes.TO_ADMIN_NO_WILL) {
      transferDefaultId = homeOwnerGroups.find(group => group.action !== ActionTypes.REMOVED)?.groupId ||
      homeOwnerGroups.filter(group => group.action === ActionTypes.REMOVED).length + 1
    }
    const fallBackId = (isMhrTransfer || isMhrCorrection) ? transferDefaultId : DEFAULT_GROUP_ID

    // Try to find a group to add the owner
    const groupToUpdate =
      homeOwnerGroups.find(
        (group: MhrRegistrationHomeOwnerGroupIF) => group.groupId === (groupId || fallBackId)
      ) || ({} as MhrRegistrationHomeOwnerGroupIF)

    // Allow update to "REMOVED" group if WILL flow
    if (groupToUpdate.owners &&
        (groupToUpdate.action !== ActionTypes.REMOVED ||
         (getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL ||
          getMhrTransferType.value?.transferType === ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL))) {
      groupToUpdate.owners.push({ ...owner, groupId: groupId || fallBackId })
    } else {
      // No groups exist, need to create a new one
      const newGroup = {
        groupId: groupId || fallBackId,
        owners: [owner] as MhrRegistrationHomeOwnerIF[]
      } as MhrRegistrationHomeOwnerGroupIF

      // Apply an ADDED action for new groups in Transfers or Corrections
      if (isMhrTransfer || isMhrCorrection) newGroup.action = ActionTypes.ADDED

      homeOwnerGroups.push(newGroup)
    }

    setTransferOrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  const editHomeOwner = (updatedOwner: MhrRegistrationHomeOwnerIF, groupId: number) => {
    const homeOwnerGroups = isMhrTransfer
      ? [...getMhrTransferHomeOwnerGroups.value]
      : [...getMhrRegistrationHomeOwnerGroups.value]
    const groupIdOfOwner = getGroupForOwner(updatedOwner.ownerId).groupId

    const groupToUpdate = homeOwnerGroups.find(
      group => group.groupId === groupIdOfOwner
    ) as MhrRegistrationHomeOwnerGroupIF

    if (groupToUpdate.groupId === groupId) {
      // need to update owner in the same group
      const i = findIndex(groupToUpdate.owners, { ownerId: updatedOwner.ownerId })
      set(groupToUpdate, `owners[${i}]`, updatedOwner)

      if (!groupToUpdate.interestNumerator && !groupToUpdate.interestDenominator &&
        groupToUpdate.owners.every(owner => owner.action === ActionTypes.REMOVED &&
        getMhrTransferType.value?.transferType !== ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL &&
        getMhrTransferType.value?.transferType !== ApiTransferTypes.TO_ADMIN_NO_WILL)) {
        set(groupToUpdate, 'action', ActionTypes.REMOVED)
      }

      setTransferOrRegistrationHomeOwnerGroups(homeOwnerGroups)
    } else {
      // need to move the owner to new group
      remove(groupToUpdate.owners, owner => owner.ownerId === updatedOwner.ownerId)
      addOwnerToTheGroup(updatedOwner, groupId)
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
    setTransferOrRegistrationHomeOwnerGroups(homeOwnerGroups)
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

    setTransferOrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  const markGroupForRemoval = (groupId: number = null, removeAll: boolean = false): void => {
    // Filter all ADDED groups when removing all groups
    const ownerGroups = removeAll
      ? getTransferOrRegistrationHomeOwnerGroups()
        .filter(group => group.action !== ActionTypes.ADDED)
      : getTransferOrRegistrationHomeOwnerGroups()

    // Apply Removed action to all owners being marked for removal (single or all)
    const homeOwnerGroups = ownerGroups.reduce((homeOwners, group) => {
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

    setTransferOrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  const undoGroupChanges = (groupId: number = null, undoAllOwners: boolean = false): void => {
    const homeOwnerGroups = getTransferOrRegistrationHomeOwnerGroups().reduce((homeOwners, group) => {
      if (group.groupId === groupId) {
        // Restore owners as well
        if (undoAllOwners) {
          const owners = group.owners.map(owner => { return { ...owner, action: null } })
          group = { ...group, owners }
        }

        const unmarkedGroup = {
          ...group,
          interestNumerator: getCurrentGroupById(groupId)?.interestNumerator,
          interestDenominator: getCurrentGroupById(groupId)?.interestDenominator,
          action: null
        }

        homeOwners.push(unmarkedGroup)
      } else homeOwners.push(group)

      return homeOwners
    }, [])

    setTransferOrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  const hasRemovedAllHomeOwners = (homeOwners: MhrRegistrationHomeOwnerIF[]): boolean => {
    return homeOwners.every(group => group.action === ActionTypes.REMOVED)
  }

  const hasRemovedAllHomeOwnerGroups = (): boolean => {
    return getTransferOrRegistrationHomeOwnerGroups().every(group => group.action === ActionTypes.REMOVED)
  }

  const hasUndefinedGroupInterest = (homeOwnerGroups: MhrHomeOwnerGroupIF[]): boolean => {
    return homeOwnerGroups.some(group => !group.interestNumerator || !group.interestDenominator)
  }

  const setGroupFractionalInterest =
    (groupId: number, fractionalData: MhrRegistrationFractionalOwnershipIF, hasChanges: boolean = false): void => {
      const homeOwnerGroups = getTransferOrRegistrationHomeOwnerGroups()
      const groupToUpdate = find(homeOwnerGroups, { groupId }) as MhrRegistrationHomeOwnerGroupIF

      Object.assign(groupToUpdate, {
        ...fractionalData,
        ...(hasChanges && {
          action: isMhrTransfer
            ? ActionTypes.CHANGED
            : isMhrCorrection ? ActionTypes.CORRECTED : ActionTypes.EDITED
        })
      })

      const updatedOwnerGroups = [...homeOwnerGroups]
      setTransferOrRegistrationHomeOwnerGroups(updatedOwnerGroups)
    }

  /**
   * Return the baseline owners snapshot by id.
   * @param ownerId The owner identifier
   */
  const getMhrBaselineOwnerById = (ownerId: number): MhrRegistrationHomeOwnerIF | undefined =>{
    return getMhrBaseline.value?.ownerGroups.flatMap(group => group.owners).find(owner => owner.ownerId === ownerId)
  }

  /**
   * Return the baseline owner group snapshot by id.
   * @param groupId The group identifier
   */
  const getMhrBaselineOwnerGroupById = (groupId: number): MhrRegistrationHomeOwnerGroupIF => {
    return getMhrBaseline.value?.ownerGroups[groupId-1]
  }

  /** Return true if the specified owner has been modified from current state **/
  const isCorrectedOwner = (owner: MhrRegistrationHomeOwnerIF): boolean => {
    const currentOwner = getMhrBaselineOwnerById(owner.ownerId)
    const isEqualName = !!owner.individualName
      ? deepChangesComparison(currentOwner.individualName, owner.individualName)
      : deepChangesComparison(currentOwner.organizationName, owner.organizationName)

    return isEqualName ||
      deepChangesComparison(currentOwner.address, owner.address) ||
      deepChangesComparison(currentOwner.phoneNumber, owner.phoneNumber) ||
      deepChangesComparison(currentOwner.phoneExtension, owner.phoneExtension) ||
      deepChangesComparison(currentOwner.suffix, owner.suffix) ||
      deepChangesComparison(currentOwner.partyType, owner.partyType)
  }

  const isCorrectedOwnerGroup = (group: MhrHomeOwnerGroupIF): boolean => {
    return [ActionTypes.CORRECTED, ActionTypes.EDITED].includes(group.action)
  }

  /**
   * Return the group number as it correlates to its current place in the active owners.
   * Will return the groupId when editing or a new groupId when creating a new group.
   * @param groupId The groups identifier
   */
  const getGroupNumberById = (groupId: number): number => {
    const activeOwnerGroups = getTransferOrRegistrationHomeOwnerGroups()
      .filter(group => group.action !== ActionTypes.REMOVED)

    return (activeOwnerGroups.findIndex(group => group.groupId === groupId)) + 1 || activeOwnerGroups.length + 1
  }

  /**
   * Utility method to calculate the least common multiple.
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
        hasEmptyGroup.value = !getTransferOrRegistrationHomeOwnerGroups().filter(group =>
          group.action !== ActionTypes.REMOVED).every(group => group.owners.filter(
              owner => owner.action !== ActionTypes.REMOVED).length > 0
        )
      }
    }
  )

  // Set Validations for HomeOwners
  watch([
      hasEmptyGroup,
      showGroups,
      getMhrRegistrationHomeOwners,
      getMhrRegistrationHomeOwnerGroups,
      isGlobalEditingMode
    ],
    () => {
    let isHomeOwnersStepValid
    if (showGroups.value && getMhrRegistrationHomeOwnerGroups.value.some(group =>
      !group.action || (group.action === ActionTypes.ADDED && !!group.interest))
    ) {
      const totalAllocationStatus = getTotalOwnershipAllocationStatus
      // groups must not be empty or have any fractional errors and add/edit form must be closed
      isHomeOwnersStepValid =
        !totalAllocationStatus.value.hasMinimumGroupsError &&
        !totalAllocationStatus.value.hasTotalAllocationError &&
        !hasEmptyGroup.value &&
        !isGlobalEditingMode.value &&
        !hasMixedOwnersInAGroup()
    } else {
      // must have at least one owner with proper id and add/edit form must be closed
      isHomeOwnersStepValid = !!getMhrRegistrationHomeOwners.value.filter(owner => owner.action !== ActionTypes.REMOVED)
          .find(owner => owner.ownerId) && !isGlobalEditingMode.value && !hasMixedOwnersInAGroup()
    }
    setValidation(MhrSectVal.HOME_OWNERS_VALID, MhrCompVal.OWNERS_VALID, isHomeOwnersStepValid)
  }, { immediate: isMhrCorrection })

  return {
    showGroups: readonly(showGroups),
    isGlobalEditingMode: readonly(isGlobalEditingMode),
    hasEmptyGroup: readonly(hasEmptyGroup),
    getHomeTenancyType,
    getMhrBaselineOwnerById,
    isCorrectedOwner,
    isCorrectedOwnerGroup,
    getTotalOwnershipAllocationStatus,
    addOwnerToTheGroup,
    editHomeOwner,
    removeOwner,
    getGroupDropdownItems,
    getGroupForOwner,
    getGroupById,
    getGroupNumberById,
    getCurrentGroupById,
    setShowGroups,
    setGlobalEditingMode,
    deleteGroup,
    setGroupFractionalInterest,
    hasMinimumGroups,
    hasMixedOwnersInAGroup,
    hasMixedOwnersInGroup,
    getGroupTenancyType,
    getTransferOrRegistrationHomeOwners,
    getTransferOrRegistrationHomeOwnerGroups,
    markGroupForRemoval,
    undoGroupChanges,
    hasRemovedAllHomeOwners,
    hasRemovedAllHomeOwnerGroups,
    hasUndefinedGroupInterest,
    ...toRefs(localState)
  }
}
