// Libraries
import { axios } from '@/utils/axios-ppr'
import { StatusCodes } from 'http-status-codes'

// Interfaces
import { SearchCriteriaIF, SearchResponseIF, SearchResultIF, UserSettingsIF } from '@/interfaces'
import { mockedSearchResponse, mockedDefaultUserSettingsResponse } from '../../tests/unit/test-data'
import { APISearchTypes, UISearchTypes } from '@/enums'
import { SearchHistoryResponseIF } from '@/interfaces/ppr-api-interfaces/search-history-response-interface'

/**
 * Actions that provide integration with the ppr api.
 *
 * Successful responses
 * 200 GET search histroy / PDF
 * 201 POST search / final result selection
 * 202 PUT result select update
 * 422 POST search (but no results found) -- hopefully we can change this to 201 with response
 *
 * Possible errors include:
 * 400 BAD_REQUEST
 * 401 NOT_AUTHORIZED
 * 500 INTERNAL_SERVER_ERROR
 */

// Submit a search query (search step 1) request.
export async function search (searchCriteria: SearchCriteriaIF): Promise<SearchResponseIF> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { 'Content-Type': 'application/json' } }
  return axios.post<SearchResponseIF>('searches', searchCriteria, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
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
  const config = { baseURL: url, headers: { 'Content-Type': 'application/json' } }
  return axios.put(`search-result/${searchId}`, selected, config)
    .then(
      response => { return response.status }
    ).catch(
      error => {
        console.error(error)
        return error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR
      }
    )
}

// Submit selected matches in search response (search step 2b)
export async function submitSelected (searchId: string, selected: Array<SearchResultIF>): Promise<number> {
  const url = sessionStorage.getItem('PPR_API_URL')
  // change to application/pdf to get the pdf right away
  const config = { baseURL: url, headers: { 'Content-Type': 'application/json' } }
  return axios.post(`search-result/${searchId}`, selected, config)
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
  const config = { baseURL: url, headers: { 'Content-Type': 'application/pdf' } }
  return axios.get(`search-result/${searchId}`, config)
    .then(
      response => {
        const data = response?.data
        if (data) {
          throw new Error('Invalid API response')
        }
        return data
      }
    ).catch(
      error => {
        return error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR
      }
    )
}

// Get user search history
export async function searchHistory (): Promise<SearchHistoryResponseIF> {
  const url = sessionStorage.getItem('PPR_API_URL')
  const config = { baseURL: url, headers: { 'Content-Type': 'application/pdf' } }
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
  const config = { baseURL: url, headers: { 'Content-Type': 'application/json' } }
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
  const config = { baseURL: url, headers: { 'Content-Type': 'application/json' } }
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
