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

  const { containsCurrentRoute, goToRoute } = useNavigation()
  const { initNewMhr, initDraftOrCurrentMhr } = useNewMhrRegistration()


  /** Returns true for staff when the feature flag is enabled **/
  const isMhrChangesEnabled: ComputedRef<boolean> = computed((): boolean => {
    return isRoleStaffReg.value && getFeatureFlag('mhr-staff-correction-enabled')
  })

  /** Returns true when the set registration type is an MhrCorrectionType and current route is a Registration Route  **/
  const isMhrCorrection: ComputedRef<boolean> = computed((): boolean => {
    return [APIRegistrationTypes.MHR_CORRECTION_STAFF, APIRegistrationTypes.MHR_CORRECTION_CLIENT]
      .includes(getRegistrationType.value?.registrationTypeAPI) &&
      containsCurrentRoute([
        RouteNames.SUBMITTING_PARTY,
        RouteNames.YOUR_HOME,
        RouteNames.HOME_OWNERS,
        RouteNames.HOME_LOCATION,
        RouteNames.MHR_REVIEW_CONFIRM
      ])
  })

  /** Initialize Mhr Correction: Set Snapshot, Current data and Correction Type to state */
  const initMhrCorrection = async (correctionType: RegistrationTypeIF, draftNumber: string = ''): Promise<void> => {
    // Clear store data for MHR
    await setEmptyMhr({ ...initNewMhr(), draftNumber })

    // Set Registration Type
    setRegistrationType(correctionType)

    // Fetch current MHR Data
    const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)

    // Preserve MHR snapshot
    await setMhrBaseline({ ...data, statusType: getMhrInformation.value?.statusType })

    // Set Current Registration to filing state
    await initDraftOrCurrentMhr(data, true)

    // Navigate to MHR home route
    await goToRoute(RouteNames.SUBMITTING_PARTY)
  }

  return {
    isMhrChangesEnabled,
    isMhrCorrection,
    initMhrCorrection
  }
}
