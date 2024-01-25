import { computed, ComputedRef, nextTick, ref, Ref } from 'vue'
import { getFeatureFlag } from '@/utils'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { locationChangeTypes } from '@/resources/mhr-transfers/transport-permits'
import { LocationChangeTypes } from '@/enums/transportPermits'
import { MhrRegistrationHomeLocationIF, MhrTransportPermitIF } from '@/interfaces'
import { APIRegistrationTypes, UnitNoteDocTypes } from '@/enums'

// Global constants
const isChangeLocationActive: Ref<boolean> = ref(false)

export const useTransportPermits = () => {
  const { isRoleStaffReg,
    isRoleQualifiedSupplier ,
    getLienRegistrationType,  getMhrUnitNotes
  } = storeToRefs(useStore())

  const {
    setEmptyMhrTransportPermit,
    setUnsavedChanges,
    setMhrTransportPermitLocationChangeType
  } = useStore()

  /** Returns true when staff or qualified supplier and the feature flag is enabled **/
  const isChangeLocationEnabled: ComputedRef<boolean> = computed((): boolean => {
    return (isRoleStaffReg.value || isRoleQualifiedSupplier.value) && getFeatureFlag('mhr-transport-permit-enabled')
  })

  /** Toggle location change flow **/
  const setLocationChange = (val: boolean) => {
    isChangeLocationActive.value = val
  }

  const setLocationChangeType = (locationChangeType: LocationChangeTypes) => {
    setMhrTransportPermitLocationChangeType(locationChangeType)
  }

  const getUiLocationType = (locationChangeType: LocationChangeTypes): string => {
    return locationChangeTypes.find(item => item.type === locationChangeType)?.title
  }

  const getUiFeeSummaryLocationType = (locationChangeType: LocationChangeTypes): string => {
    return locationChangeTypes.find(item => item.type === locationChangeType)?.feeSummaryTitle
  }

  const isTransportPermitDisabledQS = computed((): boolean =>
    // QS role check
    isRoleQualifiedSupplier.value &&
    // PPR Liens check
    [APIRegistrationTypes.LAND_TAX_LIEN,
    APIRegistrationTypes.MAINTENANCE_LIEN,
    APIRegistrationTypes.MANUFACTURED_HOME_NOTICE]
      .includes(getLienRegistrationType.value as APIRegistrationTypes) &&
    // Unit Notes check
    getMhrUnitNotes.value
      .map(note => note.documentType)
      .some(note => [
        UnitNoteDocTypes.NOTICE_OF_TAX_SALE,
        UnitNoteDocTypes.CONFIDENTIAL_NOTE,
        UnitNoteDocTypes.RESTRAINING_ORDER]
        .includes(note))
  )

  const resetTransportPermit = async (shouldResetLocationChange: boolean = false): Promise<void> => {
    setEmptyMhrTransportPermit(initTransportPermit())
    shouldResetLocationChange && setLocationChange(false)
    setUnsavedChanges(false)
    await nextTick()
  }

  const initTransportPermit = (): MhrTransportPermitIF => {
    return {
      documentId: '',
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
      locationChangeType: null,
      newLocation: {
        parkName: '',
        pad: '',
        address: {
          street: '',
          streetAdditional: '',
          city: '',
          region: null,
          country: null,
          postalCode: ''
        },
        leaveProvince: false,
        pidNumber: '',
        taxCertificate: false,
        taxExpiryDate: '',
        dealerName: '',
        additionalDescription: '',
        locationType: null,
        otherType: null,
        legalDescription: '',
        lot: '',
        parcel: '',
        block: '',
        districtLot: '',
        partOf: '',
        section: '',
        township: '',
        range: '',
        meridian: '',
        landDistrict: '',
        plan: '',
        bandName: '',
        reserveNumber: '',
        exceptionPlan: ''
      } as MhrRegistrationHomeLocationIF,
      ownLand: null
    }
  }

  return {
    initTransportPermit,
    resetTransportPermit,
    isChangeLocationActive,
    isChangeLocationEnabled,
    isTransportPermitDisabledQS,
    setLocationChange,
    setLocationChangeType,
    getUiLocationType,
    getUiFeeSummaryLocationType
  }
}
