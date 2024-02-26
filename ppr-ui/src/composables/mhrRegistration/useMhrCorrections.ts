import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { computed, ComputedRef } from 'vue'
import { getFeatureFlag } from '@/utils'

export const useMhrCorrections = () => {
  const {
    isRoleStaffReg
  } = storeToRefs(useStore())



  /** Returns true for staff when the feature flag is enabled **/
  const isMhrChangesEnabled: ComputedRef<boolean> = computed((): boolean => {
    return isRoleStaffReg.value && getFeatureFlag('mhr-user-access-enabled')
  })

  return {
    isMhrChangesEnabled
  }
}
