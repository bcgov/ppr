// Libraries
import { ActionTypes, APIAmendmentTypes, APIRegistrationTypes, DraftTypes } from '@/enums'
import {
  AddPartiesIF,
  AddCollateralIF,
  AmendmentStatementIF,
  DischargeRegistrationIF,
  DraftIF,
  ErrorIF,
  GeneralCollateralIF,
  FinancingStatementIF,
  PartyIF,
  RegistrationTypeIF,
  StateModelIF,
  RenewRegistrationIF
} from '@/interfaces'
import {
  createDischarge,
  createRenewal,
  createDraft,
  createFinancingStatement,
  getDraft,
  updateDraft
} from '@/utils'
import { RegistrationTypes } from '@/resources'

/** Set the amendment add/delete lists depending on the registration list actions */
function setAmendmentList (baseList:Array<any>, addList:Array<any>, deleteList:Array<any>) {
  for (let i = 0; i < baseList.length; i++) {
    if (baseList[i].action) {
      if (baseList[i].action === ActionTypes.ADDED || baseList[i].action === ActionTypes.EDITED) {
        addList.push(JSON.parse(JSON.stringify(baseList[i])))
      }
      if (baseList[i].action === ActionTypes.REMOVED || baseList[i].action === ActionTypes.EDITED) {
        deleteList.push(JSON.parse(JSON.stringify(baseList[i])))
      }
    }
  }
}

/** Setup the amendment registration for the API call. All data to be saved is in the store state model. */
function setupAmendmentStatement (stateModel:StateModelIF): AmendmentStatementIF {
  const registrationType: RegistrationTypeIF = stateModel.registration.registrationType
  let statement:AmendmentStatementIF = stateModel.registration.draft.amendmentStatement
  if (!statement) {
    statement = {
      changeType: APIAmendmentTypes.AMENDMENT,
      baseRegistrationNumber: stateModel.registration.registrationNumber,
      description: stateModel.registration.amendmentDescription,
      registeringParty: stateModel.registration.parties.registeringParty
    }
  } else {
    statement.description = stateModel.registration.amendmentDescription
  }
  const courtOrder = stateModel.registration.courtOrderInformation
  if (courtOrder && courtOrder.courtName !== '' && courtOrder.courtRegistry !== '' &&
      courtOrder.fileNumber !== '' && courtOrder.effectOfOrder !== '' && courtOrder.orderDate !== '') {
    statement.changeType = APIAmendmentTypes.COURT_ORDER
    statement.courtOrderInformation = stateModel.registration.courtOrderInformation
  } else {
    statement.changeType = APIAmendmentTypes.AMENDMENT
    delete statement.courtOrderInformation
  }
  // Set these every time.
  statement.addSecuredParties = []
  statement.deleteSecuredParties = []
  statement.addDebtors = []
  statement.deleteDebtors = []
  statement.addVehicleCollateral = []
  statement.deleteVehicleCollateral = []
  statement.addGeneralCollateral = []
  statement.deleteGeneralCollateral = []
  if (stateModel.folioOrReferenceNumber && stateModel.folioOrReferenceNumber !== '') {
    statement.clientReferenceId = stateModel.folioOrReferenceNumber
  } else {
    statement.clientReferenceId = ''
  }

  // trust indenture setup
  if (stateModel.registration.lengthTrust.action &&
      stateModel.registration.lengthTrust.action === ActionTypes.EDITED &&
      registrationType.registrationTypeAPI === APIRegistrationTypes.SECURITY_AGREEMENT) {
    statement.trustIndenture = stateModel.registration.lengthTrust.trustIndenture
  } else {
    statement.trustIndenture = false
  }
  const parties:AddPartiesIF = stateModel.registration.parties
  // Conditionally set draft debtors.
  setAmendmentList(parties.debtors, statement.addDebtors, statement.deleteDebtors)

  // Conditionally set draft secured parties.
  setAmendmentList(parties.securedParties, statement.addSecuredParties, statement.deleteSecuredParties)

  const collateral:AddCollateralIF = stateModel.registration.collateral
  // Conditionally set draft vehicle collateral
  setAmendmentList(collateral.vehicleCollateral, statement.addVehicleCollateral, statement.deleteVehicleCollateral)
  // Conditionally set draft general collateral
  if (collateral.generalCollateral && collateral.generalCollateral.length > 0) {
    for (let i = 0; i < collateral.generalCollateral.length; i++) {
      if (collateral.generalCollateral[i].descriptionAdd &&
          collateral.generalCollateral[i].descriptionAdd.trim().length > 0) {
        const gc:GeneralCollateralIF = {
          description: collateral.generalCollateral[i].descriptionAdd
        }
        statement.addGeneralCollateral.push(gc)
      }
      if (collateral.generalCollateral[i].descriptionDelete &&
          collateral.generalCollateral[i].descriptionDelete.trim().length > 0) {
        const gc:GeneralCollateralIF = {
          collateralId: collateral.generalCollateral[i].collateralId,
          description: collateral.generalCollateral[i].descriptionDelete
        }
        statement.deleteGeneralCollateral.push(gc)
      }
    }
  }
  return statement
}

/** Setup the draft data for the current amendment. All data to be saved is in the store state model. */
export function setupAmendmentStatementDraft (stateModel:StateModelIF): DraftIF {
  const draft:DraftIF = {
    type: DraftTypes.AMENDMENT_STATEMENT,
    amendmentStatement: setupAmendmentStatement(stateModel)
  }
  return draft
}

/** Save or update a draft of the current amendment. */
export async function saveAmendmentStatementDraft (stateModel:StateModelIF): Promise<DraftIF> {
  const draft:DraftIF = setupAmendmentStatementDraft(stateModel)
  let draftResponse:DraftIF = null
  let apiCall:String = ''
  if (draft.amendmentStatement.documentId !== undefined && draft.amendmentStatement.documentId !== '') {
    apiCall = 'update'
    draftResponse = await updateDraft(draft)
  } else {
    apiCall = 'create'
    draftResponse = await createDraft(draft)
  }

  if (draftResponse && !draftResponse.error) {
    console.log('saveAmendmentStatementDraft ' + apiCall + ' draft successful for documentId ' +
                draftResponse.amendmentStatement.documentId)
  } else if (draftResponse) {
    console.error('saveAmendmentStatementDraft failed: ' + draftResponse.error.statusCode + ': ' +
                  draftResponse.error.message)
  } else {
    console.error('saveAmendmentStatementDraft failed: no API response.')
  }
  return draftResponse
}

/** Save or update the current financing statement. Data to be saved is in the store state model. */
export async function saveFinancingStatementDraft (stateModel:StateModelIF): Promise<DraftIF> {
  const registrationType: RegistrationTypeIF = stateModel.registration.registrationType
  const draft:DraftIF = stateModel.registration.draft
  draft.type = DraftTypes.FINANCING_STATEMENT
  let statement:FinancingStatementIF = draft.financingStatement
  if (statement === undefined || statement === null) {
    statement = {
      type: registrationType.registrationTypeAPI,
      registeringParty: null,
      securedParties: [],
      debtors: [],
      vehicleCollateral: [],
      generalCollateral: []
    }
  } else {
    statement.type = registrationType.registrationTypeAPI
  }

  if (stateModel.registration.registrationTypeOtherDesc) {
    statement.otherTypeDescription = stateModel.registration.registrationTypeOtherDesc
  }

  // Step 1 setup
  const trustLength = stateModel.registration.lengthTrust
  statement.lifeInfinite = trustLength.lifeInfinite
  statement.lifeYears = trustLength.lifeYears
  statement.trustIndenture = trustLength.trustIndenture
  if (registrationType.registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN) {
    statement.lienAmount = trustLength.lienAmount
    statement.surrenderDate = trustLength.surrenderDate
  }
  // Step 2. setup
  const parties:AddPartiesIF = stateModel.registration.parties
  statement.registeringParty = parties.registeringParty
  statement.securedParties = parties.securedParties
  statement.debtors = parties.debtors
  // Step 3 setup
  const collateral:AddCollateralIF = stateModel.registration.collateral
  statement.vehicleCollateral = collateral.vehicleCollateral
  statement.generalCollateral = collateral.generalCollateral
  statement.clientReferenceId = stateModel.folioOrReferenceNumber
  // Now save the draft.
  draft.financingStatement = statement
  var draftResponse:DraftIF = null
  var apiCall:String = ''
  if (draft.financingStatement.documentId !== undefined && draft.financingStatement.documentId !== '') {
    apiCall = 'update'
    draftResponse = await updateDraft(draft)
  } else {
    apiCall = 'create'
    draftResponse = await createDraft(draft)
  }

  if (draftResponse && !draftResponse.error) {
    console.log('saveFinancingStatementDraft ' + apiCall + ' draft successful for documentId ' +
                draftResponse.financingStatement.documentId)
  } else if (draftResponse) {
    console.error('saveFinancingStatementDraft failed: ' + draftResponse.error.statusCode + ': ' +
                  draftResponse.error.message)
  } else {
    console.error('saveFinancingStatementDraft failed: no API response.')
  }
  return draftResponse
}

/** Save new financing statement. Data to be saved is in the store state model. */
export async function saveFinancingStatement (stateModel:StateModelIF): Promise<FinancingStatementIF> {
  const registrationType: RegistrationTypeIF = stateModel.registration.registrationType
  var error:ErrorIF = null
  var draft:DraftIF = stateModel.registration.draft
  const trustLength = stateModel.registration.lengthTrust
  const parties:AddPartiesIF = stateModel.registration.parties
  const collateral:AddCollateralIF = stateModel.registration.collateral
  var statement:FinancingStatementIF = {
    type: stateModel.registration.registrationType.registrationTypeAPI,
    lifeInfinite: trustLength.lifeInfinite,
    registeringParty: parties.registeringParty,
    securedParties: parties.securedParties,
    debtors: parties.debtors,
    vehicleCollateral: collateral.vehicleCollateral,
    generalCollateral: collateral.generalCollateral,
    clientReferenceId: stateModel.folioOrReferenceNumber
  }
  if (!trustLength.lifeInfinite) {
    statement.lifeYears = trustLength.lifeYears
  }
  if (stateModel.registration.registrationTypeOtherDesc) {
    statement.otherTypeDescription = stateModel.registration.registrationTypeOtherDesc
  }
  if (draft !== null && draft.financingStatement !== null) {
    statement.documentId = draft.financingStatement.documentId
  }
  if (statement.type === 'SA') {
    statement.trustIndenture = trustLength.trustIndenture
  } else if (statement.type === APIRegistrationTypes.REPAIRERS_LIEN) {
    statement.lienAmount = trustLength.lienAmount
    statement.surrenderDate = trustLength.surrenderDate + 'T08:00:00+00:00'
  }
  // Now tidy up, deleting objects that are empty strings to pass validation.
  // For example, party.birthDate = '' will fail validation.
  statement.registeringParty = cleanupParty(statement.registeringParty)
  for (let i = 0; i < statement.debtors.length; i++) {
    statement.debtors[i] = cleanupParty(statement.debtors[i])
  }
  for (let i = 0; i < statement.securedParties.length; i++) {
    statement.securedParties[i] = cleanupParty(statement.securedParties[i])
  }
  if (statement.vehicleCollateral !== null) {
    for (let i = 0; i < statement.vehicleCollateral.length; i++) {
      if (statement.vehicleCollateral[i].year !== null) {
        if (statement.vehicleCollateral[i].year === '') {
          delete statement.vehicleCollateral[i].year
        } else if (typeof statement.vehicleCollateral[i].year === 'string') {
          statement.vehicleCollateral[i].year = Number(statement.vehicleCollateral[i].year)
        }
      }
    }
  }
  // Now save the financing statement.
  const apiResponse = await createFinancingStatement(statement)

  if (apiResponse !== undefined && apiResponse.error !== undefined) {
    console.error('saveFinancingStatement failed: ' + apiResponse.error.statusCode + ': ' +
                  apiResponse.error.message)
  }
  return apiResponse
}

/** Save new discharge registration. Data to be saved is in the store state model. */
export async function saveDischarge (stateModel:StateModelIF): Promise<DischargeRegistrationIF> {
  var registration:DischargeRegistrationIF = {
    baseRegistrationNumber: stateModel.registration.registrationNumber,
    debtorName: stateModel.registration.confirmDebtorName,
    registeringParty: stateModel.registration.parties.registeringParty,
    clientReferenceId: stateModel.folioOrReferenceNumber
  }
  if (registration.clientReferenceId === null || registration.clientReferenceId.trim().length < 1) {
    delete registration.clientReferenceId
  }
  registration.registeringParty = cleanupParty(registration.registeringParty)
  // Now save the registration.
  console.log('saveDischarge calling api for base registration number ' + registration.baseRegistrationNumber + '.')
  const apiResponse = await createDischarge(registration)

  if (apiResponse !== undefined && apiResponse.error !== undefined) {
    console.error('saveDischarge failed: ' + apiResponse.error.statusCode + ': ' +
                  apiResponse.error.message)
  }
  return apiResponse
}

/** Setup a financing statement draft for editing. Get the previously saved draft and hydrate the state model. */
export async function setupFinancingStatementDraft (stateModel:StateModelIF, documentId:string): Promise<StateModelIF> {
  const draft:DraftIF = await getDraft(documentId)
  stateModel.registration.draft = draft
  if (draft === undefined) {
    console.error('getDraft failed: response null.')
    return stateModel
  }
  if (draft !== undefined && draft.error !== undefined) {
    console.error('getDraft failed: ' + draft.error.statusCode + ': ' + draft.error.message)
    return stateModel
  }

  const registrationType:RegistrationTypeIF = RegistrationTypes.find(obj => {
    return obj.registrationTypeAPI === draft.financingStatement.type
  })

  stateModel.registration.registrationType = registrationType
  if (draft.financingStatement.registeringParty) {
    stateModel.registration.parties.registeringParty = draft.financingStatement.registeringParty
  }
  // Step 1 setup
  if (draft.financingStatement.lifeInfinite) {
    stateModel.registration.lengthTrust.lifeInfinite = draft.financingStatement.lifeInfinite
  }
  if (draft.financingStatement.lifeYears) {
    stateModel.registration.lengthTrust.lifeYears = draft.financingStatement.lifeYears
  }
  if (draft.financingStatement.trustIndenture) {
    stateModel.registration.lengthTrust.trustIndenture = draft.financingStatement.trustIndenture
  }
  if (draft.financingStatement.type === APIRegistrationTypes.REPAIRERS_LIEN) {
    if (draft.financingStatement.lienAmount) {
      stateModel.registration.lengthTrust.lienAmount = draft.financingStatement.lienAmount
    }
    if (draft.financingStatement.surrenderDate) {
      stateModel.registration.lengthTrust.surrenderDate = draft.financingStatement.surrenderDate
    }
    stateModel.registration.lengthTrust.valid = (stateModel.registration.lengthTrust.lienAmount !== '' &&
                                                 stateModel.registration.lengthTrust.surrenderDate !== '')
  } else {
    stateModel.registration.lengthTrust.valid = (stateModel.registration.lengthTrust.lifeYears > 0 ||
                                                 stateModel.registration.lengthTrust.lifeInfinite === true)
  }

  // Step 2 setup
  if (draft.financingStatement.registeringParty) {
    stateModel.registration.parties.registeringParty = draft.financingStatement.registeringParty
  }
  if (draft.financingStatement.securedParties) {
    stateModel.registration.parties.securedParties = draft.financingStatement.securedParties
  }
  if (draft.financingStatement.debtors) {
    stateModel.registration.parties.debtors = draft.financingStatement.debtors
  }
  stateModel.registration.parties.valid = (stateModel.registration.parties.registeringParty &&
    stateModel.registration.parties.debtors && stateModel.registration.parties.debtors.length > 0 &&
    stateModel.registration.parties.securedParties && stateModel.registration.parties.securedParties.length > 0)

  // Step 3 setup
  if (draft.financingStatement.vehicleCollateral) {
    stateModel.registration.collateral.vehicleCollateral = draft.financingStatement.vehicleCollateral
  }
  if (draft.financingStatement.generalCollateral) {
    stateModel.registration.collateral.generalCollateral = draft.financingStatement.generalCollateral
  }
  const vcValid = stateModel.registration.collateral.vehicleCollateral?.length !== 0
  const gcValid = stateModel.registration.collateral.generalCollateral?.length !== 0
  stateModel.registration.collateral.valid = vcValid && gcValid

  if (draft.financingStatement.clientReferenceId) {
    stateModel.folioOrReferenceNumber = draft.financingStatement.clientReferenceId
  }
  return stateModel
}

/** Save new discharge registration. Data to be saved is in the store state model. */
export async function saveRenewal (stateModel:StateModelIF): Promise<RenewRegistrationIF> {
  const trustLength = stateModel.registration.lengthTrust

  var registration:RenewRegistrationIF = {
    baseRegistrationNumber: stateModel.registration.registrationNumber,
    debtorName: stateModel.registration.confirmDebtorName,
    registeringParty: stateModel.registration.parties.registeringParty,
    clientReferenceId: stateModel.folioOrReferenceNumber
  }
  if (registration.clientReferenceId === null || registration.clientReferenceId.trim().length < 1) {
    delete registration.clientReferenceId
  }
  registration.registeringParty = cleanupParty(registration.registeringParty)

  if (!trustLength.lifeInfinite) {
    registration.lifeYears = trustLength.lifeYears
  }

  // Now save the registration.
  console.log('save renewal calling api for base registration number ' + registration.baseRegistrationNumber + '.')
  const apiResponse = await createRenewal(registration)

  if (apiResponse !== undefined && apiResponse.error !== undefined) {
    console.error('save renewal failed: ' + apiResponse.error.statusCode + ': ' +
                  apiResponse.error.message)
  }
  return apiResponse
}

export function cleanupParty (party: PartyIF): PartyIF {
  if (party.emailAddress !== null && party.emailAddress === '') {
    delete party.emailAddress
  }
  if (party.code !== null && party.code === '') {
    delete party.code
  }
  if (party.code !== null && party.code !== undefined) {
    delete party.emailAddress
    delete party.birthDate
    delete party.personName
    delete party.businessName
    delete party.address
  } else {
    if (party.birthDate === null || party.birthDate === '') {
      delete party.birthDate
    }
    if (party.businessName !== null && party.businessName !== '') {
      delete party.personName
    } else {
      delete party.businessName
      if (party.personName.middle !== null && party.personName.middle === '') {
        delete party.personName.middle
      }
    }
    if (party.address.streetAdditional !== null && party.address.streetAdditional === '') {
      delete party.address.streetAdditional
    }
    if (party.address.deliveryInstructions !== null && party.address.deliveryInstructions === '') {
      delete party.address.deliveryInstructions
    }
  }
  return party
}
