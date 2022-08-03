import {
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnersIF
} from '@/interfaces'
import '@/utils/use-composition-api'

import { ref, computed, readonly } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { find, remove, set, findIndex } from 'lodash'

// when home owners not added to any groups
// then do not show it on the UI
const showGroupsUI = ref(false)
const DEFAULT_GROUP_ID = '1'

export function useHomeOwners (
  isPerson: boolean = false,
  isEditMode: boolean = false
) {
  const { getMhrRegistrationHomeOwnerGroups } = useGetters<any>([
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

  const setShowGroupsUI = show => {
    showGroupsUI.value = show
  }

  // WORKING WITH GROUPS FUNCTIONS

  // Generate dropdown items for the group selection
  const getGroupsDropdownItems = (isAddingHomeOwner: Boolean): Array<any> => {
    // Make additional Group available in dropdown when adding a new home owner
    // const additionalGroup = isAddingHomeOwner ? 1 : 0

    if (showGroupsUI.value) {
      return Array(getMhrRegistrationHomeOwnerGroups.value.length + 1)
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

  const getGroupForOwner = (
    ownerId: string
  ): MhrRegistrationHomeOwnerGroupIF => {
    // if (!showGroupsUI.value) return null
    return find(getMhrRegistrationHomeOwnerGroups.value, group => {
      return find(group.owners, { id: ownerId })
    })
  }

  const addOwnerToTheGroup = (
    owner: MhrRegistrationHomeOwnersIF,
    groupId: string
  ) => {
    const homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]

    // Try to find a group to add the owner
    const groupToUpdate =
      homeOwnerGroups.find(
        (group: MhrRegistrationHomeOwnerGroupIF) =>
          group.groupId === (groupId || DEFAULT_GROUP_ID)
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

  const editHomeOwner = (
    updatedOwner: MhrRegistrationHomeOwnersIF,
    newGroupId: string
  ) => {
    const homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]
    const groupIdOfOwner = getGroupForOwner(updatedOwner.id).groupId

    const groupToUpdate = homeOwnerGroups.find(
      group => group.groupId === groupIdOfOwner
    ) as MhrRegistrationHomeOwnerGroupIF

    if (groupToUpdate.groupId === newGroupId) {
      // need to update owner in the same group
      const i = findIndex(groupToUpdate.owners, { id: updatedOwner.id })
      set(groupToUpdate.owners, `owners[${i}]`, updatedOwner)
    } else {
      // need to move the owner to new group
      remove(groupToUpdate.owners, owner => owner.id === updatedOwner.id)
      addOwnerToTheGroup(updatedOwner, newGroupId)
    }

    removeEmptyGroups()

    // if we removed all owners from all groups - reset the groups UI flag
    if (homeOwnerGroups.length === 0) {
      setShowGroupsUI(false)
    }
  }

  /**
   * Remove Owner from the Group it belongs to.
   *
   * @param owner owner to be removed
   */
  const removeOwner = (owner: MhrRegistrationHomeOwnersIF) => {
    const homeOwnerGroups = [
      ...getMhrRegistrationHomeOwnerGroups.value
    ] as MhrRegistrationHomeOwnerGroupIF[]

    // find group id that owner belongs to
    const groupIdOfOwner =
      getGroupForOwner(owner.id)?.groupId || DEFAULT_GROUP_ID

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

    // if we removed all owners from all groups - reset the groups UI flag
    if (homeOwnerGroups.length === 0) {
      setShowGroupsUI(false)
    }
  }

  /**
   * Remove all groups without owners.
   */
  const removeEmptyGroups = () => {
    const homeOwnerGroups = [
      ...getMhrRegistrationHomeOwnerGroups.value
    ] as MhrRegistrationHomeOwnerGroupIF[]

    // find all groups with at least one owner
    const newOwnerGroups = homeOwnerGroups.filter(
      group => group.owners.length > 0
    )

    // update owner group ids with new values
    // to make them sequential again (e.g groups 1,3,5 -> 1,2,3)

    newOwnerGroups.forEach((group, index) => {
      group.groupId = (index + 1).toString()
    })

    setMhrRegistrationHomeOwnerGroups(newOwnerGroups)
  }

  return {
    showGroupsUI: readonly(showGroupsUI),
    getSideTitle,
    addOwnerToTheGroup,
    editHomeOwner,
    removeOwner,
    getGroupsDropdownItems,
    getGroupForOwner,
    setShowGroupsUI
  }
}
