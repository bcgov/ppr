// Libraries
import { ActionTypes, APIAmendmentTypes, APIRegistrationTypes, DraftTypes } from '@/enums'
import {
  AddCollateralIF,
  AddEditSaNoticeIF,
  AddPartiesIF,
  AmendmentStatementIF,
  DischargeRegistrationIF,
  DraftIF,
  FinancingStatementIF,
  GeneralCollateralIF,
  PartyIF,
  RegistrationTypeIF,
  RenewRegistrationIF,
  StateModelIF,
  VehicleCollateralIF
} from '@/interfaces'
import {
  convertToISO8601LastMinute,
  createAmendmentStatement,
  createDischarge,
  createDraft,
  createFinancingStatement,
  createRenewal,
  getDraft,
  removeEmptyProperties,
  staffAmendment,
  staffDischarge,
  staffFinancingStatement,
  staffRenewal,
  updateDraft
} from '@/utils'
import { RegistrationTypes } from '@/resources'
import { usePprRegistration } from '@/composables'
import { cloneDeep } from 'lodash'

/** Set the amendment add/delete lists depending on the registration list actions */
export function setAmendmentList (baseList:Array<any>, addList:Array<any>, deleteList:Array<any>) {
  for (let i = 0; i < baseList.length; i++) {
    if (baseList[i].action) {
      if (baseList[i].action === ActionTypes.ADDED || baseList[i].action === ActionTypes.EDITED) {
        const party = {
          ...baseList[i],
          amendPartyId: baseList[i].action === ActionTypes.EDITED ? baseList[i].partyId : 0
        }
        addList.push(JSON.parse(JSON.stringify(party)))
      }
      if (baseList[i].action === ActionTypes.REMOVED || baseList[i].action === ActionTypes.EDITED) {
        deleteList.push(JSON.parse(JSON.stringify(baseList[i])))
      }
    }
  }
}

/**
 * Categorizes the given notices into `addNotices` and `deleteNotices` arrays based on their action types.
 *
 * @param {Array<AddEditSaNoticeIF>} notices - The array of notice objects to be processed.
 * @param {Array<AddEditSaNoticeIF>} addNotices - The array to store notices with actions 'ADDED' or 'EDITED'.
 * @param {Array<AddEditSaNoticeIF>} deleteNotices - The array to store notices with actions 'REMOVED' or 'EDITED'.
 *
 * @returns An object containing the updated `addNotices` and `deleteNotices` arrays.
**/
 export function setNoticeAmendments (
  notices: Array<AddEditSaNoticeIF>, addNotices: Array<AddEditSaNoticeIF>, deleteNotices: Array<AddEditSaNoticeIF>
): { addNotices: Array<AddEditSaNoticeIF>; deleteNotices: Array<AddEditSaNoticeIF> } {
  notices?.forEach(notice => {
    // Check for child order edits. Any order changes would result in an amendment to the entire notice
    const hasOrderChange = notice.securitiesActOrders?.some(order => !!order.action)

    // Include Added/Amended Notices or Notices that contain Added/Amended Orders into ADD block
    if ([ActionTypes.ADDED, ActionTypes.EDITED].includes(notice?.action) || hasOrderChange) {
      // Clean and format notice and orders
      const formattedNotice = {
        ...removeEmptyProperties(notice),
        ...(!!notice.effectiveDateTime && {
          effectiveDateTime: convertToISO8601LastMinute(notice.effectiveDateTime.split('T')[0])
        }),
          securitiesActOrders: notice.securitiesActOrders?.filter(order =>
            order.action !== ActionTypes.REMOVED).map(order => ({
          ...removeEmptyProperties(order),
          orderDate: convertToISO8601LastMinute(order.orderDate.split('T')[0])
        }))
      } as AddEditSaNoticeIF
      addNotices.push(formattedNotice)
    }

    // Include Removed/Amended Notices or Notices that contain Removed/Amended Orders in DELETE block
    if ([ActionTypes.REMOVED, ActionTypes.EDITED].includes(notice?.action) ||
      (notice?.action !== ActionTypes.ADDED && hasOrderChange)) deleteNotices.push(notice)
  })
  return { addNotices, deleteNotices }
}

const parseNoticeAmendmentDraft = (
  notices: Array<AddEditSaNoticeIF>,
  addNotices: Array<AddEditSaNoticeIF>,
  deleteNotices: Array<AddEditSaNoticeIF>
) => {
  const consolidatedNotices: Array<AddEditSaNoticeIF> = [
    ...notices,
    ...addNotices,
    ...deleteNotices
  ]
  return Array.from(new Map(consolidatedNotices.map(notice => [notice.noticeId, notice])).values())
}

/** Set the registration list and actions from the draft add/delete lists. */
function setupRegistrationPartyList (baseList:Array<any>, addList:Array<any>, deleteList:Array<any>) {
  if (addList && addList.length > 0) {
    for (let i = 0; i < addList.length; i++) {
      addList[i].action = ActionTypes.ADDED
      // Check if an edit
      if (baseList.length > 0 && addList[i].partyId > 0) {
        for (let j = 0; j < baseList.length; j++) {
          if (baseList[j].partyId === addList[i].partyId) {
            addList[i].action = ActionTypes.EDITED
            baseList[j] = addList[i] // replace with edited values.
          }
        }
      }
      if (addList[i].action === ActionTypes.ADDED) {
        baseList.push(JSON.parse(JSON.stringify(addList[i])))
      }
    }
  }
  if (deleteList && deleteList.length > 0) {
    for (let i = 0; i < deleteList.length; i++) {
      // Mark as deleted unless an edit
      if (baseList.length > 0) {
        for (let j = 0; j < baseList.length; j++) {
          if (baseList[j].partyId === deleteList[i].partyId && !baseList[j].action) {
            baseList[j].action = ActionTypes.REMOVED
          }
        }
      }
    }
  }
}

/** Set the registration list and actions from the draft add/delete lists. */
function setupVehicleCollateralList (baseList:Array<VehicleCollateralIF>, addList:Array<VehicleCollateralIF>,
  deleteList:Array<VehicleCollateralIF>) {
  if (addList && addList.length > 0) {
    for (let i = 0; i < addList.length; i++) {
      addList[i].action = ActionTypes.ADDED
      // Check if an edit
      if (baseList.length > 0 && addList[i].vehicleId > 0) {
        for (let j = 0; j < baseList.length; j++) {
          if (baseList[j].vehicleId === addList[i].vehicleId) {
            addList[i].action = ActionTypes.EDITED
            baseList[j] = addList[i] // replace with edited values.
          }
        }
      }
      if (addList[i].action === ActionTypes.ADDED) {
        baseList.push(JSON.parse(JSON.stringify(addList[i])))
      }
    }
  }
  if (deleteList && deleteList.length > 0) {
    for (let i = 0; i < deleteList.length; i++) {
      // Mark as deleted unless an edit
      if (baseList.length > 0) {
        for (let j = 0; j < baseList.length; j++) {
          if (baseList[j].vehicleId === deleteList[i].vehicleId && !baseList[j].action) {
            baseList[j].action = ActionTypes.REMOVED
          }
        }
      }
    }
  }
}

/** Update parties to pass API validation: remove empty properties. */
function cleanupPartyList (partyList:Array<PartyIF>) {
  for (let i = 0; i < partyList.length; i++) {
    partyList[i] = cleanupParty(partyList[i])
  }
}

/** Update vehicle collateral to pass API validation. */
function cleanupVehicleCollateral (collateralList:Array<VehicleCollateralIF>) {
  if (collateralList) {
    for (let i = 0; i < collateralList.length; i++) {
      if (collateralList[i].action !== null) {
        delete collateralList[i].action
      }
      if (collateralList[i].year !== null) {
        if (collateralList[i].year === '') {
          delete collateralList[i].year
        } else if (typeof collateralList[i].year === 'string') {
          collateralList[i].year = Number(collateralList[i].year)
        }
      }
    }
  }
}

function getIsStaff (stateModel:StateModelIF): boolean {
  return stateModel.authorization?.authRoles.includes('ppr_staff') ||
  stateModel.authorization?.authRoles.includes('gov_account_user')
}

/** Setup the amendment registration for the API call. All data to be saved is in the store state model. */
function setupAmendmentStatement (stateModel:StateModelIF): AmendmentStatementIF {
  const registrationType: RegistrationTypeIF = stateModel.registration.registrationType
  let statement: AmendmentStatementIF = stateModel.registration.draft.amendmentStatement
  if (!statement) {
    statement = {
      changeType: APIAmendmentTypes.AMENDMENT,
      baseRegistrationNumber: stateModel.registration.registrationNumber,
      description: stateModel.registration.amendmentDescription,
      debtorName: stateModel.registration.confirmDebtorName,
      registeringParty: stateModel.registration.parties.registeringParty,
      authorizationReceived: true
    }
  } else {
    statement.description = stateModel.registration.amendmentDescription
    statement.registeringParty = stateModel.registration.parties.registeringParty
  }
  const courtOrder = stateModel.registration.courtOrderInformation
  if (courtOrder && courtOrder.courtName !== '' && courtOrder.courtRegistry !== '' &&
      courtOrder.fileNumber !== '' && courtOrder.effectOfOrder !== '' && courtOrder.orderDate !== '') {
    statement.changeType = APIAmendmentTypes.COURT_ORDER
    statement.courtOrderInformation = stateModel.registration.courtOrderInformation
    if (statement.courtOrderInformation.orderDate.length === 10) {
      // add time (latest possible time to avoid conflicts with creation date)
      const d = new Date(statement.courtOrderInformation.orderDate + 'T23:59:59')
      // convert back to UTC (required to pass api validation properly in some edge cases)
      let month = `${d.getUTCMonth() + 1}`
      let day = `${d.getUTCDate()}`
      let hours = `${d.getUTCHours()}`
      if (month.length < 2) month = `0${month}`
      if (day.length < 2) day = `0${day}`
      if (hours.length < 2) hours = `0${hours}`
      const orderDateUTC = `${d.getUTCFullYear()}-${month}-${day}T${hours}:59:59+00:00`
      statement.courtOrderInformation.orderDate = orderDateUTC
    }
  } else {
    statement.changeType = APIAmendmentTypes.AMENDMENT
    delete statement.courtOrderInformation
  }
  // Set these every time.
  statement.addSecuredParties = []
  statement.deleteSecuredParties = []
  statement.addSecuritiesActNotices = []
  statement.deleteSecuritiesActNotices = []
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
    if (stateModel.registration.lengthTrust.trustIndenture) {
      statement.addTrustIndenture = true
    } else {
      statement.removeTrustIndenture = true
    }
  }

  // Security Act Notices setup
  if (registrationType.registrationTypeAPI === APIRegistrationTypes.SECURITY_ACT_NOTICE) {
    setNoticeAmendments(
      stateModel.registration.securitiesActNotices,
      statement.addSecuritiesActNotices,
      statement.deleteSecuritiesActNotices
    )
  }

  const parties:AddPartiesIF = stateModel.registration.parties
  // Conditionally set draft debtors.
  setAmendmentList(parties.debtors, statement.addDebtors, statement.deleteDebtors)

  // Conditionally set draft secured parties.
  setAmendmentList(parties.securedParties, statement.addSecuredParties, statement.deleteSecuredParties)

  const collateral:AddCollateralIF = stateModel.registration.collateral
  // Conditionally set draft vehicle collateral
  if (collateral.vehicleCollateral) {
    setAmendmentList(collateral.vehicleCollateral, statement.addVehicleCollateral, statement.deleteVehicleCollateral)
  }
  // Conditionally set draft general collateral
  if (collateral.generalCollateral && collateral.generalCollateral.length > 0) {
    for (let i = 0; i < collateral.generalCollateral.length; i++) {
      if (collateral.generalCollateral[i].descriptionAdd &&
          collateral.generalCollateral[i].descriptionAdd.trim().length > 0 &&
          (!collateral.generalCollateral[i].collateralId || collateral.generalCollateral[i].collateralId < 1)) {
        const gc:GeneralCollateralIF = {
          description: collateral.generalCollateral[i].descriptionAdd
        }
        statement.addGeneralCollateral.push(gc)
      }
      if (collateral.generalCollateral[i].descriptionDelete &&
          collateral.generalCollateral[i].descriptionDelete.trim().length > 0 &&
          (!collateral.generalCollateral[i].collateralId || collateral.generalCollateral[i].collateralId < 1)) {
        const gc:GeneralCollateralIF = {
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
  let apiCall:string = ''
  if (draft.amendmentStatement.documentId !== undefined && draft.amendmentStatement.documentId !== '') {
    apiCall = 'update'
    draftResponse = await updateDraft(draft)
  } else {
    apiCall = 'create'
    draftResponse = await createDraft(draft)
  }

  if (!draftResponse.error) {
    console.log('saveAmendmentStatementDraft ' + apiCall + ' draft successful for documentId ' +
                draftResponse.amendmentStatement?.documentId)
  }
  return draftResponse
}

/** Save a new amendment. */
export async function saveAmendmentStatement (stateModel:StateModelIF): Promise<AmendmentStatementIF> {
  const statement:AmendmentStatementIF = setupAmendmentStatement(stateModel)
  // Now tidy up, deleting objects that are empty strings to pass validation.
  // For example, party.birthDate = '' will fail validation.
  statement.registeringParty = cleanupParty(statement.registeringParty)
  cleanupPartyList(statement.addDebtors)
  cleanupPartyList(statement.deleteDebtors)
  cleanupPartyList(statement.addSecuredParties)
  cleanupPartyList(statement.deleteSecuredParties)
  cleanupVehicleCollateral(statement.addVehicleCollateral)
  cleanupVehicleCollateral(statement.deleteVehicleCollateral)
  if (statement.courtOrderInformation && statement.courtOrderInformation.action) {
    delete statement.courtOrderInformation.action
  }
  // Now save the amendment statement.
  let apiResponse
  if (getIsStaff(stateModel)) {
    apiResponse = await staffAmendment(statement, stateModel.staffPayment)
  } else {
    apiResponse = await createAmendmentStatement(statement, '')
  }

  if (apiResponse && apiResponse.error) {
    console.error('saveAmendmentStatement failed: ' + apiResponse.error.statusCode + ': ' +
                  apiResponse.error.message)
  }
  return apiResponse
}

/** Save or update the current financing statement. Data to be saved is in the store state model. */
export async function saveFinancingStatementDraft (stateModel:StateModelIF): Promise<DraftIF> {
  const registrationType: RegistrationTypeIF = stateModel.registration.registrationType
  const draft: DraftIF = stateModel.registration.draft
  // remove any previous error info
  delete draft.error
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
  if (registrationType.registrationTypeAPI === APIRegistrationTypes.SECURITY_ACT_NOTICE) {
    statement.securitiesActNotices = stateModel.registration.securitiesActNotices
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
  let draftResponse:DraftIF = null
  let apiCall:string = ''
  if (draft.amendmentStatement !== undefined) {
    delete draft.amendmentStatement
  }
  if (draft.financingStatement.registeringParty !== undefined && draft.financingStatement.registeringParty === null) {
    delete draft.financingStatement.registeringParty
  }
  if (draft.createDateTime !== undefined && draft.createDateTime === null) {
    draft.createDateTime = ''
  }
  if (draft.lastUpdateDateTime !== undefined && draft.lastUpdateDateTime === null) {
    draft.lastUpdateDateTime = ''
  }
  if (draft.financingStatement.documentId !== undefined && draft.financingStatement.documentId !== '') {
    apiCall = 'update'
    draftResponse = await updateDraft(draft)
  } else {
    apiCall = 'create'
    draftResponse = await createDraft(draft)
  }

  if (!draftResponse.error) {
    console.log('saveFinancingStatementDraft ' + apiCall + ' draft successful for documentId ' +
                draftResponse.financingStatement?.documentId)
  }
  return draftResponse
}

/** Format Securities Act Notices to remove empty properties and meet date api requirements. */
const formatSecuritiesActNotices = (notices: Array<AddEditSaNoticeIF>): Array<AddEditSaNoticeIF> => {
  return cloneDeep(notices).map(notice => ({
    ...removeEmptyProperties(notice),
    ...(!!notice.effectiveDateTime && {
      effectiveDateTime: convertToISO8601LastMinute(notice.effectiveDateTime)
    }),
    securitiesActOrders: notice.securitiesActOrders?.map(order => ({
      ...removeEmptyProperties(order),
      orderDate: convertToISO8601LastMinute(order.orderDate)
    }))
  }))
}

/** Save new financing statement. Data to be saved is in the store state model. */
export async function saveFinancingStatement (stateModel:StateModelIF): Promise<FinancingStatementIF> {
  const draft:DraftIF = stateModel.registration.draft
  const trustLength = stateModel.registration.lengthTrust
  const parties:AddPartiesIF = stateModel.registration.parties
  const collateral:AddCollateralIF = stateModel.registration.collateral
  const isStaff = getIsStaff(stateModel)
  const statement:FinancingStatementIF = {
    type: stateModel.registration.registrationType.registrationTypeAPI,
    lifeInfinite: trustLength.lifeInfinite,
    registeringParty: parties.registeringParty,
    securedParties: parties.securedParties,
    debtors: parties.debtors,
    vehicleCollateral: collateral.vehicleCollateral,
    generalCollateral: collateral.generalCollateral,
    clientReferenceId: stateModel.folioOrReferenceNumber,
    authorizationReceived: true
  }
  if (!trustLength.lifeInfinite) {
    statement.lifeYears = trustLength.lifeYears
  }
  // Include Securities Act Notices Array for SE Registration Type
  if(usePprRegistration().isSecurityActNotice.value) {
    // Clean empty properties
    statement.securitiesActNotices = formatSecuritiesActNotices(stateModel.registration.securitiesActNotices)
  }
  if (stateModel.registration.registrationTypeOtherDesc) {
    statement.otherTypeDescription = stateModel.registration.registrationTypeOtherDesc
  }
  if (draft !== null && draft.financingStatement !== null) {
    statement.documentId = draft.financingStatement.documentId
  }
  if (statement.type === APIRegistrationTypes.SECURITY_AGREEMENT) {
    statement.trustIndenture = trustLength.trustIndenture
  } else if (statement.type === APIRegistrationTypes.REPAIRERS_LIEN) {
    statement.lienAmount = trustLength.lienAmount
    statement.surrenderDate = trustLength.surrenderDate + 'T08:00:00+00:00'
    // Don't need for a Repairer's Lien registration.
    delete statement.lifeYears
    delete statement.lifeInfinite
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
  let apiResponse
  if (isStaff) {
    apiResponse = await staffFinancingStatement(statement, stateModel.staffPayment)
  } else {
    apiResponse = await createFinancingStatement(statement, '')
  }

  if (apiResponse !== undefined && apiResponse.error !== undefined) {
    console.error('saveFinancingStatement failed: ' + apiResponse.error.statusCode + ': ' +
                  apiResponse.error.message)
  }
  return apiResponse
}

/** Save new discharge registration. Data to be saved is in the store state model. */
export async function saveDischarge (stateModel:StateModelIF): Promise<DischargeRegistrationIF> {
  const registration:DischargeRegistrationIF = {
    baseRegistrationNumber: stateModel.registration.registrationNumber,
    debtorName: stateModel.registration.confirmDebtorName,
    registeringParty: stateModel.registration.parties.registeringParty,
    clientReferenceId: stateModel.folioOrReferenceNumber,
    authorizationReceived: true
  }
  if (registration.clientReferenceId === null || registration.clientReferenceId.trim().length < 1) {
    delete registration.clientReferenceId
  }
  registration.registeringParty = cleanupParty(registration.registeringParty)
  // Now save the registration.
  console.log('saveDischarge calling api for base registration number ' + registration.baseRegistrationNumber + '.')

  let apiResponse
  if (getIsStaff(stateModel)) {
    apiResponse = await staffDischarge(registration, stateModel.staffPayment)
  } else {
    apiResponse = await createDischarge(registration, '')
  }

  if (apiResponse !== undefined && apiResponse.error !== undefined) {
    console.error('saveDischarge failed: ' + apiResponse.error.statusCode + ': ' +
                  apiResponse.error.message)
  }
  return apiResponse
}

/** Setup a financing statement draft for editing. Get the previously saved draft and hydrate the state model. */
export async function setupFinancingStatementDraft (stateModel:StateModelIF, documentId:string): Promise<StateModelIF> {
  const draft: DraftIF = await getDraft(documentId)
  stateModel.registration.draft = draft
  if (draft.error) return stateModel

  const registrationType: RegistrationTypeIF = RegistrationTypes.find(obj => {
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
  if (draft.financingStatement.type === APIRegistrationTypes.SECURITY_ACT_NOTICE) {
    stateModel.registration.securitiesActNotices = draft.financingStatement.securitiesActNotices
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
  stateModel.registration.collateral.valid = vcValid || gcValid

  if (draft.financingStatement.clientReferenceId) {
    stateModel.folioOrReferenceNumber = draft.financingStatement.clientReferenceId
  }
  return stateModel
}

export function setupStateModelFromAmendmentDraft (stateModel:StateModelIF, draft:DraftIF): StateModelIF {
  const draftAmendment:AmendmentStatementIF = draft.amendmentStatement
  stateModel.registration.amendmentDescription = draftAmendment.description
  if (!stateModel.registration.parties.registeringParty) {
    stateModel.registration.parties.registeringParty = draftAmendment.registeringParty
  }
  if (!stateModel.registration.confirmDebtorName) {
    stateModel.registration.confirmDebtorName = draftAmendment.debtorName
  }
  if (draftAmendment.courtOrderInformation) {
    stateModel.registration.courtOrderInformation = draftAmendment.courtOrderInformation
  }
  if (draftAmendment.clientReferenceId) {
    stateModel.folioOrReferenceNumber = draftAmendment.clientReferenceId
  }
  if ('addTrustIndenture' in draftAmendment && draftAmendment.addTrustIndenture &&
      !stateModel.originalRegistration.lengthTrust.trustIndenture) {
    stateModel.registration.lengthTrust.trustIndenture = true
    stateModel.registration.lengthTrust.action = ActionTypes.EDITED
  } else if ('removeTrustIndenture' in draftAmendment && draftAmendment.removeTrustIndenture &&
              stateModel.originalRegistration.lengthTrust.trustIndenture) {
    stateModel.registration.lengthTrust.trustIndenture = false
    stateModel.registration.lengthTrust.action = ActionTypes.EDITED
  }

  // Parse Securities Notices
  if (draftAmendment.addSecuritiesActNotices || draftAmendment.deleteSecuritiesActNotices) {
    stateModel.registration.securitiesActNotices = parseNoticeAmendmentDraft(
      stateModel.registration.securitiesActNotices,
      draftAmendment.addSecuritiesActNotices,
      draftAmendment.deleteSecuritiesActNotices
    )
  }

  const parties:AddPartiesIF = stateModel.registration.parties
  // setup secured parties.
  setupRegistrationPartyList(parties.securedParties, draftAmendment.addSecuredParties,
    draftAmendment.deleteSecuredParties)
  // setup debtors.
  setupRegistrationPartyList(parties.debtors, draftAmendment.addDebtors, draftAmendment.deleteDebtors)

  const collateral:AddCollateralIF = stateModel.registration.collateral
  if (!collateral.generalCollateral) {
    collateral.generalCollateral = []
  }
  if (!collateral.vehicleCollateral) {
    collateral.vehicleCollateral = []
  }
  // setup vehicle collateral.
  setupVehicleCollateralList(collateral.vehicleCollateral, draftAmendment.addVehicleCollateral,
    draftAmendment.deleteVehicleCollateral)
  // setup general collateral: guessing how this works with the add only solution.
  const gcAdd = draftAmendment.addGeneralCollateral
  const gcDelete = draftAmendment.deleteGeneralCollateral
  // Add or edit
  if (gcAdd && gcAdd.length > 0) {
    for (let i = 0; i < gcAdd.length; i++) {
      const newCollateral:GeneralCollateralIF = {
        descriptionAdd: gcAdd[i].description
      }
      if (gcDelete && gcDelete.length > 0) {
        for (let j = 0; j < gcDelete.length; j++) {
          if (gcDelete[j].collateralId === gcAdd[i].collateralId) {
            newCollateral.descriptionDelete = gcDelete[j].description
          }
        }
      }
      collateral.generalCollateral.push(newCollateral)
    }
  }
  // Delete only
  if ((!gcAdd || gcAdd.length === 0) && gcDelete && gcDelete.length > 0) {
    for (let i = 0; i < gcDelete.length; i++) {
      const newCollateral:GeneralCollateralIF = {
        descriptionDelete: gcDelete[i].description
      }
      collateral.generalCollateral.push(newCollateral)
    }
  }
  return stateModel
}

/**
 * Setup an amendment from draft for editing. Get the previously saved draft and hydrate the state model.
 * Assumes a separate, previous call to load the base registration data.
 */
export async function setupAmendmentStatementFromDraft (
  stateModel:StateModelIF,
  documentId:string
): Promise<StateModelIF> {
  const draft: DraftIF = await getDraft(documentId)
  stateModel.registration.draft = draft
  if (draft.error) return stateModel
  if (!draft.amendmentStatement) {
    // user will continue with a blank amendment (should never happen)
    console.error('getDraft failed: no draft amendment data found.')
    return stateModel
  }
  return setupStateModelFromAmendmentDraft(stateModel, draft)
}

/** Save new discharge registration. Data to be saved is in the store state model. */
export async function saveRenewal (stateModel:StateModelIF): Promise<RenewRegistrationIF> {
  const trustLength = stateModel.registration.lengthTrust

  const registration:RenewRegistrationIF = {
    baseRegistrationNumber: stateModel.registration.registrationNumber,
    debtorName: stateModel.registration.confirmDebtorName,
    registeringParty: stateModel.registration.parties.registeringParty,
    clientReferenceId: stateModel.folioOrReferenceNumber,
    authorizationReceived: true
  }
  if (registration.clientReferenceId === null || registration.clientReferenceId.trim().length < 1) {
    delete registration.clientReferenceId
  }
  registration.registeringParty = cleanupParty(registration.registeringParty)

  // No lifeYears, lifeInfinite for RL renewal
  if (stateModel.registration.registrationType.registrationTypeAPI === APIRegistrationTypes.REPAIRERS_LIEN) {
    registration.courtOrderInformation = stateModel.registration.courtOrderInformation
    if (registration.courtOrderInformation.orderDate.length === 10) {
      // add current time to date
      const now = new Date()
      const d = new Date(`${registration.courtOrderInformation.orderDate}T${now.toTimeString().substring(0, 8)}`)
      // convert back to UTC (required to pass api validation properly in some edge cases)
      let month = `${d.getUTCMonth() + 1}`
      let day = `${d.getUTCDate()}`
      let hours = `${d.getUTCHours()}`
      if (month.length < 2) month = `0${month}`
      if (day.length < 2) day = `0${day}`
      if (hours.length < 2) hours = `0${hours}`
      const orderDateUTC = `${d.getUTCFullYear()}-${month}-${day}T${hours}:00:00+00:00`
      registration.courtOrderInformation.orderDate = orderDateUTC
    }
  } else if (trustLength.lifeInfinite) {
    registration.lifeInfinite = trustLength.lifeInfinite
  } else {
    registration.lifeYears = trustLength.lifeYears
  }

  // Now save the registration.
  console.log('save renewal calling api for base registration number ' + registration.baseRegistrationNumber + '.')

  let apiResponse
  if (getIsStaff(stateModel)) {
    apiResponse = await staffRenewal(registration, stateModel.staffPayment)
  } else {
    apiResponse = await createRenewal(registration, '')
  }

  if (apiResponse.error) {
    console.error('save renewal failed: ' + apiResponse.error.statusCode + ': ' +
                  apiResponse.error.message)
  }
  return apiResponse
}

export function cleanupParty (party: PartyIF): PartyIF {
  if (party.action !== null) {
    delete party.action
  }
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
    if (party.businessName !== null && party.businessName !== '' && party.businessName !== undefined) {
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
