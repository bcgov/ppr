import { computed, ComputedRef, nextTick, ref, Ref } from 'vue'
import {
  createDateFromPacificTime,
  deepChangesComparison,
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
import { cloneDeep, get } from 'lodash'

// Global constants
const isChangeLocationActive: Ref<boolean> = ref(false)
const isAmendLocationActive: Ref<boolean> = ref(false)

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

  /** Checks if Home's current location is not on Manufacturer's Lot **/
  const isNotManufacturersLot: ComputedRef<boolean> = computed((): boolean =>
    getMhrRegistrationLocation.value.locationType !== HomeLocationTypes.LOT
  )

  /** Checks if Home's new locations is the same MH Park **/
  const isMovingWithinSamePark: ComputedRef<boolean> = computed((): boolean =>
    getMhrTransportPermit.value.locationChangeType === LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK
  )

  /** Checks if active/original Transport Permit filing was within same MH park **/
  const isActivePermitWithinSamePark: ComputedRef<boolean> = computed((): boolean =>
    getMhrRegistrationLocation.value.permitWithinSamePark
  )

  /** Toggle location change flow **/
  const setLocationChange = (val: boolean) => {
    isChangeLocationActive.value = val
  }

  /** Toggle Amend location change flow **/
  const setAmendLocationChange = (val: boolean) => {
    isAmendLocationActive.value = val
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
    setAmendLocationChange(false)
    setUnsavedChanges(false)
    await nextTick()
  }

  const buildAndSubmitTransportPermit = (mhrNumber: string, staffPayment: StaffPaymentIF) => {
    return submitMhrTransportPermit(mhrNumber, buildPayload(), staffPayment)
  }

  const buildPayload = (): MhrTransportPermitIF => {
    const payloadData: MhrTransportPermitIF = cloneDeep({
      ...getMhrTransportPermit.value,
      ...(!isRoleStaffReg.value && {
        submittingParty: {
          ...getMhrAccountSubmittingParty.value,
          phoneNumber: fromDisplayPhone(getMhrAccountSubmittingParty.value.phoneNumber)
        }
      })
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

    // api does not support otherType, and it should be set to the locationType
    if (payloadData.newLocation.otherType) {
      payloadData.newLocation.locationType = payloadData.newLocation.otherType
      delete payloadData.newLocation.otherType
    }

    return payloadData
  }

  // Pre-fill Transport Permit for Amendment
  const prefillTransportPermit = () => {
    const homeLocationInfo: MhrRegistrationHomeLocationIF = getMhrRegistrationLocation.value
    const ownLand = getMhrInformation.value.permitLandStatusConfirmation

    // Set original Transport Permit for future comparison with Amendment filing
    setMhrOriginalTransportPermit({ key: 'newLocation', value: homeLocationInfo })
    setMhrOriginalTransportPermit({ key: 'ownLand', value: ownLand })

    // Set Transport Permit for Amendment
    setMhrTransportPermit(cloneDeep({ key: 'newLocation', value: homeLocationInfo }))
    setMhrTransportPermit(cloneDeep({ key: 'ownLand', value: ownLand }))
  }

  /**
   * Checks if the value of a given property name has been amended between the original
   * and current transport permits.
   */
  const isValueAmended = (propName: string): boolean => {
    // using lodash get because propName includes a nested object, eg. newLocation.address
    const originalTransportPermit = get(getMhrOriginalTransportPermit.value, propName)
    const transportPermit = get(getMhrTransportPermit.value, propName)
    return deepChangesComparison(originalTransportPermit, transportPermit)
  }

  /**
   * Checks if there are changes between the original transport permit and the current transport permit data.
   */
  const hasAmendmentChanges: ComputedRef<boolean> = computed((): boolean => {
    return deepChangesComparison(
      //@ts-ignore
      getMhrOriginalTransportPermit.value,
      {
        newLocation: getMhrTransportPermit.value.newLocation,
        ownLand: getMhrTransportPermit.value.ownLand
      }
    )
  })

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
    hasActiveTransportPermit,
    initTransportPermit,
    resetTransportPermit,
    isChangeLocationActive,
    isAmendLocationActive,
    isChangeLocationEnabled,
    isNotManufacturersLot,
    isMovingWithinSamePark,
    isTransportPermitDisabledQS,
    isActivePermitWithinSamePark,
    isValueAmended,
    hasAmendmentChanges,
    setLocationChange,
    setLocationChangeType,
    setAmendLocationChange,
    getUiLocationType,
    getUiFeeSummaryLocationType,
    populateLocationInfoForSamePark,
    prefillTransportPermit,
    buildAndSubmitTransportPermit
  }
}
