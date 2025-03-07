import { APIRegistrationTypes, RegistrationFlowType } from '@/enums'
import type {
  AddCollateralIF,
  AddPartiesIF,
  CertifyIF,
  CourtOrderIF,
  FinancingStatementIF,
  LengthTrustIF
} from '@/interfaces'
import { AllRegistrationTypes } from '@/resources'
import { useStore } from '@/store/store'
import { cloneDeep } from 'lodash'
import type { ComputedRef } from 'vue';
import { computed } from 'vue'
import { getFeatureFlag } from '@/utils'
import { storeToRefs } from 'pinia'

export const usePprRegistration = () => {
  const {
    setAmendmentDescription,
    setOriginalAddCollateral,
    setOriginalLengthTrust,
    setStaffPayment,
    setCourtOrderInformation,
    setRegistrationCreationDate,
    setRegistrationExpiryDate,
    setRegistrationNumber,
    setRegistrationType,
    setAddCollateral,
    setLengthTrust,
    setSecuritiesActNotices,
    setOriginalSecuritiesActNotices,
    setAddSecuredPartiesAndDebtors,
    setOriginalAddSecuredPartiesAndDebtors,
    setRegistrationFlowType,
    setFolioOrReferenceNumber,
    setCertifyInformation
  } = useStore()
  const { getRegistrationType, getUserSettings } = storeToRefs(useStore())

  // Initializes amendments, renewals, and discharge registrations
  const initPprUpdateFilling = (statement: FinancingStatementIF, flowType: RegistrationFlowType) => {
    // load data into the store
    setRegistrationCreationDate(statement.createDateTime)
    setRegistrationExpiryDate(statement.expiryDate)
    setRegistrationNumber(statement.baseRegistrationNumber)
    setRegistrationFlowType(flowType)
    setFolioOrReferenceNumber('')
    const registrationType = AllRegistrationTypes.find((reg) =>
      reg.registrationTypeAPI === statement.type)

    setRegistrationType(registrationType)

    // Conditionally parse Securities Act Notices
    if (statement?.securitiesActNotices){
      // Map the notices to include an empty array for Orders when there is no pre-existing orders on the notice
      const mappedNotices = statement.securitiesActNotices.map(notice => ({
        ...notice,
        securitiesActOrders: notice.securitiesActOrders || []
      }))

      setSecuritiesActNotices(mappedNotices)
      setOriginalSecuritiesActNotices(cloneDeep(mappedNotices))
    }

    const collateral = {
      valid: true,
      vehicleCollateral: statement.vehicleCollateral,
      generalCollateral: statement.generalCollateral
    } as AddCollateralIF

    setAddCollateral(collateral)

    const parties = {
      valid: true,
      registeringParty: null, // will be taken from account info
      securedParties: statement.securedParties,
      debtors: statement.debtors
    } as AddPartiesIF

    setAddSecuredPartiesAndDebtors(parties)

    const origParties = {
      registeringParty: statement.registeringParty, // will be used for summary
      securedParties: statement.securedParties,
      debtors: statement.debtors
    } as AddPartiesIF

    setOriginalAddSecuredPartiesAndDebtors(origParties)

    const certifyInfo: CertifyIF = {
      valid: false,
      certified: false,
      legalName: '',
      registeringParty: null
    }

    setCertifyInformation(certifyInfo)

    if (flowType !== RegistrationFlowType.DISCHARGE) {
      const courtOrder: CourtOrderIF = {
        courtRegistry: '',
        courtName: '',
        fileNumber: '',
        effectOfOrder: '',
        orderDate: ''
      }

      setCourtOrderInformation(courtOrder)
    }

    let lengthTrust = null

    if (flowType === RegistrationFlowType.RENEWAL) {
      const isRepairsLien = registrationType.registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN &&
        !getFeatureFlag('cla-enabled')
      lengthTrust = {
        valid: !!isRepairsLien,
        showInvalid: false,
        trustIndenture: statement.trustIndenture || false,
        lifeInfinite: false,
        lifeYears: isRepairsLien ? 1 : null,
        surrenderDate: statement.surrenderDate || null,
        lienAmount: statement.lienAmount || null
      } as LengthTrustIF
    } else {
      lengthTrust = {
        valid: true,
        trustIndenture: statement.trustIndenture || false,
        lifeInfinite: statement.lifeInfinite || false,
        lifeYears: statement.lifeYears || null,
        surrenderDate: statement.surrenderDate || null,
        lienAmount: statement.lienAmount || null
      } as LengthTrustIF
    }

    console.log('usePprRegistration.initPprUpdateFilling lengthTrust: ', lengthTrust)
    setLengthTrust(lengthTrust)

    if (flowType !== RegistrationFlowType.DISCHARGE) {
      const staffPayment = {
        option: -1,
        routingSlipNumber: '',
        bcolAccountNumber: '',
        datNumber: '',
        folioNumber: '',
        isPriority: false
      }
      setStaffPayment(staffPayment)
    }

    if (flowType === RegistrationFlowType.AMENDMENT) {
      setAmendmentDescription('')
      setOriginalAddCollateral(cloneDeep(collateral))
      setOriginalLengthTrust(cloneDeep(lengthTrust))
      setOriginalAddSecuredPartiesAndDebtors(cloneDeep(origParties))
    }
  }

  /** Returns true when current ppr registration type is a Security Act Notice **/
  const isSecurityActNotice: ComputedRef<boolean> = computed((): boolean => {
    return getRegistrationType.value?.registrationTypeAPI === APIRegistrationTypes.SECURITY_ACT_NOTICE
  })

  /** Returns true when Security Act Notice Feature Flag is enabled **/
  const isSecurityActNoticeEnabled: ComputedRef<boolean> = computed((): boolean => {
    return getUserSettings.value?.hasSecuritiesActAccess && getFeatureFlag('ppr-sa-notice-enabled')
  })

  return {
    initPprUpdateFilling,
    isSecurityActNotice,
    isSecurityActNoticeEnabled
  }
}
