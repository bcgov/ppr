import { APIRegistrationTypes, RegistrationFlowType } from '@/enums'
import {
  AddCollateralIF, AddPartiesIF, CertifyIF,
  CourtOrderIF, FinancingStatementIF, LengthTrustIF
} from '@/interfaces'
import { AllRegistrationTypes } from '@/resources'
import { useStore } from '@/store/store'
import { cloneDeep } from 'lodash'

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
    setAddSecuredPartiesAndDebtors,
    setOriginalAddSecuredPartiesAndDebtors,
    setRegistrationFlowType,
    setFolioOrReferenceNumber,
    setCertifyInformation
  } = useStore()

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
      const isRepairsLien = registrationType.registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN
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

  return {
    initPprUpdateFilling
  }
}
