// Libraries
import { axios } from '@/utils/axios-ppr'
import { StatusCodes } from 'http-status-codes'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'

// Interfaces
import {
  AmendmentStatementIF,
  DischargeRegistrationIF,
  DraftIF,
  DraftResultIF,
  FinancingStatementIF,
  SearchCriteriaIF,
  SearchResponseIF,
  SearchResultIF,
  UserSettingsIF,
  SearchPartyIF,
  DebtorNameIF,
  RegistrationSummaryIF,
  RenewRegistrationIF,
  ErrorIF,
  BaseHeaderIF
} from '@/interfaces'
import { SearchHistoryResponseIF } from '@/interfaces/ppr-api-interfaces/search-history-response-interface'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces' // eslint-disable-line no-unused-vars
import { SettingOptions } from '@/enums'

/**
 * Actions that provide integration with the ppr api.
 *
 * Successful responses
 * 200 GET search histroy / PDF / final result selection
 * 201 POST search
 * 202 PUT result select update
 *
 * Possible errors include:
 * 400 BAD_REQUEST
 * 401 NOT_AUTHORIZED
 * 500 INTERNAL_SERVER_ERROR
 */

// Create default request base URL and headers.
function getDefaultConfig (): Object {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return config
}

export const successfulPPRResponses = [
  StatusCodes.OK,
  StatusCodes.CREATED,
  StatusCodes.ACCEPTED
]

// Submit a search query (search step 1) request.
export async function search (
  searchCriteria: SearchCriteriaIF,
  extraParams: string
): Promise<SearchResponseIF> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios
    .post<SearchResponseIF>(`searches${extraParams}`, searchCriteria, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      // need a unique value for the data table (can't use the index in the list)
      const results = data.results
      if (results) {
        results.forEach((item, index) => {
          item.id = index + 1
        })
        data.results = results
      }
      return data
    })
    .catch(error => {
      return {
        searchId: 'error',
        maxResultsSize: 0,
        totalResultsSize: 0,
        returnedResultsSize: 0,
        searchQuery: searchCriteria, // Echoes request
        results: [],
        error: {
          statusCode: error?.response?.status,
          message: error?.response?.data?.message
        }
      }
    })
}

// Submit a search query (search step 1) request.
export async function staffSearch (
  searchCriteria: SearchCriteriaIF,
  staffPayment: StaffPaymentIF,
  certified: boolean
): Promise<SearchResponseIF> {
  let extraParams = '?'
  // do they want a certified search
  if (certified) {
    extraParams = extraParams + 'certified=True'
  }
  // filled out staff payment parameters
  if (staffPayment) {
    if (extraParams.length > 0) {
      extraParams = extraParams + '&'
    }
    switch (staffPayment.option) {
      case StaffPaymentOptions.FAS:
        extraParams = extraParams + 'routingSlipNumber=' + staffPayment.routingSlipNumber
        break
      case StaffPaymentOptions.BCOL:  
        extraParams = extraParams + '&bcolAccountNumber=' + staffPayment.bcolAccountNumber
        extraParams = extraParams + '&datNumber=' + staffPayment.datNumber
        break
    }
  }
  return search(searchCriteria, extraParams)
}

// Update selected matches in search response (search step 2a)
export async function updateSelected (
  searchId: string,
  selected: Array<SearchResultIF>
): Promise<number> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios
    .put(`searches/${searchId}`, selected, config)
    .then(response => {
      return response.status
    })
    .catch(error => {
      return error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR
    })
}

// Submit selected matches in search response (search step 2b)
export async function submitSelected (
  searchId: string,
  selected: Array<SearchResultIF>
): Promise<number> {
  const url = sessionStorage.getItem('PPR_API_URL')
  // change to application/pdf to get the pdf right away
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios
    .post(`search-results/${searchId}`, selected, config)
    .then(response => {
      return response.status
    })
    .catch(error => {
      return error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR
    })
}

// Get pdf for a previous search
export async function searchPDF (searchId: string): Promise<any> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = {
    baseURL: url,
    headers: { Accept: 'application/pdf' },
    responseType: 'blob' as 'json'
  }
  return axios
    .get(`search-results/${searchId}`, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND
        }
      }
    })
}

// Get user search history
export async function searchHistory (): Promise<SearchHistoryResponseIF> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios
    .get<Array<SearchResponseIF>>('search-history', config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return { searches: data }
    })
    .catch(error => {
      return {
        searches: null,
        error: {
          statusCode:
            error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message
        }
      }
    })
}

// Get current user settings (404 if user not created in PPR yet)
export async function getPPRUserSettings (): Promise<UserSettingsIF> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios
    .get('user-profile', config)
    .then(response => {
      const data: UserSettingsIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        paymentConfirmationDialog: true,
        selectConfirmationDialog: true,
        defaultDropDowns: true,
        defaultTableFilters: true,
        error: {
          statusCode:
            error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message
        }
      }
    })
}

// Update user setting
export async function updateUserSettings (
  setting: SettingOptions,
  settingValue: boolean | { columns: BaseHeaderIF[] }
): Promise<UserSettingsIF> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios
    .patch('user-profile', { [`${setting}`]: settingValue }, config)
    .then(response => {
      const data: UserSettingsIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        paymentConfirmationDialog: true,
        selectConfirmationDialog: true,
        defaultDropDowns: true,
        defaultTableFilters: true,
        error: {
          statusCode:
            error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message
        }
      }
    })
}

// Save a new draft.
export async function createDraft (draft: DraftIF): Promise<DraftIF> {
  return axios
    .post<DraftIF>('drafts', draft, getDefaultConfig())
    .then(response => {
      const data: DraftIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      draft.error = {
        statusCode: error?.response?.status,
        message:
          error?.response?.data?.errorMessage +
          ' ' +
          error?.response?.data?.rootCause
      }
      return draft
    })
}

// Update an existing draft.
export async function updateDraft (draft: DraftIF): Promise<DraftIF> {
  let documentId = ''
  if (draft.financingStatement) {
    documentId = draft.financingStatement?.documentId
  } else if (draft.amendmentStatement) {
    documentId = draft.amendmentStatement?.documentId
  }
  if (!documentId || documentId === '') {
    draft.error = {
      statusCode: StatusCodes.BAD_REQUEST,
      message:
        'Draft update request invalid: no document ID. Use createDraft instead.'
    }
    return draft
  }
  return axios
    .put<DraftIF>('drafts/' + documentId, draft, getDefaultConfig())
    .then(response => {
      const data: DraftIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      draft.error = {
        statusCode: error?.response?.status,
        message:
          error?.response?.data?.errorMessage +
          ' ' +
          error?.response?.data?.rootCause
      }
      return draft
    })
}

// Get an existing draft (any type) by documentId.
export async function getDraft (documentId: string): Promise<DraftIF> {
  var draft:DraftIF
  if (documentId === undefined || documentId === '') {
    draft.error = {
      statusCode: StatusCodes.BAD_REQUEST,
      message:
        'Draft lookup request invalid: no document ID.'
    }
    return draft
  }
  return axios
    .get<DraftIF>('drafts/' + documentId, getDefaultConfig())
    .then(response => {
      const data: DraftIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      draft.error = {
        statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
        message:
          error?.response?.data?.errorMessage +
          ' ' +
          error?.response?.data?.rootCause
      }
      return draft
    })
}

// Delete an existing draft (any type) by documentId.
export async function deleteDraft (documentId: string): Promise<ErrorIF> {
  if (!documentId) return { statusCode: StatusCodes.BAD_REQUEST, message: 'No document ID given.' }
  return axios
    .delete<void>(`drafts/${documentId}`, getDefaultConfig())
    .then(response => {
      return { statusCode: response?.status as StatusCodes }
    })
    .catch(error => {
      return {
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message:
          error?.response?.data?.errorMessage +
          ' ' +
          error?.response?.data?.rootCause
      }
    })
}

// Search the party code db
export async function partyCodeSearch (
  nameOrCode: string, exactSearch: boolean
): Promise<[SearchPartyIF]> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  let fuzzyName = ''
  if (!/^\d+$/.test(nameOrCode) && !exactSearch) {
    fuzzyName = '?fuzzyNameSearch=true'
  }
  return axios
    .get(`party-codes/head-offices/${nameOrCode}${fuzzyName}`, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND
        }
      }
    })
}

// Search for the crown charge client party codes linked to the account.
export async function partyCodeAccount (): Promise<[SearchPartyIF]> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios
    .get('party-codes/accounts', config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND
        }
      }
    })
}

// Get registration history
export async function registrationHistory (): Promise<{
  registrations: RegistrationSummaryIF[],
  error: ErrorIF
}> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios
    .get('financing-statements/registrations?collapse=true', config)
    .then(response => {
      const data = response?.data as RegistrationSummaryIF[]
      if (!data) {
        throw new Error('Invalid API response')
      }
      return { registrations: data, error: null }
    })
    .catch(error => {
      return {
        registrations: null,
        error: {
          statusCode:
            error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message
        }
      }
    })
}

// Get draft history
export async function draftHistory (): Promise<{
  drafts: DraftResultIF[],
  error: ErrorIF
}> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios
    .get('drafts', config)
    .then(response => {
      const data = response?.data as DraftResultIF[]
      if (!data) {
        throw new Error('Invalid API response')
      }
      return { drafts: data, error: null }
    })
    .catch(error => {
      return {
        drafts: null,
        error: {
          statusCode:
            error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message
        }
      }
    })
}

// Save a new financing statement.
export async function createFinancingStatement (
  statement: FinancingStatementIF
): Promise<FinancingStatementIF> {
  return axios
    .post<FinancingStatementIF>(
      'financing-statements',
      statement,
      getDefaultConfig()
    )
    .then(response => {
      const data: FinancingStatementIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      statement.error = {
        statusCode: error?.response?.status,
        message:
          error?.response?.data?.errorMessage +
          ' ' +
          error?.response?.data?.rootCause
      }
      return statement
    })
}

// Save a new financing statement.
export async function createAmendmentStatement (statement: AmendmentStatementIF): Promise<AmendmentStatementIF> {
  return axios
    .post<AmendmentStatementIF>(
      `financing-statements/${statement.baseRegistrationNumber}/amendments`,
      statement,
      getDefaultConfig()
    )
    .then(response => {
      const data: AmendmentStatementIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      statement.error = {
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message:
          error?.response?.data?.errorMessage +
          ' ' +
          error?.response?.data?.rootCause
      }
      return statement
    })
}

// Save a discharge registration.
export async function createDischarge (discharge: DischargeRegistrationIF): Promise<DischargeRegistrationIF> {
  return axios
    .post<DischargeRegistrationIF>(
      `financing-statements/${discharge.baseRegistrationNumber}/discharges`,
      discharge,
      getDefaultConfig())
    .then(response => {
      const data: DischargeRegistrationIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      discharge.error = {
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message:
          error?.response?.data?.errorMessage +
          ' ' +
          error?.response?.data?.rootCause
      }
      return discharge
    })
}

// Save a renewal registration.
export async function createRenewal (renewal: RenewRegistrationIF): Promise<RenewRegistrationIF> {
  return axios
    .post<RenewRegistrationIF>(
      `financing-statements/${renewal.baseRegistrationNumber}/renewals`,
      renewal,
      getDefaultConfig())
    .then(response => {
      const data: RenewRegistrationIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      renewal.error = {
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message:
          error?.response?.data?.errorMessage +
          ' ' +
          error?.response?.data?.rootCause
      }
      return renewal
    })
}

// Get an existing financing statement.
export async function getFinancingStatement (
  current: boolean,
  registrationNum: string
): Promise<FinancingStatementIF> {
  return axios
    .get<FinancingStatementIF>(
      `financing-statements/${registrationNum}?current=${current}`,
      getDefaultConfig()
    )
    .then(response => {
      const data: FinancingStatementIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        type: null,
        registeringParty: null,
        securedParties: [],
        debtors: [],
        error: {
          statusCode: error?.response?.status,
          message:
            error?.response?.data?.errorMessage +
            ' ' +
            error?.response?.data?.rootCause
        }
      }
    })
}

// Add registration to My Registrations
export async function addRegistrationSummary (
  registrationNum: string
): Promise<RegistrationSummaryIF> {
  registrationNum = registrationNum?.toUpperCase()
  return axios
    .post(`financing-statements/registrations/${registrationNum}`, {}, getDefaultConfig())
    .then(response => {
      const data = response?.data as RegistrationSummaryIF
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        baseRegistrationNumber: '',
        createDateTime: '',
        path: '',
        registeringParty: '',
        registrationClass: '',
        registrationDescription: '',
        registrationNumber: '',
        registrationType: null,
        securedParties: '',
        error: {
          statusCode: error?.response?.status,
          message:
            error?.response?.data?.errorMessage +
            ' ' +
            error?.response?.data?.rootCause
        }
      }
    })
}

// Get registration summary information
export async function getRegistrationSummary (
  registrationNum: string
): Promise<(RegistrationSummaryIF)> {
  registrationNum = registrationNum?.toUpperCase()
  return axios
    .get(`financing-statements/registrations/${registrationNum}`, getDefaultConfig())
    .then(response => {
      const data = response?.data as RegistrationSummaryIF
      if (!data) throw new Error('Invalid API response')
      if (data.inUserList) {
        data.error = {
          statusCode: StatusCodes.CONFLICT,
          message: 'Registration is already added to this account.'
        }
      }
      return data
    })
    .catch(error => {
      return {
        baseRegistrationNumber: '',
        createDateTime: '',
        path: '',
        registeringParty: '',
        registrationClass: '',
        registrationDescription: '',
        registrationNumber: '',
        registrationType: null,
        securedParties: '',
        error: {
          statusCode: error?.response?.status,
          message:
            error?.response?.data?.errorMessage +
            ' ' +
            error?.response?.data?.rootCause
        }
      }
    })
}

// delete registration summary information from table
export async function deleteRegistrationSummary (
  registrationNum: string
): Promise<ErrorIF> {
  return axios
    .delete(`financing-statements/registrations/${registrationNum}`, getDefaultConfig())
    .then(response => {
      return { statusCode: response?.status as StatusCodes }
    })
    .catch(error => {
      return {
        statusCode: error?.response?.status,
        message:
          error?.response?.data?.errorMessage +
          ' ' +
          error?.response?.data?.rootCause
      }
    })
}

// Get pdf for a registration
export async function registrationPDF (pdfPath: string): Promise<any> {
  const url = sessionStorage.getItem('PPR_API_URL')
  // remove ppr/api/v1 from path
  pdfPath = pdfPath.replace('/ppr/api/v1', '')
  const config = {
    baseURL: url,
    headers: { Accept: 'application/pdf' },
    responseType: 'blob' as 'json'
  }
  return axios
    .get(pdfPath, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND
        }
      }
    })
}

// Get debtor names for a registration
export async function debtorNames (registrationNum: string): Promise<[DebtorNameIF]> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios
    .get(`financing-statements/${registrationNum}/debtorNames`, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        searches: null,
        error: {
          statusCode:
            error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message
        }
      }
    })
}
