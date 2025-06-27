export default {
  ConnectFeeWidget: {
    feeSummary: {
      title: 'Fee Summary',
      total: 'Total Fees',
      noFee: 'No Fee',
      priorityFees: 'Priority Fees',
      futureEffectiveFees: 'Future Effective Fees',
      serviceFees: 'Service Fee',
      itemLabels: {
        PLACEHOLDER: '-',
        TEST: 'This is test entry',
        undefined: '-',
        new_mhr: 'Manufactured Home Registration',
        mhr_public_amendment: 'Public Amendment',
        mhr_staff_correction: 'Registry Correction',
        mhr_client_correction: 'Registry Correction',
        manufactured_home_search: 'Manufactured Home Search',
        combined_home_search: 'Combined Home and Lien Search',
        mhr_re_registration: 'Re-Register Manufactured Home',
        mhr_transport_permit: 'Location Change'
      },
      feeDesc: {
        mhr_staff_correction: 'Staff Error or Omission',
        mhr_client_correction: 'Client Error or Omission',
        mhr_transport_permit: 'Transport Permit'
      }
    },
    paymentMethod: {
      DIRECT_PAY: 'Credit Card',
      PAD: 'Pre-authorized Debit (PAD) {account}',
      BCOL: 'Online Banking',
      JV: 'Journal Voucher',
      undefined: 'Default'
    },
    payingWith: {
      DIRECT_PAY: 'Paying with Credit Card',
      PAD: 'Paying with Pre-authorized Debit (PAD) {account}',
      BCOL: 'Paying with Online Banking',
      JV: 'Paying with Journal Voucher',
      undefined: 'Paying with default method'
    }
  },
  currency: {
    cad: 'CAD',
    usd: 'USD'
  }
}
