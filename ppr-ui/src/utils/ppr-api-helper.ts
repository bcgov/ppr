// Libraries
import { axios } from '@/utils/axios-ppr'
import { StatusCodes } from 'http-status-codes'

// Interfaces
import {
  DraftIF,
  SearchCriteriaIF,
  SearchResponseIF,
  SearchResultIF,
  UserSettingsIF,
  SearchPartyIF
} from '@/interfaces'
import { SearchHistoryResponseIF } from '@/interfaces/ppr-api-interfaces/search-history-response-interface'

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

export const successfulPPRResponses = [StatusCodes.OK, StatusCodes.CREATED, StatusCodes.ACCEPTED]

// Submit a search query (search step 1) request.
export async function search (searchCriteria: SearchCriteriaIF): Promise<SearchResponseIF> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.post<SearchResponseIF>('searches', searchCriteria, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      // need a unique value for the data table (can't use the index in the list)
      const results = data.results
      if (results) {
        results.forEach((item, index) => { item.id = index + 1 })
        data.results = results
      }
      return data
    }).catch(error => {
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

// Update selected matches in search response (search step 2a)
export async function updateSelected (searchId: string, selected: Array<SearchResultIF>): Promise<number> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.put(`searches/${searchId}`, selected, config)
    .then(
      response => { return response.status }
    ).catch(
      error => {
        return error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR
      }
    )
}

// Submit selected matches in search response (search step 2b)
export async function submitSelected (searchId: string, selected: Array<SearchResultIF>): Promise<number> {
  const url = sessionStorage.getItem('PPR_API_URL')
  // change to application/pdf to get the pdf right away
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.post(`search-results/${searchId}`, selected, config)
    .then(
      response => { return response.status }
    ).catch(
      error => {
        return error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR
      }
    )
}

// Get pdf for a previous search
export async function searchPDF (searchId: string): Promise<any> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/pdf' }, responseType: 'blob' as 'json' }
  return axios.get(`search-results/${searchId}`, config)
    .then(
      response => {
        const data = response?.data
        if (!data) {
          throw new Error('Invalid API response')
        }
        return data
      }
    ).catch(
      error => {
        return {
          error: {
            statusCode: error?.response?.status || StatusCodes.NOT_FOUND
          }
        }
      }
    )
}

// Get user search history
export async function searchHistory (): Promise<SearchHistoryResponseIF> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.get<Array<SearchResponseIF>>('search-history', config)
    .then(
      response => {
        const data = response?.data
        if (!data) {
          throw new Error('Invalid API response')
        }
        return { searches: data }
      }
    ).catch(
      error => {
        return {
          searches: null,
          error: {
            statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
            message: error?.response?.data?.message
          }
        }
      }
    )
}

// Get current user settings (404 if user not created in PPR yet)
export async function getPPRUserSettings (): Promise<UserSettingsIF> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.get('user-profile', config)
    .then(
      response => {
        const data: UserSettingsIF = response?.data
        if (!data) {
          throw new Error('Invalid API response')
        }
        return data
      }
    ).catch(
      error => {
        return {
          paymentConfirmationDialog: true,
          selectConfirmationDialog: true,
          error: {
            statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
            message: error?.response?.data?.message
          }
        }
      }
    )
}

// Update user setting
export async function updateUserSettings (setting: string, settingValue: boolean): Promise<UserSettingsIF> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.patch('user-profile', { [`${setting}`]: settingValue }, config)
    .then(
      response => {
        const data: UserSettingsIF = response?.data
        if (!data) {
          throw new Error('Invalid API response')
        }
        return data
      }
    ).catch(
      error => {
        return {
          paymentConfirmationDialog: true,
          selectConfirmationDialog: true,
          error: {
            statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
            message: error?.response?.data?.message
          }
        }
      }
    )
}

// Create default request base URL and headers.
function getDefaultConfig (): Object {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return config
}

// Save a new draft.
export async function createDraft (draft: DraftIF): Promise<DraftIF> {
  return axios.post<DraftIF>('drafts', draft, getDefaultConfig())
    .then(response => {
      const data: DraftIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      draft.error = {
        statusCode: error?.response?.status,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause
      }
      return draft
    })
}

// Update an existing draft.
export async function updateDraft (draft: DraftIF): Promise<DraftIF> {
  var documentId = draft.financingStatement?.documentId
  if (documentId === undefined || documentId === '') {
    draft.error = {
      statusCode: StatusCodes.BAD_REQUEST,
      message: 'Draft update request invalid: no document ID. Use createDraft instead.'
    }
    return draft
  }
  return axios.put<DraftIF>(('drafts/' + documentId), draft, getDefaultConfig())
    .then(response => {
      const data: DraftIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      draft.error = {
        statusCode: error?.response?.status,
        message: error?.response?.data?.errorMessage + ' ' + error?.response?.data?.rootCause
      }
      return draft
    })
}

// Submit a search query (search step 1) request.
export async function partyCodeSearch (nameOrCode: string): Promise<[SearchPartyIF]> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  let fuzzyName = ''
  if (!/^\d+$/.test(nameOrCode)) {
    fuzzyName = '?fuzzyNameSearch=true'
  }
  return axios.get(`party-codes/head-offices/${nameOrCode}${fuzzyName}`, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(
      error => {
        return {
          error: {
            statusCode: error?.response?.status || StatusCodes.NOT_FOUND
          }
        }
      }
    )
}
