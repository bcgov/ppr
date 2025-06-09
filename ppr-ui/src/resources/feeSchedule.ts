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
