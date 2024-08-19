// Libraries
import { axios } from '@/utils/axios-base'
import { StatusCodes } from 'http-status-codes'
import { ErrorCategories } from '@/enums'
import { LtsaDetailsIF, TitleSummariesIF } from '@/interfaces/ltsa-api-interfaces'

// Submit an LTSA summary query request.
// Testing PID #: 014597365
export async function ltsaSummary (
  pidNumber: string
): Promise<TitleSummariesIF | { error: { category: ErrorCategories; statusCode: any } }> {
  const url = sessionStorage.getItem('LTSA_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }

  return axios
    .get<TitleSummariesIF>(`titledirect/search/api/titleSummaries?filter=parcelIdentifier:${pidNumber}`, config)
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
          category: ErrorCategories.LTSA_REQUEST,
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND
        }
      }
    })
}

export async function ltsaDetails (
  pidNumber: string
): Promise<LtsaDetailsIF | { error: { category: ErrorCategories; statusCode: any } }> {
  const url = sessionStorage.getItem('LTSA_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  const orderPayload = {
    order: {
      productType: 'parcelInfo',
      fileReference: 'folio',
      productOrderParameters: {
        parcelIdentifier: pidNumber
      }
    }
  }

  return axios
    .post<LtsaDetailsIF>('titledirect/search/api/orders', orderPayload, config)
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
          category: ErrorCategories.LTSA_REQUEST,
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND
        }
      }
    })
}
