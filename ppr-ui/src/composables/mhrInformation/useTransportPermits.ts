import { computed, ComputedRef, ref, Ref } from 'vue'
import { getFeatureFlag } from '@/utils'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { locationChangeTypes } from '@/resources/mhr-transfers/transport-permits'
import { LocationChangeTypes } from '@/enums/transportPermits'

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

  const getUiLocationType = (locationChangeType: LocationChangeTypes): string => {
    return locationChangeTypes.find(item => item.type === locationChangeType)?.title
  }

  return {
    isChangeLocationActive,
    isChangeLocationEnabled,
    setLocationChange,
    getUiLocationType
  }
}
