// Libraries
import { axios } from '@/utils/axios-ppr'
import { StatusCodes } from 'http-status-codes'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import {
  ManufacturedHomeSearchResultIF,
  ManufacturedHomeSearchResponseIF,
  SearchCriteriaIF,
  SearchResponseIF
} from '@/interfaces'
import { ErrorCategories, ErrorCodes } from '@/enums'

// Submit a search query (search step 1) request.
export async function mhrSearch (
  searchCriteria: SearchCriteriaIF,
  extraParams: string
): Promise<any> {
  const url = sessionStorage.getItem('MHR_API_URL')
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
      console.log(data.results)
      return data
    })
    .catch(error => {
      if (error?.response?.data) {
        try {
          error.response.data.rootCause = error.response.data.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"statusCode":"')
            .replaceAll(',', '",')
          error.response.data.rootCause = `{${error.response.data.rootCause}"}`
          error.response.data.rootCause = JSON.parse(error.response.data.rootCause)
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
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          detail: error?.response?.data?.rootCause?.detail,
          type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes
        }
      }
    })
}
