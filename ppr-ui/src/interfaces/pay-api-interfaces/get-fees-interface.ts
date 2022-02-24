import { ErrorIF } from '@/interfaces'

export interface GetFeesI {
  error?: ErrorIF
  filingFees: number
  filingType: string
  filingTypeCode: string
  futureEffectiveFees: number
  priorityFees: number
  processingFees: number
  serviceFees: number
  tax: {
    gst: number
    pst: number
  }
  total: number
}