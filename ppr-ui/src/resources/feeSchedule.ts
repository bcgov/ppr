import { APIRegistrationTypes } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'

export const RegistrationFees = {
  // PPR REGISTRATION FEES
  [FeeSummaryTypes.NEW]: {
    filingFees: 0,
    filingType: 'New Registration',
    filingTypeCode: FeeSummaryTypes.NEW,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 10,
    serviceFees: 0,
    quantity: 1,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 15,
    waived: false,
    showFeeDesc: true,
    feeDescOverride: 'Select registration length'
  },
  [FeeSummaryTypes.AMEND]: {
    filingFees: 10,
    filingType: 'Amend Registration',
    filingTypeCode: FeeSummaryTypes.AMEND,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 5,
    serviceFees: 0,
    quantity: 1,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 15,
    waived: false,
    showFeeDesc: false,
  },
  [FeeSummaryTypes.RENEW]: {
    filingFees: 0,
    filingType: 'Renew Registration',
    filingTypeCode: FeeSummaryTypes.RENEW,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 5,
    serviceFees: 0,
    quantity: 1,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 10,
    waived: false,
    showFeeDesc: true,
    feeDescOverride: 'Select registration renewal length'
  },
  [FeeSummaryTypes.DISCHARGE]: {
    filingFees: 0,
    filingType: 'Discharge Registration',
    filingTypeCode: FeeSummaryTypes.DISCHARGE,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    quantity: 1,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 10,
    waived: true,
    showFeeDesc: false
  },

  // MHR REGISTRATION FEES
  [FeeSummaryTypes.NEW_MHR]: {
    filingFees: 50,
    filingType: APIRegistrationTypes.MANUFACTURED_HOME_REGISTRATION,
    filingTypeCode: FeeSummaryTypes.NEW_MHR,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    quantity: 1,
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
    quantity: 1,
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
    quantity: 1,
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
    quantity: 1,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 15,
    waived: false,
    showFeeDesc: true
  },
  [FeeSummaryTypes.MHR_RE_REGISTRATION]: {
    filingFees: 50,
    filingType: APIRegistrationTypes.MHR_RE_REGISTRATION,
    filingTypeCode: FeeSummaryTypes.MHR_RE_REGISTRATION,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    quantity: 1,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 50,
    waived: false,
    showFeeDesc: false
  },
  [FeeSummaryTypes.MHR_SEARCH]: {
    filingFees: 7,
    filingType: 'Manufactured Home Search',
    filingTypeCode: FeeSummaryTypes.MHR_SEARCH,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 1.50,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 7,
    quantity: 1,
    quantityDesc: '$7.00 each',
    waived: false,
    showFeeDesc: false
  },
  [FeeSummaryTypes.MHR_COMBINED_SEARCH]: {
    filingFees: 12,
    filingType: 'Combined Home and Lien search',
    filingTypeCode: FeeSummaryTypes.MHR_COMBINED_SEARCH,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 1.50,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 12,
    quantity: 1,
    quantityDesc: '$12.00 each',
    waived: false,
    showFeeDesc: false
  },
  [FeeSummaryTypes.MHR_PERMIT_DEFAULT]: {
    filingFees: 0,
    filingType: 'Location Change',
    filingTypeCode: FeeSummaryTypes.MHR_PERMIT_DEFAULT,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 0,
    quantity: 1,
    quantityDesc: '',
    waived: false,
    showFeeDesc: true
  },
  [FeeSummaryTypes.MHR_TRANSPORT_PERMIT]: {
    filingFees: 25,
    filingType: 'Location Change',
    filingTypeCode: FeeSummaryTypes.MHR_TRANSPORT_PERMIT,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 25,
    quantity: 1,
    quantityDesc: '',
    waived: false,
    showFeeDesc: true
  },
  [FeeSummaryTypes.MHR_TRANSPORT_PERMIT_EXTEND]: {
    filingFees: 25,
    filingType: 'Extend Transport Permit',
    filingTypeCode: FeeSummaryTypes.MHR_TRANSPORT_PERMIT_EXTEND,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 25,
    quantity: 1,
    quantityDesc: '',
    waived: false,
    showFeeDesc: true
  },
  [FeeSummaryTypes.MHR_AMEND_TRANSPORT_PERMIT]: {
    filingFees: 15,
    filingType: 'Amend Transport Permit',
    filingTypeCode: FeeSummaryTypes.MHR_AMEND_TRANSPORT_PERMIT,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 15,
    quantity: 1,
    waived: false,
    showFeeDesc: false
  },
  [FeeSummaryTypes.MHR_TRANSPORT_PERMIT_CANCEL]: {
    filingFees: 15,
    filingType: 'Cancel Transport Permit',
    filingTypeCode: FeeSummaryTypes.MHR_TRANSPORT_PERMIT_CANCEL,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 15,
    quantity: 1,
    waived: false,
    showFeeDesc: false
  },
  [FeeSummaryTypes.MHR_LOCATION_CHANGE]: {
    filingFees: 25,
    filingType: 'Registered Location Change',
    filingTypeCode: FeeSummaryTypes.MHR_LOCATION_CHANGE,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 25,
    quantity: 1,
    waived: false,
    showFeeDesc: true
  },
  [FeeSummaryTypes.MHR_OWNER_DEFAULT]: {
    filingFees: 0,
    filingType: 'Ownership Transfer or Change',
    filingTypeCode: FeeSummaryTypes.MHR_OWNER_DEFAULT,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 0,
    quantity: 1,
    quantityDesc: '',
    waived: false,
    showFeeDesc: true
  },
  [FeeSummaryTypes.MHR_TRANSFER]: {
    filingFees: 50,
    filingType: 'Ownership Transfer or Change',
    filingTypeCode: FeeSummaryTypes.MHR_TRANSFER,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 50,
    quantity: 1,
    quantityDesc: '',
    waived: false,
    showFeeDesc: true
  },
  [FeeSummaryTypes.RESIDENTIAL_EXEMPTION]: {
    filingFees: 50,
    filingType: 'Residential Exemption',
    filingTypeCode: FeeSummaryTypes.RESIDENTIAL_EXEMPTION,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 50,
    quantity: 1,
    quantityDesc: '',
    waived: false,
    showFeeDesc: false
  },
  [FeeSummaryTypes.NON_RESIDENTIAL_EXEMPTION]: {
    filingFees: 0,
    filingType: 'Non Residential Exemption',
    filingTypeCode: FeeSummaryTypes.NON_RESIDENTIAL_EXEMPTION,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 0,
    quantity: 1,
    quantityDesc: '',
    waived: true,
    showFeeDesc: false
  },
  [FeeSummaryTypes.PARTY_CODES]: {
    filingFees: 50,
    filingType: 'Create Party Codes',
    filingTypeCode: FeeSummaryTypes.PARTY_CODES,
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 50,
    quantity: 1,
    quantityDesc: '',
    waived: false,
    showFeeDesc: false
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
