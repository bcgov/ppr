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
  BaseHeaderIF,
  RegistrationSortIF
} from '@/interfaces'
import { SearchHistoryResponseIF } from '@/interfaces/ppr-api-interfaces/search-history-response-interface'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces' // eslint-disable-line no-unused-vars
import { DraftTypes, ErrorCategories, SettingOptions } from '@/enums'

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

const UIFilterToApiFilter = {
  endDate: 'endDateTime',
  folNum: 'clientReferenceId',
  orderBy: 'sortCriteriaName',
  orderVal: 'sortDirection',
  regBy: 'registeringName',
  regNum: 'registrationNumber',
  regType: 'registrationType',
  startDate: 'startDateTime',
  status: 'statusType'
}

// add sorting params for registration history/draft api calls
function addSortParams (url: string, sortOptions: RegistrationSortIF): string {
  const sortKeys = Object.keys(sortOptions)
  // add all set filters as params to the call
  for (const i in sortKeys) {
    // convert to api expected value (too tied in with header logic to change earlier)
    if (sortOptions[sortKeys[i]] === 'createDateTime') {
      // sortKeys[i] === orderBy (only case this will happen)
      sortOptions[sortKeys[i]] = 'startDateTime'
    }
    // add timestamp onto datetime param values
    if (sortOptions[sortKeys[i]] && ['startDateTime', 'endDateTime'].includes(UIFilterToApiFilter[sortKeys[i]])) {
      // ensure its not already converted
      if (sortOptions[sortKeys[i]].length < 11) {
        sortOptions[sortKeys[i]] = sortOptions[sortKeys[i]]
        // convert to local date object
        const d = new Date(`${sortOptions[sortKeys[i]]}T00:00:00`)
        // get the offset from utc in hours
        let offset = `${d.getTimezoneOffset() / 60}`
        let tzDiff = '-'
        if (offset[0] === '-') {
          // flip tzDiff and remove negative from offset
          tzDiff = '+'
          offset = offset.substring(1, offset.length)
        }
        // check if offset has minutes
        const minsIndex = offset.indexOf('.')
        if (minsIndex !== -1) {
          // remove the minutes from the offset (not perfect but better than an error)
          offset = offset.substring(0, minsIndex)
        }
        // add zero to offset if necessary
        if (offset.length < 2) offset = `0${offset}`
        // add desired timestamp
        let time = '00:00:00'
        if (UIFilterToApiFilter[sortKeys[i]] === 'endDateTime') time = '23:59:59'
        // combine date, timestamp and tz info
        sortOptions[sortKeys[i]] = `${d.toISOString().substring(0, 10)}T${time}${tzDiff}${offset}:00`
      }
    }
    if (sortOptions[sortKeys[i]]) {
      url += `&${UIFilterToApiFilter[sortKeys[i]]}=${sortOptions[sortKeys[i]]}`
    }
  }
  return url
}

// Create default request base URL and headers.
function getDefaultConfig (): Object {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return config
}

function staffPaymentParameters (staffPayment: StaffPaymentIF) {
  let paymentParams = ''
  // filled out staff payment parameters
  if (staffPayment) {
    switch (staffPayment.option) {
      case StaffPaymentOptions.FAS:
        paymentParams = paymentParams + 'routingSlipNumber=' + staffPayment.routingSlipNumber
        break
      case StaffPaymentOptions.BCOL:
        paymentParams = paymentParams + 'bcolAccountNumber=' + staffPayment.bcolAccountNumber
        paymentParams = paymentParams + '&datNumber=' + staffPayment.datNumber
        break
    }
  }
  return paymentParams
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        searchId: 'error',
        maxResultsSize: 0,
        totalResultsSize: 0,
        returnedResultsSize: 0,
        searchQuery: searchCriteria, // Echoes request
        results: [],
        error: {
          category: ErrorCategories.SEARCH,
          statusCode: StatusCodes.GATEWAY_TIMEOUT,
          message: error?.response?.data?.message,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
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
  const paymentParams = staffPaymentParameters(staffPayment)
  if (paymentParams.length > 0) {
    extraParams = extraParams + '&'
  }
  extraParams = extraParams + paymentParams
  return search(searchCriteria, extraParams)
}

// Save a new financing statement (staff)
export async function staffFinancingStatement (
  statement: FinancingStatementIF,
  staffPayment: StaffPaymentIF
): Promise<FinancingStatementIF> {
  let extraParams = ''
  const paymentParams = staffPaymentParameters(staffPayment)
  if (paymentParams.length > 0) {
    extraParams = '?'
  }
  extraParams = extraParams + paymentParams
  return createFinancingStatement(statement, extraParams)
}

// Save a new financing statement (staff)
export async function staffAmendment (
  statement: AmendmentStatementIF,
  staffPayment: StaffPaymentIF
): Promise<AmendmentStatementIF> {
  let extraParams = ''
  const paymentParams = staffPaymentParameters(staffPayment)
  if (paymentParams.length > 0) {
    extraParams = '?'
  }
  extraParams = extraParams + paymentParams
  return createAmendmentStatement(statement, extraParams)
}

export async function staffDischarge (
  discharge: DischargeRegistrationIF,
  staffPayment: StaffPaymentIF
): Promise<DischargeRegistrationIF> {
  let extraParams = ''
  const paymentParams = staffPaymentParameters(staffPayment)
  if (paymentParams.length > 0) {
    extraParams = '?'
  }
  extraParams = extraParams + paymentParams
  return createDischarge(discharge, extraParams)
}

export async function staffRenewal (
  renewal: RenewRegistrationIF,
  staffPayment: StaffPaymentIF
): Promise<RenewRegistrationIF> {
  let extraParams = ''
  const paymentParams = staffPaymentParameters(staffPayment)
  if (paymentParams.length > 0) {
    extraParams = '?'
  }
  extraParams = extraParams + paymentParams
  return createRenewal(renewal, extraParams)
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
  selected: Array<SearchResultIF>,
  shouldCallback: boolean
): Promise<number> {
  const url = sessionStorage.getItem('PPR_API_URL')
  // change to application/pdf to get the pdf right away
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  let callback = ''
  if (shouldCallback) {
    callback = '?callbackURL=PPR_UI'
  }
  return axios
    .post(`search-results/${searchId}${callback}`, selected, config)
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
          category: ErrorCategories.REPORT_GENERATION,
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        searches: null,
        error: {
          category: ErrorCategories.HISTORY_SEARCHES,
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        paymentConfirmationDialog: true,
        selectConfirmationDialog: true,
        defaultDropDowns: true,
        defaultTableFilters: true,
        error: {
          category: ErrorCategories.ACCOUNT_SETTINGS,
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        paymentConfirmationDialog: true,
        selectConfirmationDialog: true,
        defaultDropDowns: true,
        defaultTableFilters: true,
        error: {
          category: ErrorCategories.ACCOUNT_SETTINGS,
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      draft.error = {
        category: ErrorCategories.REGISTRATION_SAVE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
        detail: error?.parsed?.rootCause?.detail,
        type: error?.parsed?.rootCause?.type
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
      category: ErrorCategories.REGISTRATION_SAVE,
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      draft.error = {
        category: ErrorCategories.REGISTRATION_SAVE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
        detail: error?.parsed?.rootCause?.detail,
        type: error?.parsed?.rootCause?.type
      }
      return draft
    })
}

// Get an existing draft (any type) by documentId.
export async function getDraft (documentId: string): Promise<DraftIF> {
  const draft: DraftIF = {}
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      draft.error = {
        category: ErrorCategories.DRAFT_LOAD,
        statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
        detail: error?.parsed?.rootCause?.detail,
        type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        category: ErrorCategories.DRAFT_DELETE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
        detail: error?.parsed?.rootCause?.detail,
        type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
          message: error?.response?.data?.errorMessage,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
          message: error?.response?.data?.errorMessage,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}

// Get registration history
export async function registrationHistory (sortOptions: RegistrationSortIF, page: number): Promise<{
  registrations: RegistrationSummaryIF[],
  error: ErrorIF
}> {
  const baseURL = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: baseURL, headers: { Accept: 'application/json' } }
  const url = addSortParams(
    `financing-statements/registrations?collapse=true&pageNumber=${page}&fromUI=true`,
    sortOptions
  )
  return axios
    .get(url, config)
    .then(response => {
      const data = response?.data as RegistrationSummaryIF[]
      if (!data) {
        throw new Error('Invalid API response')
      }
      return { registrations: data, error: null }
    })
    .catch(error => {
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        registrations: null,
        error: {
          category: ErrorCategories.HISTORY_REGISTRATIONS,
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.errorMessage,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}

// Get draft history
export async function draftHistory (sortOptions: RegistrationSortIF): Promise<{
  drafts: DraftResultIF[],
  error: ErrorIF
}> {
  if (!sortOptions) {
    // set it to empty sort options
    sortOptions = {
      endDate: null,
      folNum: '',
      orderBy: '',
      orderVal: '',
      regBy: '',
      regNum: '',
      regParty: '',
      regType: '',
      secParty: '',
      startDate: null,
      status: ''
    }
  }
  const baseURL = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: baseURL, headers: { Accept: 'application/json' } }
  const url = addSortParams('drafts?fromUI=true', sortOptions)
  return axios
    .get(url, config)
    .then(response => {
      const data = response?.data as DraftResultIF[]
      if (!data) {
        throw new Error('Invalid API response')
      }
      return { drafts: data, error: null }
    })
    .catch(error => {
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        drafts: null,
        error: {
          category: ErrorCategories.HISTORY_REGISTRATIONS,
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.errorMessage,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}

// Save a new financing statement.
export async function createFinancingStatement (
  statement: FinancingStatementIF,
  extraParams: string
): Promise<FinancingStatementIF> {
  return axios
    .post<FinancingStatementIF>(
      `financing-statements${extraParams}`,
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      statement.error = {
        category: ErrorCategories.REGISTRATION_CREATE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
        detail: error?.parsed?.rootCause?.detail,
        type: error?.parsed?.rootCause?.type
      }
      return statement
    })
}

// Save a new financing statement.
export async function createAmendmentStatement (
  statement: AmendmentStatementIF,
  extraParams: string
): Promise<AmendmentStatementIF> {
  return axios
    .post<AmendmentStatementIF>(
      `financing-statements/${statement.baseRegistrationNumber}/amendments${extraParams}`,
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
        category: ErrorCategories.REGISTRATION_CREATE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
        detail: error?.parsed?.rootCause?.detail,
        type: error?.parsed?.rootCause?.type
      }
      return statement
    })
}

// Save a discharge registration.
export async function createDischarge (
  discharge: DischargeRegistrationIF,
  extraParams: string
): Promise<DischargeRegistrationIF> {
  return axios
    .post<DischargeRegistrationIF>(
      `financing-statements/${discharge.baseRegistrationNumber}/discharges${extraParams}`,
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      discharge.error = {
        category: ErrorCategories.REGISTRATION_CREATE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
        detail: error?.parsed?.rootCause?.detail,
        type: error?.parsed?.rootCause?.type
      }
      return discharge
    })
}

// Save a renewal registration.
export async function createRenewal (
  renewal: RenewRegistrationIF,
  extraParams: string
): Promise<RenewRegistrationIF> {
  return axios
    .post<RenewRegistrationIF>(
      `financing-statements/${renewal.baseRegistrationNumber}/renewals${extraParams}`,
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      renewal.error = {
        category: ErrorCategories.REGISTRATION_CREATE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
        detail: error?.parsed?.rootCause?.detail,
        type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        type: null,
        registeringParty: null,
        securedParties: [],
        debtors: [],
        error: {
          category: ErrorCategories.REGISTRATION_LOAD,
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
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
          message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}

// Get registration summary information
export async function getRegistrationSummary (
  registrationNum: string,
  refreshing: boolean
): Promise<(RegistrationSummaryIF)> {
  registrationNum = registrationNum?.toUpperCase()
  return axios
    .get(`financing-statements/registrations/${registrationNum}`, getDefaultConfig())
    .then(response => {
      const data = response?.data as RegistrationSummaryIF
      if (!data) throw new Error('Invalid API response')
      if (!refreshing && data.inUserList) {
        data.error = {
          statusCode: StatusCodes.CONFLICT,
          message: 'Registration is already added to this account.'
        }
      }
      return data
    })
    .catch(error => {
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
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
          category: ErrorCategories.HISTORY_REGISTRATIONS,
          statusCode: error?.response?.status,
          message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        category: ErrorCategories.REGISTRATION_DELETE,
        statusCode: error?.response?.status,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause,
        detail: error?.parsed?.rootCause?.detail,
        type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        error: {
          category: ErrorCategories.REPORT_GENERATION,
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
          message: error?.response?.data?.errorMessage,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
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
      if (error?.response?.data) {
        try {
          error.parsed = JSON.parse(error?.response?.data.replaceAll('\n', '').replaceAll('\\', ''))
          error.parsed.rootCause = error.parsed.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"status_code":"')
            .replaceAll(',', '",')
          error.parsed.rootCause = `{${error.parsed.rootCause}"}`
          error.parsed.rootCause = JSON.parse(error.parsed.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        searches: null,
        error: {
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.errorMessage,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}
