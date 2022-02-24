// external
import { StatusCodes } from 'http-status-codes'
// local
import { FeeCodes } from '@/composables/fees/enums'
import { ErrorCategories } from '@/enums'
import { GetFeesI } from '@/interfaces'
import { axios } from '@/utils/axios-pay'

// get fees for account
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
