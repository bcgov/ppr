import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { computed, ComputedRef, reactive } from 'vue'
import {
  deepChangesComparison,
  deleteEmptyProperties,
  fetchMhRegistration,
  fromDisplayPhone,
  getFeatureFlag,
  getMhrDraft
} from '@/utils'
import { ActionTypes, APIRegistrationTypes, HomeCertificationOptions, RouteNames } from '@/enums'
import { useNavigation, useNewMhrRegistration, useTransportPermits } from '@/composables'
import {
  AdminRegistrationIF,
  HomeSectionIF,
  MhRegistrationSummaryIF,
  NewMhrRegistrationApiIF,
  RegistrationTypeIF,
  SubmittingPartyIF,
  UpdatedBadgeIF
} from '@/interfaces'
import { cloneDeep, omit } from 'lodash'
import { MhrCorrectionClient, MhrCorrectionStaff, MhrPublicAmendment } from '@/resources/registrationTypes'

export const useMhrCorrections = () => {
  const {
    setMhrBaseline,
    setRegistrationType,
    setMhrDraftNumber,
    setMhrStatusType,
    setMhrInformation
  } = useStore()
  const {
    getMhrStatusType,
    getMhrRegistration,
    getMhrInformation,
    getRegistrationType,
    getMhrBaseline,
    getMhrHomeSections,
    isRoleStaffReg,
    getMhrTransportPermit,
    getMhrAccountSubmittingParty,
    getMhrTransportPermitPreviousLocation,
    getMhrRegistrationOwnLand,
    getMhrRegistrationLocation,
    getMhrRegistrationHomeOwnerGroups
  } = storeToRefs(useStore())

  const { containsCurrentRoute, goToRoute } = useNavigation()

  /** Returns true for staff when the feature flag is enabled **/
  const isMhrChangesEnabled: ComputedRef<boolean> = computed((): boolean => {
    return isRoleStaffReg.value && getFeatureFlag('mhr-staff-correction-enabled')
  })

  /** Returns true when the current route is a Registration Route (mhr or mhr corrections) **/
  const isRegistrationRoute: ComputedRef<boolean> = computed((): boolean => {
    return containsCurrentRoute([
      RouteNames.SUBMITTING_PARTY,
      RouteNames.YOUR_HOME,
      RouteNames.HOME_OWNERS,
      RouteNames.HOME_LOCATION,
      RouteNames.MHR_REVIEW_CONFIRM
    ])
  })

  /** Returns true when the set registration type is an MhrCorrectionType and current route is a Registration Route  **/
  const isMhrCorrection: ComputedRef<boolean> = computed((): boolean => {
    return [APIRegistrationTypes.MHR_CORRECTION_STAFF, APIRegistrationTypes.MHR_CORRECTION_CLIENT,
      APIRegistrationTypes.MHR_PUBLIC_AMENDMENT].includes(getRegistrationType.value?.registrationTypeAPI) &&
      isRegistrationRoute.value
  })

  /** Returns true when the set registration type is a REGC_STAFF and current route is a Registration Route  **/
  const isStaffCorrection: ComputedRef<boolean> = computed((): boolean => {
    return isRegistrationRoute.value &&
      getRegistrationType.value?.registrationTypeAPI === APIRegistrationTypes.MHR_CORRECTION_STAFF
  })

  /** Returns true when the set registration type is a REGC_CLIENT and current route is a Registration Route  **/
  const isClientCorrection: ComputedRef<boolean> = computed((): boolean => {
    return isRegistrationRoute.value &&
      getRegistrationType.value?.registrationTypeAPI === APIRegistrationTypes.MHR_CORRECTION_CLIENT
  })

  /** Returns true when the set registration type is a PUBA and current route is a Registration Route  **/
  const isPublicAmendment: ComputedRef<boolean> = computed((): boolean => {
    return isRegistrationRoute.value &&
      getRegistrationType.value?.registrationTypeAPI === APIRegistrationTypes.MHR_PUBLIC_AMENDMENT
  })

  /** Returns true when NOT evaluated during a Correction Filing (ie Base MHR) OR has at least 1 Correction Made  **/
  const hasMadeMhrCorrections: ComputedRef<boolean> = computed((): boolean => !!getCorrectionsList().length)

  /** Returns an accurate label based on type of correction **/
  const correctAmendLabel: ComputedRef<string> = computed((): string => {
    return isPublicAmendment.value ? 'Amend' : 'Correct'
  })

  /** Array of keys representing description-related correction groups.*/
  const descriptionGroup: Array<string> = [
    'manufacturer', 'manufacturerYear', 'make', 'model', 'homeCertification', 'rebuilt', 'otherRemarks', 'homeSections'
  ]

  /** Array of keys representing location-related correction groups.*/
  const locationGroup: Array<string> = ['location', 'civicAddress']

  /** Correction State Models: Used in multiple ui-locations for CORRECTED LABELS, centralized for re-use **/
  const correctionState = reactive({
    action: computed((): ActionTypes => isPublicAmendment.value ? ActionTypes.EDITED : ActionTypes.CORRECTED),
    // Mhr Status Type
    status: computed ((): UpdatedBadgeIF => ({
      baseline: getMhrBaseline.value?.statusType,
      currentState: getMhrStatusType.value
    })),
    // Your Home Step
    manufacturer: computed((): UpdatedBadgeIF => ({
      baseline: getMhrBaseline.value?.description.manufacturer,
      currentState: getMhrRegistration.value?.description.manufacturer
    })),
    manufacturerYear: computed((): UpdatedBadgeIF => ({
      baseline: {
        year: getMhrBaseline.value?.description.baseInformation.year,
        circa: getMhrBaseline.value?.description.baseInformation.circa
      },
      currentState: {
        year: getMhrRegistration.value.description.baseInformation.year,
        circa: getMhrRegistration.value.description.baseInformation.circa || false
      }
    })),
    make: computed((): UpdatedBadgeIF => ({
      baseline: getMhrBaseline.value?.description.baseInformation.make,
      currentState: getMhrRegistration.value?.description.baseInformation.make
    })),
    model: computed((): UpdatedBadgeIF => ({
      baseline: getMhrBaseline.value?.description.baseInformation.model,
      currentState: getMhrRegistration.value?.description.baseInformation.model
    })),
    homeCertification: computed((): UpdatedBadgeIF => {
      if (getMhrBaseline.value?.description.certificationOption === HomeCertificationOptions.CSA) {
        return {
          baseline: {
            certificationOption: getMhrBaseline.value?.description.certificationOption,
            csaNumber: getMhrBaseline.value?.description.csaNumber,
            csaStandard: getMhrBaseline.value?.description.csaStandard
          },
          currentState: {
            certificationOption: getMhrRegistration.value?.description.certificationOption,
            csaNumber: getMhrRegistration.value?.description.csaNumber,
            csaStandard: getMhrRegistration.value?.description.csaStandard
          }
        }
      } else {
        return {
          baseline: {
            certificationOption: getMhrBaseline.value?.description.certificationOption,
            engineerName: getMhrBaseline.value?.description.engineerName,
            engineerDate: getMhrBaseline.value?.description.engineerDate
          },
          currentState: {
            certificationOption: getMhrRegistration.value?.description.certificationOption,
            engineerName: getMhrRegistration.value?.description.engineerName,
            engineerDate: getMhrRegistration.value?.description.engineerDate
          }
        }
      }
    }),
    rebuilt: computed((): UpdatedBadgeIF => ({
      baseline: getMhrBaseline.value?.description.rebuiltRemarks,
      currentState: getMhrRegistration.value.description.rebuiltRemarks
    })),
    otherRemarks: computed((): UpdatedBadgeIF => ({
      baseline: getMhrBaseline.value?.description.otherRemarks,
      currentState: getMhrRegistration.value.description.otherRemarks
    })),
    // Home Location Step
    // Actions need to be passed explicitly, due location components/configuration used across Permits
    location: computed(
      (): UpdatedBadgeIF => ({
        action: isPublicAmendment.value ? ActionTypes.EDITED : ActionTypes.CORRECTED,
        baseline: omit(
          getMhrBaseline.value?.location,
          'address',
          'otherType',
          'locationType',
          'permitWithinSamePark',
          'taxCertificate',
          'leaveProvince'
        ),
        currentState: omit(
          getMhrRegistrationLocation.value,
          'address',
          'otherType',
          'locationType',
          'permitWithinSamePark',
          'taxCertificate',
          'leaveProvince'
        )
      })
    ),
    civicAddress: computed((): UpdatedBadgeIF => ({
      action: isPublicAmendment.value ? ActionTypes.EDITED : ActionTypes.CORRECTED,
      // postal code is not displayed in UI and causing the corrections badge to show up
      baseline: omit(getMhrBaseline.value?.location.address, 'postalCode'),
      currentState: omit(getMhrRegistrationLocation.value.address, 'postalCode')
    })),
    landDetails: computed((): UpdatedBadgeIF => ({
      action: isPublicAmendment.value ? ActionTypes.EDITED : ActionTypes.CORRECTED,
      baseline: getMhrBaseline.value?.ownLand,
      currentState: getMhrRegistrationOwnLand.value
    })),
    // HomeSection: Leveraging section applied actions for correction identification
    homeSections: computed ((): boolean => getMhrHomeSections.value?.some(section => !!section.action)),
    // HomeOwners: Leveraging group and owner applied actions for correction identification
    ownerGroups: computed ((): boolean => getMhrRegistrationHomeOwnerGroups.value?.some(group =>
      !!group.action || group.owners.some(owner => !!owner.action))
    )
  })

  /**
   * Retrieves the names of properties from the correctionState that have corrections between baseline and current state
   * @returns string[] An array containing the names of properties with corrections that were corrected.
   */
  const getCorrectionsList = () => Object.keys(correctionState)
    .filter(key => {
      // Do not include action property in correctionsList
      if (key === 'action') return

      const { baseline, currentState } = correctionState[key]

      // Use deepChangesComparison with baseline and currentState if they exist,
      // otherwise, evaluate the value of correctionState[key] itself
      return (baseline !== undefined || currentState !== undefined)
        ? deepChangesComparison(baseline, currentState)
        : correctionState[key]
    }).map(key => key)

  /** Initialize Mhr Correction: Set Snapshot, Current data and Correction Type to state */
  const initMhrCorrection = async (correctionType: RegistrationTypeIF): Promise<void> => {
    // Set Registration Type
    setRegistrationType(correctionType)

    // Fetch current MHR Data
    const { data } = await fetchMhRegistration(getMhrInformation.value.mhrNumber)

    // Handle 'certificationOption' or 'noCertification' value mapping (because it's not returned in response)
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
    await useNewMhrRegistration(true).initDraftOrCurrentMhr(data, true)

    // Navigate to MHR home route
    await goToRoute(RouteNames.SUBMITTING_PARTY)
  }

  const initDraftMhrCorrection = async (mhrInfo: MhRegistrationSummaryIF): Promise<void> => {

    const draftNumber = mhrInfo.draftNumber
    await setMhrInformation(mhrInfo)

    // Fetch draft MHR Data
    const { registration } = await getMhrDraft(draftNumber)
    // Fetch original MHR Data (before the draft correction updates)
    const { data } = await fetchMhRegistration(mhrInfo.mhrNumber)

    const correctionType: RegistrationTypeIF = [MhrCorrectionStaff, MhrCorrectionClient, MhrPublicAmendment]
      .find((corr: RegistrationTypeIF) => corr.registrationTypeAPI === registration.documentType)

    setRegistrationType(correctionType)
    setMhrDraftNumber(draftNumber)

    // Handle 'certificationOption' or 'noCertification' value mapping (because it's not returned in response)
    const certificationOption = (data?.description?.csaNumber && HomeCertificationOptions.CSA) ||
    (data?.description?.engineerName && HomeCertificationOptions.ENGINEER_INSPECTION) || null

    // Set MHR data as baseline state
    await setMhrBaseline(cloneDeep({
      ...data,
      description: {
        ...data.description,
        certificationOption: certificationOption,
        hasNoCertification: certificationOption === null,
      },
      statusType: data?.status
    }))

    await setMhrStatusType(data?.status)

    // Set draft registration as current state
    await useNewMhrRegistration(true).initDraftOrCurrentMhr(registration)
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
      homeSectionToCorrect.action = isPublicAmendment.value
        ? ActionTypes.EDITED
        : ActionTypes.CORRECTED
    } else {
      homeSectionToCorrect.action = null
    }
  }

  /**
   * Builds a correction payload based on the provided MHR state.
   * @param {NewMhrRegistrationApiIF} mhrState - The state of the Manufactured Home Registration.
   * @returns {AdminRegistrationIF} - The correction payload for the Admin Registration.
   */
  const buildCorrectionPayload = (mhrState: NewMhrRegistrationApiIF): AdminRegistrationIF => {
    const correctionsList = getCorrectionsList()
    return {
      attentionReference: mhrState.attentionReference || '',
      documentId: mhrState.documentId,
      documentType: getRegistrationType.value?.registrationTypeAPI,
      ...(mhrState.draftNumber && {
        draftNumber: mhrState.draftNumber
      }),
      submittingParty: mhrState.submittingParty,
      ...(correctionsList.includes('status') && {
        status: getMhrStatusType.value
      }),
      ...(correctionsList.some(value => descriptionGroup.includes(value)) && {
        description: {
          ...mhrState.description,
          baseInformation: {
            ...mhrState.description.baseInformation,
            year: Number(mhrState.description.baseInformation.year) // Cast to number to support legacy strings
          },
          sections: [
            ...mhrState.description.sections.filter(section => section?.action !== ActionTypes.REMOVED)
          ]
        }
      }),
      ...(correctionsList.includes('ownerGroups') && {
        addOwnerGroups: mhrState.ownerGroups
          .filter(group => group.action !== ActionTypes.REMOVED)
          .map(group => ({
            ...group,
            owners: group.owners.filter(owner => owner.action !== ActionTypes.REMOVED)
          })),
        deleteOwnerGroups: getMhrBaseline.value.ownerGroups
      }),
      ...(correctionsList.some(value => locationGroup.includes(value)) && {
        location: { ...mhrState.location, taxCertificate: false }
      }),
      ...(correctionsList.includes('landDetails') && {
        ownLand: mhrState.ownLand
      })
    }
  }

  /** Build and return payload for an Admin Registration: Registered Location Change **/
  const buildLocationChange = (): AdminRegistrationIF => {

    const isCancelTransportPermit = useTransportPermits().isCancelChangeLocationActive.value

    const submittingParty: SubmittingPartyIF = isRoleStaffReg.value
      ? getMhrTransportPermit.value.submittingParty
      : getMhrAccountSubmittingParty.value

    const payloadData: AdminRegistrationIF = {
      documentType: isCancelTransportPermit
        ? APIRegistrationTypes.TRANSPORT_PERMIT_CANCEL
        : APIRegistrationTypes.REGISTERED_LOCATION_CHANGE,
      documentId: getMhrTransportPermit.value.documentId,
      submittingParty: {
        ...submittingParty,
        phoneNumber: fromDisplayPhone(submittingParty?.phoneNumber)
      },
      location: isCancelTransportPermit
        ? { ...getMhrTransportPermitPreviousLocation.value }
        : { ...getMhrTransportPermit.value.newLocation }
    }
    deleteEmptyProperties(payloadData)
    return payloadData
  }

  return {
    getCorrectionsList,
    correctionState,
    isMhrChangesEnabled,
    isMhrCorrection,
    isStaffCorrection,
    isClientCorrection,
    isPublicAmendment,
    correctAmendLabel,
    hasMadeMhrCorrections,
    initMhrCorrection,
    initDraftMhrCorrection,
    correctHomeSection,
    buildLocationChange,
    buildCorrectionPayload
  }
}
