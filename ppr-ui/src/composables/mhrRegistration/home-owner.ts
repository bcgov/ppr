import {
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnersIF
} from '@/interfaces'
import '@/utils/use-composition-api'

import { ref, computed, readonly } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { find, cloneDeep, remove, merge } from 'lodash'

// when home owners not added to any groups
// then do not show it on the UI
const showGroupsUI = ref(false)

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
          value: '1'
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
          group.groupId === (groupId || '1')
      ) || ({} as MhrRegistrationHomeOwnerGroupIF)

    if (groupToUpdate.owners) {
      groupToUpdate.owners.push(owner)
    } else {
      // No groups exist, need to create a new one
      const newGroup = {
        groupId: groupId || '1',
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
      groupToUpdate.owners.splice(
        groupToUpdate.owners.indexOf(updatedOwner),
        1,
        updatedOwner
      )
    } else {
      // need to move the owner to new group

      // groupToUpdate.owners.splice(groupToUpdate.owners.indexOf(updatedOwner), 1)
      // groupToUpdate.owners.splice(
      //   groupToUpdate.owners.length - 1,
      //   0,
      //   updatedOwner
      // )
      // removeOwner(updatedOwner)
      remove(groupToUpdate.owners, owner => owner.id === updatedOwner.id)
      addOwnerToTheGroup(updatedOwner, newGroupId)
    }

    removeEmptyGroups()
  }

  const removeOwner = (owner: MhrRegistrationHomeOwnersIF) => {
    const homeOwnerGroups = [
      ...getMhrRegistrationHomeOwnerGroups.value
    ] as MhrRegistrationHomeOwnerGroupIF[]
    // find group id that owner belongs to
    const groupIdOfOwner = getGroupForOwner(owner.id)?.groupId || '1'
    // find group to remove the owner from
    const groupToUpdate = homeOwnerGroups.find(
      group => group.groupId === groupIdOfOwner
    ) as MhrRegistrationHomeOwnerGroupIF
    // remove the owner from the group
    // groupToUpdate.owners.splice(groupToUpdate.owners.indexOf(owner), 1)
    // update all groups

    remove(groupToUpdate.owners, o => o.id === owner.id)
    setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)

    if (groupToUpdate.owners.length === 0) {
      removeEmptyGroups()
    }

    // if we removed all owners from all groups - reset the groups UI flag
    if (homeOwnerGroups.length === 0) {
      setShowGroupsUI(false)
    }
  }

  const removeEmptyGroups = () => {
    const homeOwnerGroups = [
      ...getMhrRegistrationHomeOwnerGroups.value
    ] as MhrRegistrationHomeOwnerGroupIF[]

    const newOwnerGroups = homeOwnerGroups.filter(
      group => group.owners.length > 0
    )

    newOwnerGroups.forEach((group, index) => {
      group.groupId = (index + 1).toString()
    })

    setMhrRegistrationHomeOwnerGroups(newOwnerGroups)

    // if (groupToUpdate.owners.length === 0) {
    //   // delete owner group because it has no owners
    //   const emptyGroupIndex = homeOwnerGroups.indexOf(groupToUpdate)
    //   homeOwnerGroups.splice(emptyGroupIndex, 1)
    //   // decrease all subsequent groupIds by 1,
    //   // as if owners got moved from group 3 to 2, 2 to 1 etc.
    //   find(
    //     homeOwnerGroups,
    //     group => {
    //       group.groupId = (Number(group.groupId) - 1).toString()
    //     },
    //     emptyGroupIndex
    //   )

    //   setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
    // }
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
