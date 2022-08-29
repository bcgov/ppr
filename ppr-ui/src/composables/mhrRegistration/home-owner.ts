import {
  MhrRegistrationFractionalOwnershipIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnersIF
} from '@/interfaces'
import '@/utils/use-composition-api'

import { ref, computed, readonly, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { find, remove, set, findIndex } from 'lodash'

const DEFAULT_GROUP_ID = '1'

// Show or hide grouping of the Owners in the table
const showGroups = ref(false)
// Set global edit mode to enable or disable all Edit and dropdown buttons
const isGlobalEditingMode = ref(false)

export function useHomeOwners (isPerson: boolean = false, isEditMode: boolean = false) {
  const { getMhrRegistrationHomeOwners, getMhrRegistrationHomeOwnerGroups } = useGetters<any>([
    'getMhrRegistrationHomeOwners',
    'getMhrRegistrationHomeOwnerGroups'
  ])

  const { setMhrRegistrationHomeOwnerGroups } = useActions<any>([
    'setMhrRegistrationHomeOwnerGroups'
  ])

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

  const getHomeTenancyType = (): string => {
    const numOfGroups = getMhrRegistrationHomeOwnerGroups.value.length
    const numOfOwners = getMhrRegistrationHomeOwners.value?.length

    // One Group with multiple owners
    if (numOfGroups === 1 && numOfOwners > 1 && showGroups.value) return 'Joint Tenants'
    // More than one Group
    if (numOfGroups > 1 && showGroups.value) return 'Tenants In Common'
    // No owners added
    if (numOfOwners === 0) return 'N/A'
    // One or more Owner
    return numOfOwners === 1 ? 'Sole Ownership' : 'Joint Tenants'
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

    removeEmptyGroups()
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

    // if there are no more owners in the group - delete the Group as well.
    if (groupToUpdate.owners.length === 0) {
      removeEmptyGroups()
    }
  }

  // Remove all groups without owners
  const removeEmptyGroups = (): void => {
    const homeOwnerGroups = [
      ...getMhrRegistrationHomeOwnerGroups.value
    ] as MhrRegistrationHomeOwnerGroupIF[]

    // find all groups with at least one owner
    const newOwnerGroups = homeOwnerGroups.filter(group => group.owners.length > 0)
    // update owner group ids with new values
    // to make them sequential again (e.g groups 1,3,5 -> 1,2,3)
    newOwnerGroups.forEach((group, index) => {
      group.groupId = (index + 1).toString()
    })

    setMhrRegistrationHomeOwnerGroups(newOwnerGroups)
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

  const setGroupFractionalInterest = (groupId: string, fractionalData): void => {
    const homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]

    const allGroupsTotals = homeOwnerGroups.map(group => group.interestTotal)

    // check if dominator is already the same for all Groups
    const isAlreadyLCM = allGroupsTotals.includes(fractionalData.interestTotal.toString())

    if (homeOwnerGroups.length > 1 && !isAlreadyLCM) {
      // Calculate common fractions for Groups
      const { updatedGroups, updatedFractionalData } = updateGroupsWithCommonFractionalInterest(
        homeOwnerGroups,
        fractionalData
      )
      const groupToUpdate = find(updatedGroups, { groupId: groupId })
      Object.assign(groupToUpdate, { ...updatedFractionalData })
      setMhrRegistrationHomeOwnerGroups(updatedGroups)
    } else {
      const groupToUpdate = find(homeOwnerGroups, { groupId: groupId })
      Object.assign(groupToUpdate, { ...fractionalData })
      setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
    }
  }

  /**
   * Utility method to calculate and update groups with lowest common denominator.
   * Used when multiple Home Owner Groups have different fractional interest totals.
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

    // Calculate LCM for all group that already exists
    // by multiplying all total interests
    currentHomeOwnerGroups.every((group: MhrRegistrationHomeOwnerGroupIF) => {
      LCM = LCM * Number(group.interestTotal)
    })

    // Since new fractional data is not included in any groups yet,
    // it needs to be calculated as well for LCM,
    // but only if new fractional total couldn't be part of LCM
    // e.g. 1/25, new factorial 1/5 - no need to find a new LCM, as it is 25 already
    if (LCM % currentFractionalData.interestTotal !== 0) {
      LCM = LCM * currentFractionalData.interestTotal
    }

    // Update all fractional amounts for groups that already exist
    const updatedGroups = currentHomeOwnerGroups.map(group => {
      const newNumerator = (LCM / group.interestTotal) * group.interestNumerator
      group.interestNumerator = newNumerator.toString()
      group.interestTotal = LCM.toString()
      return group
    })

    const updatedFractionalData = currentFractionalData

    // Update current fractional data with new values
    updatedFractionalData.interestNumerator = (
      (LCM / currentFractionalData.interestTotal) *
      currentFractionalData.interestNumerator
    ).toString()
    updatedFractionalData.interestTotal = LCM.toString()

    return { updatedGroups, updatedFractionalData }
  }

  // Do not show groups in the owner's table when there are no groups (e.g. after Group deletion)
  watch(
    () => getMhrRegistrationHomeOwnerGroups.value,
    () => {
      if (getMhrRegistrationHomeOwnerGroups.value.length === 0) {
        setShowGroups(false)
      }
    }
  )

  return {
    showGroups: readonly(showGroups),
    isGlobalEditingMode: readonly(isGlobalEditingMode),
    getSideTitle,
    getHomeTenancyType,
    addOwnerToTheGroup,
    editHomeOwner,
    removeOwner,
    getGroupDropdownItems,
    getGroupForOwner,
    setShowGroups,
    setGlobalEditingMode,
    removeEmptyGroups,
    deleteGroup,
    setGroupFractionalInterest
  }
}
