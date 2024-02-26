import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { computed, ComputedRef } from 'vue'
import { fetchMhRegistration, getFeatureFlag } from '@/utils'
import { APIRegistrationTypes, RouteNames } from '@/enums'
import { useNavigation, useNewMhrRegistration } from '@/composables'
import { RegistrationTypeIF } from '@/interfaces'

export const useMhrCorrections = () => {
  const {
    setEmptyMhr,
    setMhrBaseline,
    setRegistrationType,
  } = useStore()
  const {
    getMhrInformation,
    getRegistrationType,
    isRoleStaffReg
  } = storeToRefs(useStore())

  const { goToRoute } = useNavigation()
  const { initNewMhr, initDraftOrCurrentMhr } = useNewMhrRegistration()


  /** Returns true for staff when the feature flag is enabled **/
  const isMhrChangesEnabled: ComputedRef<boolean> = computed((): boolean => {
    return isRoleStaffReg.value && getFeatureFlag('mhr-staff-correction-enabled')
  })

  /** Returns true when the set registration type is a Mhr Correction Type **/
  const isMhrCorrection: ComputedRef<boolean> = computed((): boolean => {
    return [APIRegistrationTypes.MHR_CORRECTION_STAFF, APIRegistrationTypes.MHR_CORRECTION_CLIENT]
      .includes(getRegistrationType.value?.registrationTypeAPI)
  })

  /** Initialize Mhr Correction: Set Snapshot, Current data and Correction Type to state */
  const initMhrCorrection = async (correctionType: RegistrationTypeIF, draftNumber: string = ''): Promise<void> => {
    // Clear store data for MHR
    await setEmptyMhr({ ...initNewMhr(), draftNumber })
    // Set Registration Type
    setRegistrationType(correctionType) // Replace with Corrections or type designated

    const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)

    // Preserve MHR snapshot
    await setMhrBaseline(data)

    // Set Current Registration to filing state
    await initDraftOrCurrentMhr(data)

    await goToRoute(RouteNames.SUBMITTING_PARTY)
  }

  return {
    isMhrChangesEnabled,
    isMhrCorrection,
    initMhrCorrection
  }
}
