/* eslint-disable no-useless-constructor */
// Libraries
import { axios } from '@/utils/axios-ppr'

// Interfaces
import { SearchCriteriaIF, SearchResponseIF } from '@/interfaces'
import { mockedSearchResponse } from '../../tests/unit/test-data'

const HttpStatus = require('http-status-codes')

/**
 * Actions that provide integration with the ppr api.
 *
 * Possible errors include:
 * 401 NOT_AUTHORIZED
 * 400 BAD_REQUEST
 * 500 INTERNAL_SERVER_ERROR
 */
// export default class PPRApiHelper {
export class PPRApiHelper {
  constructor () {
  }

  /**
   * Submit a search query (search step 1) request.
   * @returns SearchResponseIF, or null if no results.
   */
  search (searchCriteria: SearchCriteriaIF): Promise<any> {
    // console.log('search called')
    const url = sessionStorage.getItem('PPR_API_URL')
    // console.log('URL=' + url)
    const config = { baseURL: url, headers: { 'Content-Type': 'application/json' } }
    return axios.post<SearchResponseIF>('searches', searchCriteria, config)
      .then(response => {
        const data = response?.data
        // console.log('search response data: ' + data)
        if (!data) {
          throw new Error('Invalid API response')
        }
        return data
      }).catch(error => {
        // TODO: do something based on specific api responses
        // console.log('search response error: ' + error)
        // if (error?.response?.status === HttpStatus.NOT_FOUND ||
        //     error?.response?.status === HttpStatus.UNPROCESSABLE_ENTITY) {
        //   return null
        // }
        return {
          // temporary -- forces payment error dialogue popup unless message given
          errors: error?.response?.data?.message || 'payment'
        }
      })
  }
}
