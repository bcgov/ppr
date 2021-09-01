// Libraries
import { APIRegistrationTypes, DraftTypes } from '@/enums'
import {
  AddPartiesIF,
  AddCollateralIF,
  DraftIF,
  ErrorIF,
  FinancingStatementIF,
  GeneralCollateralIF,
  PartyIF,
  RegistrationTypeIF,
  StateModelIF
} from '@/interfaces'
import { createDraft, createFinancingStatement, updateDraft } from '@/utils'

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
