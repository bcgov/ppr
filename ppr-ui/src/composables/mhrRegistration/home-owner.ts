import '@/utils/use-composition-api'

import { ref, computed, readonly } from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'

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
  const getGroupSelectorItems = (): Array<any> => {
    if (showGroupsUI.value) {
      return Array(getMhrRegistrationHomeOwnerGroups.value.length + 1)
        .fill({})
        .map((v, i) => {
          return { text: 'Group ' + (i + 1), value: i + 1 }
        })
    } else {
      return [
        {
          text: 'Group 1',
          value: 1
        }
      ]
    }
  }

  return {
    showGroupsUI: readonly(showGroupsUI),
    getSideTitle,
    getGroupSelectorItems,
    setShowGroupsUI
  }
}
