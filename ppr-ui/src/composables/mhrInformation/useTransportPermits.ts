import { computed, ComputedRef, nextTick, ref, Ref } from 'vue'
import {
  createDateFromPacificTime,
  deleteEmptyProperties,
  fromDisplayPhone,
  getFeatureFlag,
  submitMhrTransportPermit
} from '@/utils'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { locationChangeTypes } from '@/resources/mhr-transport-permits/transport-permits'
import { LocationChangeTypes } from '@/enums/transportPermits'
import { MhrRegistrationHomeLocationIF, MhrTransportPermitIF, StaffPaymentIF } from '@/interfaces'
import { APIRegistrationTypes, HomeLocationTypes, MhApiStatusTypes, UnitNoteDocTypes } from '@/enums'
import { cloneDeep, get, isEqual } from 'lodash'

// Global constants
const isChangeLocationActive: Ref<boolean> = ref(false)
const isAmendLocationActive: Ref<boolean> = ref(false)
const isCancelChangeLocationActive: Ref<boolean> = ref(false)

export const useTransportPermits = () => {
  const {
    isRoleStaffSbc,
    isRoleStaffReg,
    isRoleQualifiedSupplier,
    getLienRegistrationType,
    getMhrUnitNotes,
    getMhrTransportPermit,
    getMhrOriginalTransportPermit,
    getMhrInformation,
    getMhrAccountSubmittingParty,
    getMhrRegistrationLocation
  } = storeToRefs(useStore())

  const {
    setMhrTransportPermit,
    setMhrOriginalTransportPermit,
    setEmptyMhrTransportPermit,
    setUnsavedChanges,
    setMhrTransportPermitLocationChangeType
  } = useStore()

  /** Returns true when the Mhr Information permitStatus is ACTIVE **/
  const hasActiveTransportPermit: ComputedRef<boolean> = computed((): boolean => {
    return getMhrInformation.value.permitStatus === MhApiStatusTypes.ACTIVE
  })

  /** Returns true when staff or qualified supplier and the feature flag is enabled **/
  const isChangeLocationEnabled: ComputedRef<boolean> = computed((): boolean => {
    return (isRoleStaffReg.value || isRoleQualifiedSupplier.value || isRoleStaffSbc.value) &&
      getFeatureFlag('mhr-transport-permit-enabled')
  })

  /** Returns true when staff and the feature flag is enabled to amend transport **/
  const isAmendChangeLocationEnabled: ComputedRef<boolean> = computed((): boolean => {
    return (isRoleStaffReg.value || isRoleQualifiedSupplier.value || isRoleStaffSbc.value) &&
      getFeatureFlag('mhr-amend-transport-permit-enabled')
  })

  /** Returns true when staff and the feature flag is enabled to cancel transport permit**/
  const isCancelChangeLocationEnabled: ComputedRef<boolean> = computed((): boolean => {
    return (isRoleStaffReg.value || isRoleQualifiedSupplier.value || isRoleStaffSbc.value) &&
      getFeatureFlag('mhr-cancel-transport-permit-enabled')
  })

  /** Checks if Home's current location is not on Manufacturer's Lot **/
  const isNotManufacturersLot: ComputedRef<boolean> = computed((): boolean =>
    getMhrRegistrationLocation.value.locationType !== HomeLocationTypes.LOT
  )

  /** Is true if the Mhr Status is Active and the Home's current location is outside BC **/
  const isActiveHomeOutsideBc: ComputedRef<boolean> = computed((): boolean => {
    const isOutSideBc = getMhrRegistrationLocation.value?.address?.region !== 'BC'
    return getMhrInformation.value?.statusType === MhApiStatusTypes.ACTIVE && isOutSideBc
  })

  /** Checks if Home's new locations is the same MH Park **/
  const isMovingWithinSamePark: ComputedRef<boolean> = computed((): boolean =>
    getMhrTransportPermit.value.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK
  )

  /** Checks if active/original Transport Permit filing was within same MH park **/
  const isActivePermitWithinSamePark: ComputedRef<boolean> = computed((): boolean =>
    getMhrRegistrationLocation.value.permitWithinSamePark
  )

  /** Is true when the set locationChangeType is Registered Location Change **/
  const isRegisteredLocationChange: ComputedRef<boolean> = computed(() =>
    getMhrTransportPermit.value?.locationChangeType === LocationChangeTypes.REGISTERED_LOCATION)

  /** Toggle location change flow **/
  const setLocationChange = (val: boolean) => {
    isChangeLocationActive.value = val
  }

  /** Toggle Amend location change flow **/
  const setAmendLocationChange = (val: boolean) => {
    isAmendLocationActive.value = val
  }

  /** Toggle Amend location change flow **/
  const setCancelLocationChange = (val: boolean) => {
    isCancelChangeLocationActive.value = val
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

  // For Transport Permits within same park, copy the reg summary info to the transport permit
  const populateLocationInfoForSamePark = (locationInfo: MhrRegistrationHomeLocationIF) => {
    setMhrTransportPermit({ key: 'newLocation', value: cloneDeep(locationInfo) })
  }

  const getLandStatusConfirmation = (newLocation: HomeLocationTypes): boolean => {
    // API rule - set landStatusConfirmation to true if either:
    // the new location type is MH_PARK and the move is not within the same park,
    // or the new location type is STRATA, RESERVE, or OTHER.
    return (newLocation === HomeLocationTypes.HOME_PARK && !isMovingWithinSamePark.value) ||
      [HomeLocationTypes.OTHER_RESERVE, HomeLocationTypes.OTHER_STRATA, HomeLocationTypes.OTHER_TYPE]
      .includes(newLocation)
  }

  const isTransportPermitDisabled = computed((): boolean =>
    // QS or SBC role check
    (isRoleQualifiedSupplier.value || isRoleStaffSbc.value) &&
    // PPR Liens check
    ([APIRegistrationTypes.LAND_TAX_LIEN,
    APIRegistrationTypes.MAINTENANCE_LIEN,
    APIRegistrationTypes.MANUFACTURED_HOME_NOTICE]
      .includes(getLienRegistrationType.value as APIRegistrationTypes) ||
    // Unit Notes check
    getMhrUnitNotes.value
      .map(note => note.documentType)
      .some(note => [
        UnitNoteDocTypes.NOTICE_OF_TAX_SALE,
        UnitNoteDocTypes.CONFIDENTIAL_NOTE,
        UnitNoteDocTypes.RESTRAINING_ORDER]
        .includes(note))
    )
  )

  const resetTransportPermit = async (shouldResetLocationChange: boolean = false): Promise<void> => {
    setEmptyMhrTransportPermit(initTransportPermit())
    shouldResetLocationChange && setLocationChange(false)
    setAmendLocationChange(false)
    setUnsavedChanges(false)
    await nextTick()
  }

  const buildAndSubmitTransportPermit = (mhrNumber: string, staffPayment: StaffPaymentIF) => {
    return submitMhrTransportPermit(mhrNumber, buildPayload(), staffPayment)
  }

  const buildPayload = (): MhrTransportPermitIF => {
    const submittingParty = isRoleStaffReg.value || isRoleStaffSbc.value
      ? getMhrTransportPermit.value.submittingParty
      : getMhrAccountSubmittingParty.value

    // for amendments, the land status confirmation is not always set in UI, but is required for API payload
    if (isAmendLocationActive.value && getMhrTransportPermit.value.landStatusConfirmation === undefined) {
      const landStatus = getLandStatusConfirmation(getMhrTransportPermit.value.newLocation.locationType)
      setMhrTransportPermit({ key: 'landStatusConfirmation', value: landStatus })
    }

    const payloadData: MhrTransportPermitIF = cloneDeep({
      ...getMhrTransportPermit.value,
      submittingParty: {
        ...submittingParty,
        phoneNumber: fromDisplayPhone(submittingParty?.phoneNumber)
      }
    })
    deleteEmptyProperties(payloadData)

    // only regular Transport Permit has Tax Certificate date
    if (getMhrTransportPermit.value.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT) {
      // in certain scenarios there is no tax expiry date
      if (payloadData.newLocation.taxExpiryDate) {
        const yearMonthDay = payloadData.newLocation.taxExpiryDate.split('-')
        const year = parseInt(yearMonthDay[0])
        const month = parseInt(yearMonthDay[1]) - 1
        const day = parseInt(yearMonthDay[2])

        payloadData.newLocation.taxExpiryDate = createDateFromPacificTime(year, month, day, 0, 1)
          .toISOString()
          .replace('.000Z', '+00:00')
      }
    }

    // clean up tax certificate data because it is not showing in UI
    if (getMhrTransportPermit.value.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK) {
      payloadData.newLocation.taxCertificate = false
      delete payloadData.newLocation.taxExpiryDate
    }

    // api does not support otherType, and it should be set to the locationType
    if (payloadData.newLocation?.otherType) {
      payloadData.newLocation.locationType = payloadData.newLocation.otherType
      delete payloadData.newLocation.otherType
    }

    // clean up UI only props
    delete payloadData.registrationStatus

    return payloadData
  }

  // Pre-fill Transport Permit for Amendment
  const prefillTransportPermit = () => {
    const homeLocationInfo: MhrRegistrationHomeLocationIF = getMhrRegistrationLocation.value
    const ownLand = getMhrInformation.value.permitLandStatusConfirmation

    // Set original Transport Permit for future comparison with Amendment filing
    setMhrOriginalTransportPermit({ key: 'newLocation', value: homeLocationInfo })
    setMhrOriginalTransportPermit({ key: 'ownLand', value: ownLand })
    // Store original Reg Status to compare it to updated status and show the Amended badge
    setMhrOriginalTransportPermit({ key: 'registrationStatus', value: getMhrInformation.value.statusType })

    // Set Transport Permit for Amendment
    setMhrTransportPermit(cloneDeep({ key: 'newLocation', value: homeLocationInfo }))
    setMhrTransportPermit(cloneDeep({ key: 'ownLand', value: ownLand }))

    // indicate that the filing amends a transport permit
    setMhrTransportPermit({ key: 'amendment', value: true })
  }

  /**
   * Checks if the value of a given property name has been amended between the original
   * and current transport permits.
   */
  const isValueAmended = (propName: string): boolean => {
    // using lodash get because propName includes a nested object, eg. newLocation.address
    const originalTransportPermit = get(getMhrOriginalTransportPermit.value, propName)
    const transportPermit = get(getMhrTransportPermit.value, propName)
    return !isEqual(originalTransportPermit, transportPermit)
  }

  /**
   * Checks if there are changes between the original transport permit and the current transport permit data.
   */
  const hasAmendmentChanges: ComputedRef<boolean> = computed((): boolean => {
    return !isEqual(
      {
        newLocation: getMhrOriginalTransportPermit.value.newLocation,
        ownLand: getMhrOriginalTransportPermit.value.ownLand
      },
      {
        newLocation: getMhrTransportPermit.value.newLocation,
        ownLand: getMhrTransportPermit.value.ownLand
      }
    )
  })

  const initTransportPermit = (): MhrTransportPermitIF => {
    isAmendLocationActive.value = false
    isCancelChangeLocationActive.value = false
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
      previousLocation: null,
      ownLand: null,
      registrationStatus: ''
    }
  }

  return {
    hasActiveTransportPermit,
    initTransportPermit,
    resetTransportPermit,
    isChangeLocationActive,
    isAmendLocationActive,
    isCancelChangeLocationActive,
    isChangeLocationEnabled,
    isAmendChangeLocationEnabled,
    isCancelChangeLocationEnabled,
    isNotManufacturersLot,
    isActiveHomeOutsideBc,
    isMovingWithinSamePark,
    isRegisteredLocationChange,
    isTransportPermitDisabled,
    isActivePermitWithinSamePark,
    isValueAmended,
    hasAmendmentChanges,
    setLocationChange,
    setLocationChangeType,
    setAmendLocationChange,
    setCancelLocationChange,
    getUiLocationType,
    getUiFeeSummaryLocationType,
    populateLocationInfoForSamePark,
    getLandStatusConfirmation,
    prefillTransportPermit,
    buildAndSubmitTransportPermit
  }
}
