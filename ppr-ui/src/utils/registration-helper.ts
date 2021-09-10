// Libraries
import { APIRegistrationTypes, DraftTypes, UIRegistrationTypes } from '@/enums'
import {
  AddPartiesIF,
  AddCollateralIF,
  DischargeRegistrationIF,
  DraftIF,
  ErrorIF,
  FinancingStatementIF,
  GeneralCollateralIF,
  PartyIF,
  RegistrationTypeIF,
  StateModelIF,
  DebtorNameIF
} from '@/interfaces'
import {
  createDischarge,
  createDraft,
  createFinancingStatement,
  getDraft,
  updateDraft
} from '@/utils'
import { RegistrationTypes } from '@/resources'

/** Save or update the current financing statement. Data to be saved is in the store state model. */
export async function saveFinancingStatementDraft (stateModel:StateModelIF): Promise<DraftIF> {
  const registrationType: RegistrationTypeIF = stateModel.registration.registrationType
  // console.log('registrationType: ' + JSON.stringify(registrationType))
  var error:ErrorIF = null
  var draft:DraftIF = stateModel.registration.draft
  // console.log('draft: ' + JSON.stringify(draft))
  draft.type = DraftTypes.FINANCING_STATEMENT
  var statement:FinancingStatementIF = draft.financingStatement
  // console.log('statement: ' + JSON.stringify(statement))
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
  if (collateral.generalCollateral !== null && collateral.generalCollateral !== '') {
    var generalCollateral: GeneralCollateralIF = { description: collateral.generalCollateral }
    statement.generalCollateral = [generalCollateral]
  } else {
    statement.generalCollateral = []
  }
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
  // await store.dispatch('setDraft', apiResponse)
  if (draftResponse !== undefined && draftResponse.error === undefined) {
    console.log('saveFinancingStatementDraft ' + apiCall + ' draft successful for documentId ' +
                draftResponse.financingStatement.documentId)
  } else if (draftResponse !== undefined) {
    console.error('saveFinancingStatementDraft failed: ' + draftResponse.error.statusCode + ': ' +
                  draftResponse.error.message)
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
    generalCollateral: [],
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
  if (collateral.generalCollateral !== null && collateral.generalCollateral !== '') {
    var generalCollateral: GeneralCollateralIF = { description: collateral.generalCollateral }
    statement.generalCollateral = [generalCollateral]
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

  var registrationType:RegistrationTypeIF = RegistrationTypes.find(obj => {
    return obj.registrationTypeAPI === draft.financingStatement.type
  })
  /*
  for (const regType of RegistrationTypes) {
    if (regType.registrationTypeAPI !== null && regType.registrationTypeAPI === draft.financingStatement.type) {
      // console.log(regType)
      registrationType = regType
      break
    }
  }
  */

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
  if (draft.financingStatement.generalCollateral && draft.financingStatement.generalCollateral.length > 0) {
    stateModel.registration.collateral.generalCollateral = draft.financingStatement.generalCollateral[0].description
  }
  stateModel.registration.collateral.valid = ((stateModel.registration.collateral.vehicleCollateral &&
      stateModel.registration.collateral.vehicleCollateral.length > 0) ||
      (stateModel.registration.collateral.generalCollateral &&
       stateModel.registration.collateral.generalCollateral !== ''))

  if (draft.financingStatement.clientReferenceId) {
    stateModel.folioOrReferenceNumber = draft.financingStatement.clientReferenceId
  }
  return stateModel
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
