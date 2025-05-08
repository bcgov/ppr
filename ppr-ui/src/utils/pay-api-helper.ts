// external
import { StatusCodes } from 'http-status-codes'
// local
import type { FeeCodes } from '@/composables/fees/enums'
import { ErrorCategories } from '@/enums'
import type { GetFeesI } from '@/interfaces'
import { axios } from '@/utils/axios-pay'

/**
 * Retrieves fee information for a specific fee code from the Payment API.
 * @param {FeeCodes} feeCode - The fee code to retrieve fee information for.
 * @returns {Promise<GetFeesI>} A promise that resolves to fee information or error details.
 */
export async function getFees (feeCode: FeeCodes): Promise<GetFeesI> {
  const url = sessionStorage.getItem('PAY_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.get(`fees/PPR/${feeCode}`, config)
    .then(
      response => {
        const data = response?.data
        if (!data) {
          throw new Error('Unable to obtain fee amounts.')
        }
        return data
      }
    ).catch(error => {
      return {
        error: {
          category: ErrorCategories.ACCOUNT_SETTINGS,
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          detail: error?.parsed?.rootCause?.detail,
          type: error?.parsed?.rootCause?.type
        },
        filingFees: null,
        filingType: null,
        filingTypeCode: null,
        futureEffectiveFees: null,
        priorityFees: null,
        processingFees: null,
        serviceFees: null,
        tax: null,
        total: null
      }
    })
}

/**
 * Retrieves payment information for a specific account from the Payment API.
 * @param {string} accountId - The account ID to retrieve payment information for.
 * @returns {Promise<any>} A promise that resolves to account payment information or error details.
 */
export async function getPaymentInformation (accountId: string): Promise<any> {
  const url = sessionStorage.getItem('PAY_API_URL')
  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.get(`accounts/${accountId}`, config)
    .then(
      response => {
        const data = response?.data
        if (!data) {
          throw new Error('Unable to obtain payment information.')
        }
        return data
      }
    ).catch(error => {
      return {
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
