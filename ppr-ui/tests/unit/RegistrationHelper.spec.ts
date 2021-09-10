// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import CompositionApi from '@vue/composition-api'
import { getVuexStore } from '@/store'
import { mount, createLocalVue } from '@vue/test-utils'

import {
  cleanupParty,
  saveDischarge,
  saveFinancingStatement,
  saveFinancingStatementDraft,
  setupFinancingStatementDraft
} from '@/utils'
import { DischargeRegistrationIF, PartyIF, FinancingStatementIF, DraftIF, StateModelIF } from '@/interfaces'
import { APIRegistrationTypes } from '@/enums'

// Components
import { FolioNumberSummary } from '@/components/common'

// Other
import {
  mockedDebtorNames,
  mockedDraftFinancingStatementAll,
  mockedSelectSecurityAgreement,
  mockedRegisteringParty1,
  mockedSecuredParties1,
  mockedDebtors1,
  mockedVehicleCollateral1,
  mockedGeneralCollateral1,
  mockedNewRegStep1
} from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

describe('Registration API Helper Tests', () => {
  // Use mock service directly - account id can be anything.
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('PPR_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/ppr/api/v1/')

  let wrapper: any

  beforeEach(async () => {
    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(CompositionApi)
    localVue.use(Vuetify)
    document.body.setAttribute('data-app', 'true')
    wrapper = mount(FolioNumberSummary, {
      localVue,
      propsData: {},
      store,
      vuetify
    })
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement)
    await store.dispatch('setLengthTrust', mockedNewRegStep1)
    await store.dispatch('setFolioOrReferenceNumber', 'ABC123')
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1,
      debtors: mockedDebtors1
    })
    await store.dispatch('setAddCollateral', {
      vehicleCollateral: mockedVehicleCollateral1,
      generalCollateral: mockedGeneralCollateral1
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('save new security agreement', async () => {
    var statement:FinancingStatementIF = await saveFinancingStatement(wrapper.vm.$store.state.stateModel)
    // console.log(JSON.stringify(statement))
    expect(statement.createDateTime).toBeDefined()
    expect(statement.baseRegistrationNumber).toBeDefined()
    expect(statement.payment).toBeDefined()
  })

  it('save new repairers lien', async () => {
    const model:StateModelIF = wrapper.vm.$store.state.stateModel
    model.registration.lengthTrust.lienAmount = '1000.00'
    model.registration.lengthTrust.surrenderDate = '2021-07-28T07:00:00+00:00'
    model.registration.lengthTrust.trustIndenture = false
    model.registration.lengthTrust.lifeYears = 1
    var statement:FinancingStatementIF = await saveFinancingStatement(model)
    // console.log(JSON.stringify(statement))
    expect(statement.createDateTime).toBeDefined()
    expect(statement.baseRegistrationNumber).toBeDefined()
    expect(statement.payment).toBeDefined()
  })

  it('save new financing statement draft', async () => {
    await store.dispatch('setDraft', mockedDraftFinancingStatementAll)
    var draft:DraftIF = await saveFinancingStatementDraft(wrapper.vm.$store.state.stateModel)
    // console.log(JSON.stringify(statement))
    expect(draft.createDateTime).toBeDefined()
    expect(draft.financingStatement.documentId).toBeDefined()
  })

  it('save new RL financing statement draft', async () => {
    const testDraft = (JSON.parse(JSON.stringify(mockedDraftFinancingStatementAll)))
    testDraft.financingStatement.type = APIRegistrationTypes.REPAIRERS_LIEN
    testDraft.financingStatement.surrenderDate = '2021-07-28T07:00:00+00:00'
    testDraft.financingStatement.lienAmount = '1000'
    testDraft.financingStatement.lifeYears = 1
    await store.dispatch('setDraft', testDraft)
    var draft:DraftIF = await saveFinancingStatementDraft(wrapper.vm.$store.state.stateModel)
    // console.log(JSON.stringify(statement))
    expect(draft.createDateTime).toBeDefined()
    expect(draft.financingStatement.documentId).toBeDefined()
  })

  it('verify cleanupParty works as expected', async () => {
    var party:PartyIF = mockedRegisteringParty1
    party.address.streetAdditional = ''
    party = cleanupParty(party)
    // console.log(JSON.stringify(party))
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
    await store.dispatch('resetNewRegistration', null)
    var stateModel:StateModelIF = await setupFinancingStatementDraft(wrapper.vm.$store.state.stateModel, 'D0034001')
    // console.log(JSON.stringify(stateModel))
    expect(stateModel.registration.draft).toBeDefined()
    expect(stateModel.registration.draft.error).toBeUndefined()
    expect(stateModel.registration.draft.financingStatement).toBeDefined()
    expect(stateModel.registration.draft.financingStatement.documentId).toBe('D0034001')
    expect(stateModel.folioOrReferenceNumber).toBeDefined()
    expect(stateModel.registration.registrationType).toBeDefined()
    expect(stateModel.registration.registrationType.registrationTypeUI).toBeDefined()
    expect(stateModel.registration.parties.registeringParty).toBeDefined()
    expect(stateModel.registration.lengthTrust).toBeDefined()
    expect(stateModel.registration.lengthTrust.lifeYears).toBe(5)
    expect(stateModel.registration.registrationType.registrationTypeAPI).toBe(APIRegistrationTypes.SECURITY_AGREEMENT)
    expect(stateModel.registration.parties.securedParties).toBeDefined()
    expect(stateModel.registration.parties.securedParties.length).toBe(1)
    expect(stateModel.registration.parties.debtors).toBeDefined()
    expect(stateModel.registration.parties.debtors.length).toBe(1)
    expect(stateModel.registration.collateral.vehicleCollateral).toBeDefined()
    expect(stateModel.registration.collateral.vehicleCollateral.length).toBe(1)
    // Update store and check it.
    await store.dispatch('setDraft', stateModel.registration.draft)
    await store.dispatch('setLengthTrust', stateModel.registration.lengthTrust)
    await store.dispatch('setAddCollateral', stateModel.registration.collateral)
    await store.dispatch('setAddSecuredPartiesAndDebtors', stateModel.registration.parties)
    await store.dispatch('setFolioOrReferenceNumber', stateModel.folioOrReferenceNumber)
    const storeModel:StateModelIF = wrapper.vm.$store.state.stateModel
    expect(storeModel.registration.draft).toBeDefined()
    expect(storeModel.registration.draft.error).toBeUndefined()
    expect(storeModel.registration.draft.financingStatement).toBeDefined()
    expect(storeModel.registration.draft.financingStatement.documentId).toBe('D0034001')
    expect(storeModel.folioOrReferenceNumber).toBe(stateModel.folioOrReferenceNumber)
    expect(storeModel.registration.registrationType).toBeDefined()
    expect(storeModel.registration.registrationType.registrationTypeUI).toBeDefined()
    expect(storeModel.registration.parties.registeringParty).toBeDefined()
    expect(storeModel.registration.lengthTrust).toBeDefined()
    expect(storeModel.registration.lengthTrust.lifeYears).toBe(5)
    expect(storeModel.registration.registrationType.registrationTypeAPI).toBe(APIRegistrationTypes.SECURITY_AGREEMENT)
    expect(storeModel.registration.parties.securedParties).toBeDefined()
    expect(storeModel.registration.parties.securedParties.length).toBe(1)
    expect(storeModel.registration.parties.debtors).toBeDefined()
    expect(storeModel.registration.parties.debtors.length).toBe(1)
    expect(storeModel.registration.collateral.vehicleCollateral).toBeDefined()
    expect(storeModel.registration.collateral.vehicleCollateral.length).toBe(1)
  })
})

describe('Registration API Helper Discharge Tests', () => {
  // Use mock service directly - account id can be anything.
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('PPR_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/ppr/api/v1/')

  let wrapper: any

  beforeEach(async () => {
    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(CompositionApi)
    localVue.use(Vuetify)
    document.body.setAttribute('data-app', 'true')
    wrapper = mount(FolioNumberSummary, {
      localVue,
      propsData: {},
      store,
      vuetify
    })
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement)
    await store.dispatch('setRegistrationNumber', '023001B')
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      registeringParty: mockedRegisteringParty1
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('save business debtor with folio', async () => {
    await store.dispatch('setFolioOrReferenceNumber', 'A-00000402')
    await store.dispatch('setRegistrationConfirmDebtorName', mockedDebtorNames[0])

    var registration:DischargeRegistrationIF = await saveDischarge(wrapper.vm.$store.state.stateModel)
    // console.log(JSON.stringify(statement))
    expect(registration.createDateTime).toBeDefined()
    expect(registration.baseRegistrationNumber).toBeDefined()
    expect(registration.dischargeRegistrationNumber).toBeDefined()
    expect(registration.payment).toBeDefined()
  })

  it('save individual debtor with folio', async () => {
    await store.dispatch('setFolioOrReferenceNumber', 'A-00000402')
    await store.dispatch('setRegistrationConfirmDebtorName', mockedDebtorNames[2])

    var registration:DischargeRegistrationIF = await saveDischarge(wrapper.vm.$store.state.stateModel)
    // console.log(JSON.stringify(statement))
    expect(registration.createDateTime).toBeDefined()
    expect(registration.baseRegistrationNumber).toBeDefined()
    expect(registration.dischargeRegistrationNumber).toBeDefined()
    expect(registration.payment).toBeDefined()
  })

  it('save business debtor no folio', async () => {
    await store.dispatch('setRegistrationConfirmDebtorName', mockedDebtorNames[0])

    var registration:DischargeRegistrationIF = await saveDischarge(wrapper.vm.$store.state.stateModel)
    // console.log(JSON.stringify(statement))
    expect(registration.createDateTime).toBeDefined()
    expect(registration.baseRegistrationNumber).toBeDefined()
    expect(registration.dischargeRegistrationNumber).toBeDefined()
    expect(registration.payment).toBeDefined()
  })
})
