import { computed, ComputedRef } from 'vue'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useNavigation } from '@/composables'
import {
  cleanEmpty,
  fromDisplayPhone,
  getAccountInfoFromAuth,
  getFeatureFlag,
  hasTruthyValue,
  parseAccountToSubmittingParty
} from '@/utils'
import { ExemptionIF, IndividualNameIF, MhRegistrationSummaryIF, PartyIF, UnitNoteIF } from '@/interfaces'
import { APIMhrDescriptionTypes, MhApiStatusTypes, RouteNames, UnitNoteDocTypes, UnitNoteStatusTypes } from '@/enums'

export const useExemptions = () => {
  const { goToRoute } = useNavigation()
  const { setMhrExemption, setMhrExemptionNote, setMhrExemptionValidation, setMhrExemptionValue } = useStore()
  const {
    getMhrExemption,
    getMhrExemptionValidation,
    isRoleStaffReg,
    isRoleQualifiedSupplier,
    getMhrUnitNotes
  } = storeToRefs(useStore())

  /** Returns true when staff or qualified supplier and the feature flag is enabled **/
  const isExemptionEnabled: ComputedRef<boolean> = computed((): boolean => {
    return (isRoleStaffReg.value || isRoleQualifiedSupplier.value) &&
      getFeatureFlag('mhr-exemption-enabled')
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

  /** Construct the payload for Exemptions submission **/
  const buildExemptionPayload = (): ExemptionIF => {
    const party = getMhrExemption.value.submittingParty
    const submittingParty: PartyIF = {
      ...party,
      personName: (party.personName && hasTruthyValue(party.personName))
        ? { ...party.personName } as IndividualNameIF
        : {} as IndividualNameIF,
      phoneNumber: fromDisplayPhone(party.phoneNumber)
    }
    return {
      ...cleanEmpty(getMhrExemption.value),
      submittingParty: cleanEmpty(submittingParty)
    }
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
        const account = await getAccountInfoFromAuth()
        setMhrExemptionValue({ key: 'submittingParty', value: parseAccountToSubmittingParty(account) })

        // Reset Validations here for qs specific requirements
        updateValidation('documentId', true)
        updateValidation('submittingParty', true)
        updateValidation('staffPayment', true)
        break
      case isRoleStaffReg.value:
        const validationState = getMhrExemptionValidation.value
        // eslint-disable-next-line no-return-assign
        Object.keys(validationState).forEach(flag => validationState[flag] = false)

        // Staff specific flags
        updateValidation('remarks', true)
        updateValidation('attention', true)
        updateValidation('folio', true)
        break
      default:
    }
  }

  /** Check if MHR Registration has filed Residential Exemption **/
  const hasChildResExemption = (mhrRegSummary: MhRegistrationSummaryIF): boolean => {
    return mhrRegSummary.changes?.filter(
      reg =>
        [APIMhrDescriptionTypes.RESIDENTIAL_EXEMPTION.toString(),
          APIMhrDescriptionTypes.NON_RESIDENTIAL_EXEMPTION.toString()].includes(reg.registrationDescription) &&
        (reg.statusType === MhApiStatusTypes.EXEMPT || reg.statusType === MhApiStatusTypes.ACTIVE)
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
    goToExemptions,
    updateValidation,
    buildExemptionPayload,
    hasChildResExemption,
    getActiveExemption
  }
}
