// Libraries
import { axios } from '@/utils/axios-ppr'
import { StatusCodes } from 'http-status-codes'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import {
  ManufacturedHomeSearchResultIF,
  SearchResponseIF,
  MhrSearchCriteriaIF
} from '@/interfaces'
import { ErrorCategories, ErrorCodes } from '@/enums'
import { useSearch } from '@/composables/useSearch'
const { mapMhrSearchType } = useSearch()

// Submit an mhr search query request.
export async function mhrSearch (
  searchCriteria: MhrSearchCriteriaIF,
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

      // Map query return type to differentiate between ppr & mhr in ui
      data.searchQuery.type = mapMhrSearchType(data.searchQuery.type, true)

      // need a unique value for the data table (can't use the index in the list)
      const results = data.results
      if (results) {
        results.forEach((item, index) => {
          item.id = index + 1
          item.selected = false
        })
        data.results = results
      }
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

function mhrStaffPaymentParameters (staffPayment: StaffPaymentIF) {
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

// Submit selected matches in mhr search results
export async function submitSelectedMhr (
  searchId: string,
  selected: Array<ManufacturedHomeSearchResultIF>,
  staffPayment: StaffPaymentIF = null,
  isCertified: boolean = false
): Promise<number> {
  const url = sessionStorage.getItem('MHR_API_URL')
  // change to application/pdf to get the pdf right away
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  let extraParams = ''

  if (staffPayment) {
    extraParams += '?'

    // do they want a certified search
    if (isCertified) {
      extraParams += 'certified=True'
    }

    const paymentParams = mhrStaffPaymentParameters(staffPayment)
    if (paymentParams.length > 0) {
      if (isCertified) extraParams += '&'
      extraParams += `${paymentParams}`
    }
  }

  return axios
    .post(`search-results/${searchId}${extraParams}`, selected, config)
    .then(response => {
      return response.status
    })
    .catch(error => {
      return error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR
    })
}

// Get pdf for a previous search
export async function searchMhrPDF (searchId: string): Promise<any> {
  const url = sessionStorage.getItem('MHR_API_URL')
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
