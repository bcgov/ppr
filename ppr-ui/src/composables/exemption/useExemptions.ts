import { computed, ComputedRef } from 'vue-demi'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useNavigation } from '@/composables'
import { RouteNames, UnitNoteDocTypes } from '@/enums'
import {
  cleanEmpty,
  fromDisplayPhone,
  getAccountInfoFromAuth,
  getFeatureFlag,
  hasTruthyValue,
  parseAccountToSubmittingParty
} from '@/utils'
import { ExemptionIF } from '@/interfaces'

export const useExemptions = () => {
  const { goToRoute } = useNavigation()
  const { setMhrExemption, setMhrExemptionNote, setMhrExemptionValidation, setMhrExemptionValue } = useStore()
  const { getMhrExemption, isRoleStaffReg, isRoleQualifiedSupplier } = storeToRefs(useStore())

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
    setMhrExemptionValidation({ key: validationFlag, value: value })
  }

  /** Construct the payload for Exemptions submission **/
  const buildExemptionPayload = (): ExemptionIF => {
    const party = getMhrExemption.value.submittingParty
    const submittingParty = {
      ...party,
      personName: (party.personName && hasTruthyValue(party.personName))
        ? { ...party.personName }
        : '',
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

    if (isRoleQualifiedSupplier.value) {
      const account = await getAccountInfoFromAuth()
      setMhrExemptionValue({ key: 'submittingParty', value: parseAccountToSubmittingParty(account) })

      // Reset Validations here for qs specific requirements
      updateValidation('documentId', true)
      updateValidation('submittingParty', true)
      updateValidation('staffPayment', true)
    }
  }

  return {
    isExemptionEnabled,
    goToExemptions,
    updateValidation,
    buildExemptionPayload
  }
}
