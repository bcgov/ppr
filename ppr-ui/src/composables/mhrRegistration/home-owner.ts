import { computed } from '@vue/composition-api'

export function useHomeOwners (
  isPerson: boolean = false,
  isEditMode: boolean = false
) {
  // Title for left side bar
  const getSideTitle = computed((): string => {
    if (isPerson) {
      return isEditMode ? 'Add a Person' : 'Edit Person'
    } else {
      return isEditMode ? 'Add a Business' : 'Edit Business'
    }
  })

  return { getSideTitle }
}
