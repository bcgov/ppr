import { computed, ComputedRef, nextTick } from 'vue-demi'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useNavigation } from '@/composables'
import { RouteNames, UnitNoteDocTypes } from '@/enums'
import { getFeatureFlag } from '@/utils'

export const useExemptions = () => {
  const { goToRoute } = useNavigation()
  const { setMhrExemption, setMhrExemptionNote, setMhrExemptionValidation } = useStore()
  const { getMhrExemptionValidation, isRoleStaffReg, isRoleQualifiedSupplier } = storeToRefs(useStore())

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

    // Reset Validations
    for (const flag in getMhrExemptionValidation.value) {
      updateValidation(flag, false)
    }
  }

  return {
    updateValidation,
    isExemptionEnabled,
    goToExemptions
  }
}
