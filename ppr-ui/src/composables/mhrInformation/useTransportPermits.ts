import { computed, ComputedRef, ref, Ref } from 'vue'
import { getFeatureFlag } from '@/utils'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'

// Global constants
const isChangeLocationActive: Ref<boolean> = ref(false)

export const useTransportPermits = () => {
  const { isRoleStaffReg, isRoleQualifiedSupplier } = storeToRefs(useStore())

  /** Returns true when staff or qualified supplier and the feature flag is enabled **/
  const isChangeLocationEnabled: ComputedRef<boolean> = computed((): boolean => {
    return (isRoleStaffReg.value || isRoleQualifiedSupplier.value) &&
      getFeatureFlag('mhr-transport-permit-enabled')
  })

  /** Toggle location change flow **/
  const setLocationChange = (val: boolean) => {
    isChangeLocationActive.value = val
  }
  return {
    isChangeLocationActive,
    isChangeLocationEnabled,
    setLocationChange
  }
}
