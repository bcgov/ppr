import { computed, ComputedRef, nextTick } from 'vue-demi'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useNavigation } from '@/composables'
import { RouteNames, UnitNoteDocTypes } from '@/enums'
import { getFeatureFlag } from '@/utils'

export const useExemptions = () => {
  const { goToRoute } = useNavigation()
  const { setMhrExemptionNote } = useStore()
  const { isRoleStaffReg, isRoleQualifiedSupplier } = storeToRefs(useStore())

  /** Returns true when staff or qualified supplier and the feature flag is enabled **/
  const areExemptionsEnabled: ComputedRef<boolean> = computed((): boolean => {
    return (isRoleStaffReg.value || isRoleQualifiedSupplier.value) &&
      getFeatureFlag('mhr-exemption-enabled')
  })

  /** Navigate to Exemptions Home route **/
  const goToExemptions = async (exemptionType: UnitNoteDocTypes): Promise<void> => {
    await initExemption(exemptionType)
    await goToRoute(RouteNames.EXEMPTION_DETAILS)
  }

  const initExemption = async (exemptionType: UnitNoteDocTypes): Promise<void> => {
    setMhrExemptionNote({ key: 'documentType', value: exemptionType })
    // Reset filing here
  }

  return {
    areExemptionsEnabled,
    goToExemptions
  }
}
