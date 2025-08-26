import type { ComputedRef } from 'vue';
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useNavigation } from '@/composables'
import {
  fromDisplayPhone,
  getAccountInfoFromAuth,
  hasTruthyValue,
  parseAccountToSubmittingParty,
  removeEmptyProperties
} from '@/utils'
import type { ExemptionIF, IndividualNameIF, MhRegistrationSummaryIF, PartyIF, UnitNoteIF } from '@/interfaces'
import {
  APIMhrDescriptionTypes,
  MhApiStatusTypes,
  NonResOptions,
  RouteNames,
  UIRegistrationTypes,
  UnitNoteDocTypes,
  UnitNoteStatusTypes
} from '@/enums'
import { useRouter } from 'vue-router'

export const useExemptions = () => {
  const router = useRouter()
  const { goToRoute } = useNavigation()
  const { setMhrExemption, setMhrExemptionNote, setMhrExemptionValidation, setMhrExemptionValue } = useStore()
  const {
    getCurrentUser,
    getMhrExemption,
    getMhrExemptionValidation,
    isRoleStaffReg,
    isRoleQualifiedSupplier,
    isRoleQualifiedSupplierLawyersNotaries,
    getMhrUnitNotes,
    getMhrInformation
  } = storeToRefs(useStore())

  /** Returns true when staff or qualified supplier(Lawyers and Notaries) and the feature flag is enabled **/
  const isExemptionEnabled: ComputedRef<boolean> = computed((): boolean => {
    return (isRoleStaffReg.value || isRoleQualifiedSupplierLawyersNotaries.value)
  })

  /** Returns true when staff and the feature flag is enabled **/
  const isNonResExemptionEnabled: ComputedRef<boolean> = computed((): boolean => {
    return isRoleStaffReg.value
  })

  /** Returns true when current exemption type is non-residential **/
  const isNonResExemption: ComputedRef<boolean> = computed((): boolean => {
    return getMhrExemption.value?.note?.documentType === UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION
  })

  /** Returns true when current exemption type is residential **/
  const isResExemption: ComputedRef<boolean> = computed((): boolean => {
    return getMhrExemption.value?.note?.documentType === UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER
  })

  /** Returns true if in Exemptions flow with active Transport Permit **/
  const isExemptionWithActiveTransportPermit: ComputedRef<boolean> = computed((): boolean => {
    return (
      getMhrInformation.value.permitStatus === MhApiStatusTypes.ACTIVE &&
      (isResExemption.value || isNonResExemption.value) &&
      [RouteNames.EXEMPTION_DETAILS, RouteNames.EXEMPTION_REVIEW].includes(router.currentRoute.value.name as RouteNames)
    )
  })

  /** Returns Exemption type label **/
  const exemptionLabel: ComputedRef<string> = computed((): string => {
    switch (getMhrExemption.value?.note?.documentType) {
      case UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER:
        return UIRegistrationTypes.RESIDENTIAL_EXEMPTION
      case UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION:
        return UIRegistrationTypes.NON_RESIDENTIAL_EXEMPTION
      default:
        return ''
    }
  })

  /** Navigate to Exemptions Home route **/
  const goToExemptions = async (exemptionType: UnitNoteDocTypes): Promise<void> => {
    await initExemption(exemptionType)
    await goToRoute(RouteNames.EXEMPTION_DETAILS)
  }

  /** Set exemption validation flag values **/
  const updateValidation = (validationFlag: string, value: boolean): void => {
    setMhrExemptionValidation({ key: validationFlag, value })
  }

  /**
   * Formats a non-residential reason value to uppercase and replaces spaces with underscores.
   * @param {string} value - The value to format.
   * @returns {string} The formatted value.
   * @example 'Storage Shed' -> 'STORAGE_SHED'
   */
  const formatNonResReason = (value: string): string => value.toUpperCase().replace(/\s+/g, '_')

  /** Construct the payload for Exemptions submission **/
  const buildExemptionPayload = (): ExemptionIF => {
    const party = getMhrExemption.value.submittingParty
    const note = getMhrExemption.value?.note
    const submittingParty: PartyIF = {
      ...party,
      personName: (party.personName && hasTruthyValue(party.personName))
        ? { ...party.personName } as IndividualNameIF
        : {} as IndividualNameIF,
      phoneNumber: fromDisplayPhone(party.phoneNumber)
    }

    return {
      ...removeEmptyProperties(getMhrExemption.value),
      submittingParty: removeEmptyProperties(submittingParty),
      nonResidential: isNonResExemption.value,
      ...(isNonResExemption.value && {
        note: {
          ...removeEmptyProperties(note),
          destroyed: note.nonResidentialOption === NonResOptions.DESTROYED,
          nonResidentialReason: formatNonResReason(note.nonResidentialReason)
        }
      })
    } as ExemptionIF
  }

  /** Initialize Exemption **/
  const initExemption = async (exemptionType: UnitNoteDocTypes): Promise<void> => {
    setMhrExemption({
      documentId: '',
      clientReferenceId: '',
      attentionReference: '',
      submittingParty: {
        personName: {
          first: '',
          last: '',
          middle: ''
        },
        businessName: '',
        address: {
          street: '',
          streetAdditional: '',
          city: '',
          region: '',
          country: '',
          postalCode: ''
        },
        emailAddress: '',
        phoneNumber: '',
        phoneExtension: ''
      },
      nonResidential: null,
      note: {
        documentType: null,
        remarks: ''
      }
    })
    setMhrExemptionNote({ key: 'documentType', value: exemptionType })

    // Initialize role specific values
    switch (true) {
      case isRoleQualifiedSupplier.value:
        {
          const account = await getAccountInfoFromAuth(getCurrentUser.value)
          setMhrExemptionValue({ key: 'submittingParty', value: parseAccountToSubmittingParty(account) })

          // Reset Validations here for qs specific requirements
          updateValidation('documentId', true)
          updateValidation('declarationDetails', true)
          updateValidation('submittingParty', true)
          updateValidation('staffPayment', true)
          break
        }
      case isRoleStaffReg.value:
        {
          const validationState = getMhrExemptionValidation.value
          Object.keys(validationState).forEach(flag => validationState[flag] = false)

          // Staff specific flags
          updateValidation('declarationDetails', !isNonResExemption.value)
          updateValidation('remarks', true)
          updateValidation('attention', true)
          updateValidation('folio', true)
          updateValidation('staffPayment', isNonResExemption.value)
          break
        }
      default:
    }
  }

  /** Check if MHR Registration has filed Residential Exemption **/
  const hasChildResExemption = (mhrRegSummary: MhRegistrationSummaryIF): boolean => {
    return mhrRegSummary.changes?.filter(
      reg =>
        [APIMhrDescriptionTypes.RESIDENTIAL_EXEMPTION.toString(),
          APIMhrDescriptionTypes.NON_RESIDENTIAL_EXEMPTION.toString()].includes(reg.registrationDescription) &&
        [MhApiStatusTypes.EXEMPT, MhApiStatusTypes.ACTIVE, MhApiStatusTypes.FROZEN]
          .includes(reg.statusType as MhApiStatusTypes)
    ).length > 0
  }

  /* Get active Residential Exemption from unit notes */
  const getActiveExemption = () => {
    // there should be only one active residential exemption
    return getMhrUnitNotes.value.find((unitNote: UnitNoteIF) =>
      [UnitNoteDocTypes.RESIDENTIAL_EXEMPTION_ORDER, UnitNoteDocTypes.NON_RESIDENTIAL_EXEMPTION]
        .includes(unitNote.documentType) &&
      unitNote.status === UnitNoteStatusTypes.ACTIVE
    )
  }

  return {
    isExemptionEnabled,
    isNonResExemptionEnabled,
    isNonResExemption,
    isResExemption,
    isExemptionWithActiveTransportPermit,
    exemptionLabel,
    goToExemptions,
    updateValidation,
    buildExemptionPayload,
    hasChildResExemption,
    getActiveExemption
  }
}
