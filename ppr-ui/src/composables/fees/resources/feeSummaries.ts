import { FeeSummaryDefaults } from '../enums'
import { FeeSummaryI } from '../interfaces'

export const defaultFeeSummaries = {
  [FeeSummaryDefaults.AMEND]: {
    feeAmount: 10,
    processingFee: 5,
    quantity: 1,
    serviceFee: 1.5
  } as FeeSummaryI,
  [FeeSummaryDefaults.NO_FEE]: {
    feeAmount: 0,
    processingFee: 0,
    quantity: 1,
    serviceFee: 0
  } as FeeSummaryI,
  [FeeSummaryDefaults.DEFAULT_5]: {
    feeAmount: 5,
    processingFee: 10,
    quantity: 1,
    serviceFee: 1.5
  } as FeeSummaryI,
  [FeeSummaryDefaults.DEFAULT_10]: {
    feeAmount: 10,
    processingFee: 10,
    quantity: 1,
    serviceFee: 1.5
  } as FeeSummaryI,
  [FeeSummaryDefaults.DEFAULT_50]: {
    feeAmount: 50,
    processingFee: 0,
    quantity: 1,
    serviceFee: 0
  } as FeeSummaryI,
  [FeeSummaryDefaults.DEFAULT_500]: {
    feeAmount: 500,
    processingFee: 10,
    quantity: 1,
    serviceFee: 1.5
  } as FeeSummaryI,
  [FeeSummaryDefaults.SELECT_5]: {
    feeAmount: 5,
    processingFee: 10,
    quantity: 0,
    serviceFee: 1.5
  } as FeeSummaryI,
  [FeeSummaryDefaults.SEARCH_5]: {
    feeAmount: 5,
    processingFee: 0,
    quantity: 1,
    serviceFee: 0
  } as FeeSummaryI,
  [FeeSummaryDefaults.SEARCH_7]: {
    feeAmount: 7,
    processingFee: 0,
    quantity: 0,
    serviceFee: 1.5
  } as FeeSummaryI,
  [FeeSummaryDefaults.SEARCH_10]: {
    feeAmount: 10,
    processingFee: 0,
    quantity: 0,
    serviceFee: 0
  } as FeeSummaryI,
  [FeeSummaryDefaults.SEARCH_12]: {
    feeAmount: 12,
    processingFee: 0,
    quantity: 0,
    serviceFee: 1.5
  } as FeeSummaryI,
  [FeeSummaryDefaults.SEARCH_15]: {
    feeAmount: 15,
    processingFee: 0,
    quantity: 0,
    serviceFee: 0
  } as FeeSummaryI,
  [FeeSummaryDefaults.UNIT_NOTE_10]: {
    feeAmount: 10,
    processingFee: 0,
    quantity: 1,
    serviceFee: 0
  } as FeeSummaryI,
  [FeeSummaryDefaults.UNIT_NOTE_20]: {
    feeAmount: 20,
    processingFee: 0,
    quantity: 1,
    serviceFee: 0
  } as FeeSummaryI,
  [FeeSummaryDefaults.UNIT_NOTE_50]: {
    feeAmount: 50,
    processingFee: 0,
    quantity: 1,
    serviceFee: 0
  } as FeeSummaryI
}
