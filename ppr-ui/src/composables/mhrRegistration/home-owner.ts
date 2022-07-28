import {
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnersIF
} from '@/interfaces'
import '@/utils/use-composition-api'

import { ref, computed, readonly } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { filter, some } from 'lodash'

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
  const getGroupsDropdownItems = (): Array<any> => {
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

  const getGroupIdForOwner = (
    ownerId: string
  ): MhrRegistrationHomeOwnerGroupIF => {
    return filter(
      getMhrRegistrationHomeOwnerGroups.value,
      (group: MhrRegistrationHomeOwnerGroupIF) =>
        some(group.owners, ['id', ownerId])
    )[0]
  }

  const addOwnerToTheGroup = (
    owner: MhrRegistrationHomeOwnersIF,
    groupId: string
  ) => {
    console.log('Adding owner to group:', groupId || '1')
    const homeOwnerGroups = [...getMhrRegistrationHomeOwnerGroups.value]

    // Try to find a group to add the owner
    const groupToUpdate =
      homeOwnerGroups.find(group => group.groupId === groupId) ||
      ({} as MhrRegistrationHomeOwnerGroupIF)

    if (groupToUpdate.owners) {
      console.log('Found the group. Updating')
      groupToUpdate.owners.push(owner)
    } else {
      // No groups exist, need to create a new one
      console.log('No group found. Adding.')
      const newGroup = {
        groupId: groupId || '1',
        owners: [owner] as MhrRegistrationHomeOwnersIF[]
      } as MhrRegistrationHomeOwnerGroupIF
      homeOwnerGroups.push(newGroup)
    }

    setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
  }

  return {
    showGroupsUI: readonly(showGroupsUI),
    getSideTitle,
    addOwnerToTheGroup,
    getGroupsDropdownItems,
    getGroupIdForOwner,
    setShowGroupsUI
  }
}
