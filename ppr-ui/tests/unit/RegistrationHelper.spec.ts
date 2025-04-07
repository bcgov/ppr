import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import {
  cleanupParty,
  saveAmendmentStatement,
  saveAmendmentStatementDraft,
  saveDischarge,
  saveFinancingStatement,
  saveFinancingStatementDraft,
  setupAmendmentStatementDraft,
  setupFinancingStatementDraft,
  setupStateModelFromAmendmentDraft,
  setupAmendmentStatementFromDraft
} from '@/utils'
import type {
  AmendmentStatementIF,
  DischargeRegistrationIF,
  DraftIF,
  FinancingStatementIF,
  PartyIF,
  StateModelIF
} from '@/interfaces'
import { ActionTypes, APIAmendmentTypes, APIRegistrationTypes } from '@/enums'
import { FolioNumberSummary } from '@/components/common'
import {
  mockedAmendmentCourtOrder,
  mockedDraftAmendmentAdd,
  mockedDraftAmendmentCourtOrder,
  mockedDraftAmendmentDelete,
  mockedDraftAmendmentEdit,
  mockedModelAmendmdmentAdd,
  mockedModelAmendmdmentCourtOrder,
  mockedModelAmendmdmentDelete,
  mockedModelAmendmdmentEdit,
  mockedDraftAmendmentStatement,
  mockedDebtorNames,
  mockedDraftFinancingStatementAll,
  mockedGeneralCollateralAdd,
  mockedGeneralCollateralDelete,
  mockedGeneralCollateralEdit,
  mockedSelectSecurityAgreement,
  mockedRegisteringParty1,
  mockedSecuredParties1,
  mockedSecuredPartiesAdd,
  mockedSecuredPartiesDelete,
  mockedSecuredPartiesEdit,
  mockedDebtors1,
  mockedDebtorsAdd,
  mockedDebtorsDelete,
  mockedDebtorsEdit,
  mockedVehicleCollateral1,
  mockedVehicleCollateralAdd,
  mockedVehicleCollateralDelete,
  mockedVehicleCollateralEdit,
  mockedGeneralCollateral1,
  mockedLengthTrust1,
  mockedVehicleCollateralExisting,
  mockedGeneralCollateralExisting,
  mockedSecuredPartiesExisting,
  mockedDebtorsExisting,
  mockedFinancingStatementComplete,
  mockedDraft1,
  mockedDischargeResponse,
  mockedAmendmentStatementComplete
} from './test-data'
import { createComponent } from './utils'
import { vi } from 'vitest'

const store = useStore()

describe('Registration API Helper Tests', () => {
  let wrapper

  vi.mock('@/utils/ppr-api-helper', () => ({
    createFinancingStatement: vi.fn(() =>
      Promise.resolve({ ...mockedFinancingStatementComplete })),
    createAmendmentStatement: vi.fn(() =>
      Promise.resolve({ ...mockedAmendmentStatementComplete })),
    createDraft: vi.fn(() =>
      Promise.resolve({ ...mockedDraft1 })),
    updateDraft: vi.fn(() =>
      Promise.resolve({ ...mockedDraftAmendmentStatement })),
    getDraft: vi.fn(() =>
      Promise.resolve({ ...mockedDraft1 })),
    createDischarge: vi.fn(() =>
      Promise.resolve({ ...mockedDischargeResponse }))
  }))

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement)
    await store.setLengthTrust(mockedLengthTrust1)
    await store.setFolioOrReferenceNumber('ABC123')
    await store.setAddSecuredPartiesAndDebtors({
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1,
      debtors: mockedDebtors1
    })
    await store.setAddCollateral({
      vehicleCollateral: mockedVehicleCollateral1,
      generalCollateral: mockedGeneralCollateral1
    })
    wrapper = await createComponent(FolioNumberSummary)
    await nextTick()
  })

  it('save new security agreement', async () => {
    const statement:FinancingStatementIF = await saveFinancingStatement(store.getStateModel)
    await nextTick()

    expect(statement.createDateTime).toBeDefined()
    expect(statement.baseRegistrationNumber).toBeDefined()
    expect(statement.payment).toBeDefined()
  })

  it('save new repairers lien', async () => {
    const model:StateModelIF = store.getStateModel
    model.registration.lengthTrust.lienAmount = '1000.00'
    model.registration.lengthTrust.surrenderDate = '2021-07-28T07:00:00+00:00'
    model.registration.lengthTrust.trustIndenture = false
    model.registration.lengthTrust.lifeYears = 1
    const statement:FinancingStatementIF = await saveFinancingStatement(model)
    expect(statement.createDateTime).toBeDefined()
    expect(statement.baseRegistrationNumber).toBeDefined()
    expect(statement.payment).toBeDefined()
  })

  it('save new financing statement draft', async () => {
    await store.setDraft(mockedDraftFinancingStatementAll)
    const draft:DraftIF = await saveFinancingStatementDraft(store.getStateModel)
    await nextTick()

    expect(draft.createDateTime).toBeDefined()
    expect(draft.financingStatement.documentId).toBeDefined()
  })

  it('save new RL financing statement draft', async () => {
    const testDraft = (JSON.parse(JSON.stringify(mockedDraftFinancingStatementAll)))
    testDraft.financingStatement.type = APIRegistrationTypes.REPAIRERS_LIEN
    testDraft.financingStatement.surrenderDate = '2021-07-28T07:00:00+00:00'
    testDraft.financingStatement.lienAmount = '1000'
    testDraft.financingStatement.lifeYears = 1
    await store.setDraft(testDraft)
    const draft:DraftIF = await saveFinancingStatementDraft(store.getStateModel)

    expect(draft.createDateTime).toBeDefined()
    expect(draft.financingStatement.documentId).toBeDefined()
  })

  it('verify cleanupParty works as expected', async () => {
    let party:PartyIF = mockedRegisteringParty1
    party.address.streetAdditional = ''
    party = cleanupParty(party)

    expect(party.businessName).toBeDefined()
    expect(party.address).toBeDefined()
    expect(party.address.street).toBeDefined()
    expect(party.address.city).toBeDefined()
    expect(party.address.region).toBeDefined()
    expect(party.address.postalCode).toBeDefined()
    expect(party.address.country).toBe('CA')
    expect(('streetAdditional' in party.address)).toBeFalsy()
    expect(('deliveryInstructions' in party.address)).toBeFalsy()
    expect(('birthDate' in party)).toBeFalsy()
    expect(('personName' in party)).toBeFalsy()
    expect(('code' in party)).toBeFalsy()
    expect(('emailAddress' in party)).toBeFalsy()
  })

  it('setup financing statement draft for editing', async () => {
    const stateModel:StateModelIF = await setupFinancingStatementDraft(store.getStateModel, 'D9000018')
    await nextTick()

    expect(stateModel.registration.draft).toBeDefined()
    expect(stateModel.registration.draft.error).toBeUndefined()
    expect(stateModel.registration.draft.financingStatement).toBeDefined()
    expect(stateModel.registration.draft.financingStatement.documentId).toBe('D9000018')
    expect(stateModel.folioOrReferenceNumber).toBeDefined()
    expect(stateModel.registration.registrationFlowType).toBeDefined()
    expect(stateModel.registration.parties.registeringParty).toBeDefined()
    expect(stateModel.registration.lengthTrust).toBeDefined()
    expect(stateModel.registration.lengthTrust.lifeYears).toBe(1)
    expect(stateModel.registration.parties.securedParties).toBeDefined()
    expect(stateModel.registration.parties.securedParties.length).toBe(1)
    expect(stateModel.registration.parties.debtors).toBeDefined()
    expect(stateModel.registration.parties.debtors.length).toBe(1)
    expect(stateModel.registration.collateral.vehicleCollateral).toBeDefined()
    expect(stateModel.registration.collateral.vehicleCollateral.length).toBe(2)
  })
})

describe('Registration API Helper Discharge Tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement)
    await store.setRegistrationNumber('023001B')
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1
    })
    wrapper = await createComponent(FolioNumberSummary)
    await nextTick()
  })

  it('save business debtor with folio', async () => {
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])

    const registration:DischargeRegistrationIF = await saveDischarge(store.getStateModel)

    expect(registration.createDateTime).toBeDefined()
    expect(registration.baseRegistrationNumber).toBeDefined()
    expect(registration.dischargeRegistrationNumber).toBeDefined()
    expect(registration.payment).toBeDefined()
  })

  it('save individual debtor with folio', async () => {
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[2])

    const registration:DischargeRegistrationIF = await saveDischarge(store.getStateModel)

    expect(registration.createDateTime).toBeDefined()
    expect(registration.baseRegistrationNumber).toBeDefined()
    expect(registration.dischargeRegistrationNumber).toBeDefined()
    expect(registration.payment).toBeDefined()
  })

  it('save business debtor no folio', async () => {
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])

    const registration:DischargeRegistrationIF = await saveDischarge(store.getStateModel)

    expect(registration.createDateTime).toBeDefined()
    expect(registration.baseRegistrationNumber).toBeDefined()
    expect(registration.dischargeRegistrationNumber).toBeDefined()
    expect(registration.payment).toBeDefined()
  })
})

describe('Registration API Helper Draft Amendment setup tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(FolioNumberSummary)
    await nextTick()
  })

  it('amendment draft add stuff setup', async () => {
    const draft:DraftIF = setupAmendmentStatementDraft(mockedModelAmendmdmentAdd)
    expect(draft.amendmentStatement).toBeDefined()
    const amendDraft:AmendmentStatementIF = draft.amendmentStatement
    expect(amendDraft.baseRegistrationNumber).toBe('0023001B')
    expect(amendDraft.changeType).toBe(APIAmendmentTypes.AMENDMENT)
    expect(amendDraft.description).toBe('Adding')
    expect(amendDraft.registeringParty).toBeDefined()
    expect(amendDraft.clientReferenceId).toBe('UT-AM-001-ADD')
    expect(amendDraft.addDebtors.length).toBe(1)
    expect(amendDraft.deleteDebtors.length).toBe(0)
    expect(amendDraft.addSecuredParties.length).toBe(1)
    expect(amendDraft.deleteSecuredParties.length).toBe(0)
    expect(amendDraft.addGeneralCollateral.length).toBe(1)
    expect(amendDraft.deleteGeneralCollateral.length).toBe(0)
    expect(amendDraft.addVehicleCollateral.length).toBe(1)
    expect(amendDraft.deleteVehicleCollateral.length).toBe(0)
  })

  it('amendment draft delete stuff setup', async () => {
    const draft:DraftIF = setupAmendmentStatementDraft(mockedModelAmendmdmentDelete)
    expect(draft.amendmentStatement).toBeDefined()
    const amendDraft:AmendmentStatementIF = draft.amendmentStatement
    expect(amendDraft.baseRegistrationNumber).toBe('0023001B')
    expect(amendDraft.changeType).toBe(APIAmendmentTypes.AMENDMENT)
    expect(amendDraft.description).toBe('Deleting')
    expect(amendDraft.registeringParty).toBeDefined()
    expect(amendDraft.clientReferenceId).toBe('UT-AM-002-DELETE')
    expect(amendDraft.addDebtors.length).toBe(0)
    expect(amendDraft.deleteDebtors.length).toBe(1)
    expect(amendDraft.addSecuredParties.length).toBe(0)
    expect(amendDraft.deleteSecuredParties.length).toBe(1)
    expect(amendDraft.addGeneralCollateral.length).toBe(0)
    expect(amendDraft.deleteGeneralCollateral.length).toBe(1)
    expect(amendDraft.addVehicleCollateral.length).toBe(0)
    expect(amendDraft.deleteVehicleCollateral.length).toBe(1)
  })

  it('amendment draft edit stuff setup', async () => {
    const draft:DraftIF = setupAmendmentStatementDraft(mockedModelAmendmdmentEdit)
    expect(draft.amendmentStatement).toBeDefined()
    const amendDraft:AmendmentStatementIF = draft.amendmentStatement
    expect(amendDraft.baseRegistrationNumber).toBe('0023001B')
    expect(amendDraft.changeType).toBe(APIAmendmentTypes.AMENDMENT)
    expect(amendDraft.description).toBe('Editing')
    expect(amendDraft.registeringParty).toBeDefined()
    expect(amendDraft.clientReferenceId).toBe('UT-AM-003-EDIT')
    expect(amendDraft.addDebtors.length).toBe(1)
    expect(amendDraft.deleteDebtors.length).toBe(1)
    expect(amendDraft.addSecuredParties.length).toBe(1)
    expect(amendDraft.deleteSecuredParties.length).toBe(1)
    expect(amendDraft.addGeneralCollateral.length).toBe(1)
    expect(amendDraft.deleteGeneralCollateral.length).toBe(1)
    expect(amendDraft.addVehicleCollateral.length).toBe(1)
    expect(amendDraft.deleteVehicleCollateral.length).toBe(1)
  })

  it('amendment draft court order setup', async () => {
    const draft:DraftIF = setupAmendmentStatementDraft(mockedModelAmendmdmentCourtOrder)
    expect(draft.amendmentStatement).toBeDefined()
    const amendDraft:AmendmentStatementIF = draft.amendmentStatement
    expect(amendDraft.baseRegistrationNumber).toBe('0023001B')
    expect(amendDraft.changeType).toBe(APIAmendmentTypes.COURT_ORDER)
    expect(amendDraft.description).toBe('Court Order')
    expect(amendDraft.registeringParty).toBeDefined()
    expect(amendDraft.courtOrderInformation).toBeDefined()
    expect(amendDraft.courtOrderInformation.orderDate).toBe('2021-09-03T18:00:00+00:00')
    expect(amendDraft.clientReferenceId).toBe('UT-AM-004-COURT-ORDER')
    expect(amendDraft.addDebtors.length).toBe(0)
    expect(amendDraft.deleteDebtors.length).toBe(0)
    expect(amendDraft.addSecuredParties.length).toBe(0)
    expect(amendDraft.deleteSecuredParties.length).toBe(0)
    expect(amendDraft.addGeneralCollateral.length).toBe(0)
    expect(amendDraft.deleteGeneralCollateral.length).toBe(0)
    expect(amendDraft.addVehicleCollateral.length).toBe(0)
    expect(amendDraft.deleteVehicleCollateral.length).toBe(0)
  })
})

describe('Registration API Helper Save Draft Amendment Tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement)
    await store.setRegistrationNumber('023003B')
    await store.setDraft(mockedDraftAmendmentStatement)
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])

    wrapper = await createComponent(FolioNumberSummary)
    await nextTick()
  })

  it('save draft add', async () => {
    await store.setGeneralCollateral(mockedGeneralCollateralAdd)
    await store.setVehicleCollateral(mockedVehicleCollateralAdd)
    await store.setAmendmentDescription('Test add')
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1,
      securedParties: mockedSecuredPartiesAdd,
      debtors: mockedDebtorsAdd
    })
    const draft:DraftIF = await saveAmendmentStatementDraft(store.getStateModel)
    expect(draft.type).toBeDefined()
    expect(draft.createDateTime).toBeDefined()
    expect(draft.lastUpdateDateTime).toBeDefined()
    expect(draft.amendmentStatement).toBeDefined()
    expect(draft.amendmentStatement.baseRegistrationNumber).toBeDefined()
    expect(draft.amendmentStatement.documentId).toBeDefined()
  })

  it('save draft delete', async () => {
    await store.setGeneralCollateral(mockedGeneralCollateralDelete)
    await store.setVehicleCollateral(mockedVehicleCollateralDelete)
    await store.setAmendmentDescription('Test delete')
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1,
      securedParties: mockedSecuredPartiesDelete,
      debtors: mockedDebtorsDelete
    })
    const draft:DraftIF = await saveAmendmentStatementDraft(store.getStateModel)
    expect(draft.type).toBeDefined()
    expect(draft.createDateTime).toBeDefined()
    expect(draft.lastUpdateDateTime).toBeDefined()
    expect(draft.amendmentStatement).toBeDefined()
    expect(draft.amendmentStatement.baseRegistrationNumber).toBeDefined()
    expect(draft.amendmentStatement.documentId).toBeDefined()
  })

  it('save draft edit', async () => {
    await store.setGeneralCollateral(mockedGeneralCollateralEdit)
    await store.setVehicleCollateral(mockedVehicleCollateralEdit)
    await store.setAmendmentDescription('Test edit')
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1,
      securedParties: mockedSecuredPartiesEdit,
      debtors: mockedDebtorsEdit
    })
    const draft:DraftIF = await saveAmendmentStatementDraft(store.getStateModel)
    expect(draft.type).toBeDefined()
    expect(draft.createDateTime).toBeDefined()
    expect(draft.lastUpdateDateTime).toBeDefined()
    expect(draft.amendmentStatement).toBeDefined()
    expect(draft.amendmentStatement.baseRegistrationNumber).toBeDefined()
    expect(draft.amendmentStatement.documentId).toBeDefined()
  })

  it('save draft court order', async () => {
    await store.setCourtOrderInformation(mockedAmendmentCourtOrder)
    await store.setVehicleCollateral(mockedVehicleCollateralEdit)
    await store.setAmendmentDescription('Test court order')
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1,
      securedParties: mockedSecuredPartiesAdd,
      debtors: mockedDebtorsAdd
    })
    const draft:DraftIF = await saveAmendmentStatementDraft(store.getStateModel)
    expect(draft.type).toBeDefined()
    expect(draft.createDateTime).toBeDefined()
    expect(draft.lastUpdateDateTime).toBeDefined()
    expect(draft.amendmentStatement).toBeDefined()
    expect(draft.amendmentStatement.baseRegistrationNumber).toBeDefined()
    expect(draft.amendmentStatement.documentId).toBeDefined()
  })
})

describe('Registration API Helper Create Amendment Tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement)
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])

    wrapper = await createComponent(FolioNumberSummary)
    await nextTick()
  })

  it('save amendment court order', async () => {
    await store.setRegistrationNumber('0023001B')
    await store.setCourtOrderInformation(mockedAmendmentCourtOrder)
    await store.setVehicleCollateral(mockedVehicleCollateralAdd)
    await store.setAmendmentDescription('Test court order')
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: mockedRegisteringParty1,
      securedParties: mockedSecuredPartiesAdd,
      debtors: mockedDebtorsAdd
    })

    const registration:AmendmentStatementIF = await saveAmendmentStatement(store.getStateModel)

    expect(registration.createDateTime).toBeDefined()
    expect(registration.baseRegistrationNumber).toBeDefined()
    expect(registration.payment).toBeDefined()
  })
})

describe('Draft Amendment Setup State Model Tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement)
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationNumber('0023001B')
    await store.setVehicleCollateral(mockedVehicleCollateralExisting)
    await store.setGeneralCollateral(mockedGeneralCollateralExisting)
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: null,
      securedParties: mockedSecuredPartiesExisting,
      debtors: mockedDebtorsExisting
    })
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })

    wrapper = await createComponent(FolioNumberSummary)
    await nextTick()
  })

  it('draft add setup model', async () => {
    const model:StateModelIF =
      setupStateModelFromAmendmentDraft(store.getStateModel, mockedDraftAmendmentAdd)
    expect(model.registration.parties.registeringParty).toBeDefined()
    expect(model.folioOrReferenceNumber).toBeDefined()
    expect(model.registration.confirmDebtorName).toBeDefined()
    expect(model.registration.amendmentDescription).toBeDefined()
    expect(model.registration.parties.securedParties.length).toBe(2)
    expect(model.registration.parties.securedParties[1].action).toBe(ActionTypes.ADDED)
    expect(model.registration.parties.debtors.length).toBe(2)
    expect(model.registration.parties.debtors[1].action).toBe(ActionTypes.ADDED)
    expect(model.registration.collateral.vehicleCollateral.length).toBe(2)
    expect(model.registration.collateral.vehicleCollateral[1].action).toBe(ActionTypes.ADDED)
    expect(model.registration.collateral.generalCollateral.length).toBe(2)
    expect(model.registration.collateral.generalCollateral[1].descriptionAdd).toBeDefined()
  })

  it('draft delete setup model', async () => {
    const model:StateModelIF =
      setupStateModelFromAmendmentDraft(store.getStateModel, mockedDraftAmendmentDelete)
    expect(model.registration.parties.registeringParty).toBeDefined()
    expect(model.folioOrReferenceNumber).toBeDefined()
    expect(model.registration.confirmDebtorName).toBeDefined()
    expect(model.registration.amendmentDescription).toBeDefined()
    expect(model.registration.parties.securedParties[0].action).toBe(ActionTypes.REMOVED)
    expect(model.registration.parties.debtors[0].action).toBe(ActionTypes.REMOVED)
    expect(model.registration.collateral.vehicleCollateral[0].action).toBe(ActionTypes.REMOVED)
    expect(model.registration.collateral.generalCollateral[2].descriptionDelete).toBeDefined()
  })

  it('draft edit setup model', async () => {
    const model:StateModelIF =
      setupStateModelFromAmendmentDraft(store.getStateModel, mockedDraftAmendmentEdit)
    expect(model.registration.parties.registeringParty).toBeDefined()
    expect(model.folioOrReferenceNumber).toBeDefined()
    expect(model.registration.confirmDebtorName).toBeDefined()
    expect(model.registration.amendmentDescription).toBeDefined()
    expect(model.registration.parties.securedParties[0].action).toBe(ActionTypes.EDITED)
    expect(model.registration.parties.debtors[0].action).toBe(ActionTypes.EDITED)
    expect(model.registration.collateral.vehicleCollateral[0].action).toBe(ActionTypes.EDITED)
    expect(model.registration.collateral.generalCollateral[3].descriptionAdd).toBeDefined()
    expect(model.registration.collateral.generalCollateral[3].descriptionDelete).toBeDefined()
    expect(model.registration.lengthTrust.action).toBe(ActionTypes.EDITED)
  })

  it('draft court order setup model', async () => {
    const model:StateModelIF =
      setupStateModelFromAmendmentDraft(store.getStateModel, mockedDraftAmendmentCourtOrder)
    expect(model.registration.parties.registeringParty).toBeDefined()
    expect(model.folioOrReferenceNumber).toBeDefined()
    expect(model.registration.confirmDebtorName).toBeDefined()
    expect(model.registration.amendmentDescription).toBeDefined()
    expect(model.registration.courtOrderInformation).toBeDefined()
    expect(model.registration.lengthTrust.action).toBeUndefined()
  })
})

describe('Registration API Helper Load Amendment Draft Tests', () => {
  let wrapper

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement)
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationNumber('0023001B')
    await store.setVehicleCollateral(mockedVehicleCollateralExisting)
    await store.setGeneralCollateral(mockedGeneralCollateralExisting)
    await store.setAddSecuredPartiesAndDebtors({
      registeringParty: null,
      securedParties: mockedSecuredPartiesExisting,
      debtors: mockedDebtorsExisting
    })

    wrapper = await createComponent(FolioNumberSummary)
    await nextTick()
  })

  it('setup security agreement draft', async () => {
    const model:StateModelIF = await setupAmendmentStatementFromDraft(store.getStateModel, 'D0034002')
    expect(model.registration.parties.registeringParty).toBeDefined()
    expect(model.folioOrReferenceNumber).toBeDefined()
    expect(model.registration.confirmDebtorName).toBeDefined()
    expect(model.registration.amendmentDescription).toBeDefined()
  })
})
