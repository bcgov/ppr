// Libraries
import { DraftTypes } from '@/enums'
import {
  AddPartiesIF,
  AddCollateralIF,
  DraftIF,
  ErrorIF,
  FinancingStatementIF,
  LengthTrustIF,
  RegistrationTypeIF,
  StateModelIF
} from '@/interfaces'
import { createDraft, updateDraft } from '@/utils'

/** Save or update the current financing statement. Data to be saved is in the store state model. */
export async function saveFinancingStatementDraft (stateModel:StateModelIF): Promise<DraftIF> {
  const registrationType: RegistrationTypeIF = stateModel.registrationType
  // console.log('registrationType: ' + JSON.stringify(registrationType))
  var error:ErrorIF = null
  var draft:DraftIF = stateModel.draft
  // console.log('draft: ' + JSON.stringify(draft))
  draft.type = DraftTypes.FINANCING_STATEMENT
  var statement:FinancingStatementIF = draft.financingStatement
  console.log('statement: ' + JSON.stringify(statement))
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
  // Step 1 setup
  const trustLength = stateModel.lengthTrustStep
  statement.lifeInfinite = trustLength.lifeInfinite
  statement.lifeYears = trustLength.lifeYears
  statement.trustIndenture = trustLength.trustIndenture
  // Step 2. setup
  const parties:AddPartiesIF = stateModel.addSecuredPartiesAndDebtorsStep
  statement.registeringParty = parties.registeringParty
  statement.securedParties = parties.securedParties
  statement.debtors = parties.debtors
  // Step 3 setup
  const collateral:AddCollateralIF = stateModel.addCollateralStep
  statement.vehicleCollateral = collateral.vehicleCollateral
  if (collateral.generalCollateral !== null && collateral.generalCollateral !== '') {
    statement.generalCollateral = [
      {
        description: collateral.generalCollateral
      }
    ]
  } else {
    statement.generalCollateral = []
  }
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
