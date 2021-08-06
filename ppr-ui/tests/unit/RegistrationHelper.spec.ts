// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import CompositionApi from '@vue/composition-api'
import { getVuexStore } from '@/store'
import { mount, createLocalVue } from '@vue/test-utils'

import { cleanupParty, saveFinancingStatement, saveFinancingStatementDraft } from '@/utils'
import { PartyIF, FinancingStatementIF, DraftIF, StateModelIF } from '@/interfaces'

// Components
import { FolioNumberSummary } from '@/components/common'

// Other
import {
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
    model.lengthTrustStep.lienAmount = '1000.00'
    model.lengthTrustStep.surrenderDate = '2021-07-28T07:00:00+00:00'
    model.lengthTrustStep.trustIndenture = false
    model.lengthTrustStep.lifeYears = 1
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
    testDraft.financingStatement.type = 'RL'
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
})
