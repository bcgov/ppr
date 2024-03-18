import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { computed, ComputedRef } from 'vue'
import { deleteEmptyProperties, fetchMhRegistration, fromDisplayPhone, getFeatureFlag } from '@/utils'
import { ActionTypes, APIRegistrationTypes, HomeCertificationOptions, RouteNames } from '@/enums'
import { useNavigation, useNewMhrRegistration } from '@/composables'
import { AdminRegistrationIF, HomeSectionIF, RegistrationTypeIF } from '@/interfaces'
import { deepChangesComparison } from '@/utils'
import { cloneDeep, omit } from 'lodash'

export const useMhrCorrections = () => {
  const {
    setMhrBaseline,
    setRegistrationType,
  } = useStore()
  const {
    getMhrInformation,
    getRegistrationType,
    getMhrBaseline,
    getMhrHomeSections,
    isRoleStaffReg,
    getMhrTransportPermit
  } = storeToRefs(useStore())

  const { containsCurrentRoute, goToRoute } = useNavigation()
  const { initDraftOrCurrentMhr } = useNewMhrRegistration()


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
  const initMhrCorrection = async (correctionType: RegistrationTypeIF): Promise<void> => {
    // Set Registration Type
    setRegistrationType(correctionType)

    // Fetch current MHR Data
    const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)

     // Handle 'certificationOption' or 'noCertification' value mapping (because it's not returner in response)
     const certificationOption = (data?.description?.csaNumber && HomeCertificationOptions.CSA) ||
     (data?.description?.engineerName && HomeCertificationOptions.ENGINEER_INSPECTION) || null

    // Preserve MHR snapshot
    await setMhrBaseline(cloneDeep({
      ...data,
      description: {
        ...data.description,
        certificationOption: certificationOption,
        hasNoCertification: certificationOption === null,
      },
      statusType: getMhrInformation.value?.statusType
    }))

    // Set Current Registration to filing state
    await initDraftOrCurrentMhr(data, true)

    // Navigate to MHR home route
    await goToRoute(RouteNames.SUBMITTING_PARTY)
  }

  /**
   * Corrects the details of a given home section.
   * This function modifies the `homeSectionToCorrect` object directly by adjusting its
   * `action` property based on certain conditions and deep comparisons with baseline data.
   *
   * Note: The `homeSectionToCorrect` object is passed by reference.
   *
   * @param {HomeSectionIF} homeSectionToCorrect - The home section object to be directly corrected
   */
  const correctHomeSection = (homeSectionToCorrect: HomeSectionIF): void => {
    const homeSections = getMhrHomeSections.value

    // need to omit id and action because not always they are optional and not always present in home section
    const baseline = omit(getMhrBaseline.value?.description.sections[homeSectionToCorrect.id], ['id', 'action'])
    const current = omit(homeSectionToCorrect, ['id', 'action'])

    // workaround for a deep compare because values in baseline are 0's
    // but in current sections are being passed as null
    current.lengthInches ||= 0 // assign 0 if value is null
    current.widthInches ||= 0 // assign 0 if value is null

    if (homeSections[homeSectionToCorrect.id]?.action === ActionTypes.ADDED) {
      // preserve the action for the sections that already Added
      // because when Editing a section, the action is not being passed on Done button click
      homeSectionToCorrect.action = homeSections[homeSectionToCorrect.id].action
    } else if (deepChangesComparison(baseline, current)) {
      // if there are changes add corrected badge
      homeSectionToCorrect.action = ActionTypes.CORRECTED
    } else {
      homeSectionToCorrect.action = null
    }
  }

  /** Build and return payload for an Admin Registration: Registered Location Change **/
  const buildLocationChange = (): AdminRegistrationIF => {
    const payloadData: AdminRegistrationIF = {
      documentType: APIRegistrationTypes.REGISTERED_LOCATION_CHANGE,
      documentId: getMhrTransportPermit.value.documentId,
      submittingParty: {
        ...getMhrTransportPermit.value.submittingParty,
        phoneNumber: fromDisplayPhone(getMhrTransportPermit.value.submittingParty?.phoneNumber)
      },
      location: {
        ...getMhrTransportPermit.value.newLocation
      }
    }
    deleteEmptyProperties(payloadData)
    return payloadData
  }

  return {
    isMhrChangesEnabled,
    isMhrCorrection,
    initMhrCorrection,
    correctHomeSection,
    buildLocationChange
  }
}
