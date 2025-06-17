import { APIRegistrationTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'

export const RegistrationFees = {
  [FeeSummaryTypes.NEW_MHR]: {
    filingFees: 50,
    filingType: APIRegistrationTypes.MANUFACTURED_HOME_REGISTRATION,
    filingTypeCode: FeeSummaryTypes.NEW_MHR,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 50,
    waived: false
  },
  [FeeSummaryTypes.MHR_PUBLIC_AMENDMENT]: {
    filingFees: 15,
    filingType: APIRegistrationTypes.MHR_PUBLIC_AMENDMENT,
    filingTypeCode: FeeSummaryTypes.MHR_PUBLIC_AMENDMENT,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 15,
    waived: false
  },
  [FeeSummaryTypes.MHR_STAFF_CORRECTION]: {
    filingFees: 0,
    filingType: APIRegistrationTypes.MHR_CORRECTION_STAFF,
    filingTypeCode: FeeSummaryTypes.MHR_STAFF_CORRECTION,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 0,
    waived: true,
    showFeeDesc: true
  },
  [FeeSummaryTypes.MHR_CLIENT_CORRECTION]: {
    filingFees: 15,
    filingType: APIRegistrationTypes.MHR_CORRECTION_CLIENT,
    filingTypeCode: FeeSummaryTypes.MHR_CLIENT_CORRECTION,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 15,
    waived: false,
    showFeeDesc: true
  },
  [FeeSummaryTypes.NO_FEE]: {
    filingFees: 0,
    filingType: APIRegistrationTypes.MANUFACTURED_HOME_REGISTRATION,
    filingTypeCode: FeeSummaryTypes.NEW_MHR,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0, // Staff Service Fee?
    tax: {
      gst: 0,
      pst: 0
    },
    total: 50,
    waived: true
  }
}
