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
        mhr_permit_default: 'Location Change',
        mhr_owner_default: 'Ownership Transfer or Change',
        mhr_transport_permit: 'Location Change',
        mhr_amend_transport_permit: 'Amend Transport Permit',
        mhr_transport_permit_cancel: 'Cancel Transport Permit',
        mhr_transport_permit_extend: 'Location Change',
        mhr_location_change: 'Location Change',
        mhr_transfer: 'Ownership Transfer or Change',
        // Bill Of Sale Transfers
        TRANS: 'Ownership Transfer or Change',
        TRANS_FAMILY_ACT: 'Ownership Transfer or Change',
        TRANS_INFORMAL_SALE: 'Ownership Transfer or Change',
        TRANS_QUIT_CLAIM: 'Ownership Transfer or Change',
        TRANS_SEVER_GRANT: 'Ownership Transfer or Change',
        TRANS_RECEIVERSHIP: 'Ownership Transfer or Change',
        TRANS_WRIT_SEIZURE: 'Ownership Transfer or Change',

        // Transfers Due to Death
        TRAND: 'Ownership Transfer or Change',
        TRANS_AFFIDAVIT: 'Ownership Transfer or Change',
        TRANS_ADMIN: 'Ownership Transfer or Change',
        TRANS_WILL: 'Ownership Transfer or Change',

        // Other Transfers
        ABAN: 'Ownership Transfer or Change',
        BANK: 'Ownership Transfer or Change',
        COU: 'Ownership Transfer or Change',
        FORE: 'Ownership Transfer or Change',
        GENT: 'Ownership Transfer or Change',
        TRANS_LAND_TITLE: 'Ownership Transfer or Change',
        REIV: 'Ownership Transfer or Change',
        REPV: 'Ownership Transfer or Change',
        SZL: 'Ownership Transfer or Change',
        TAXS: 'Ownership Transfer or Change',
        VEST: 'Ownership Transfer or Change',

        // Exemptions
        residential_exemption: 'Residential Exemption',
        non_residential_exemption: 'Non-Residential Exemption',
      },
      feeDesc: {
        mhr_staff_correction: 'Staff Error or Omission',
        mhr_client_correction: 'Client Error or Omission',
        mhr_permit_default: 'Select Location Change Type',
        mhr_owner_default: 'Select Transfer Type',
        mhr_transport_permit: 'Transport Permit',
        mhr_transport_permit_extend: 'Extend Transport Permit',
        mhr_location_change: 'Registered Location Change',

        // Bill Of Sale Transfers
        TRANS: 'Transfer Due to Sale or Gift',
        TRANS_FAMILY_ACT: 'Transfer Due to Family Maintenance Act',
        TRANS_INFORMAL_SALE: 'Transfer with an Informal Bill of Sale',
        TRANS_QUIT_CLAIM: 'Transfer Due to Quit Claim',
        TRANS_SEVER_GRANT: 'Transfer Due to Severing Joint Tenancy',
        TRANS_RECEIVERSHIP: 'Transfer Due to Receivership',
        TRANS_WRIT_SEIZURE: 'Transfer Due to Writ of Seizure and Sale',

        // Transfers Due to Death
        TRAND: 'Transfer to Surviving Joint Tenant(s)',
        TRANS_AFFIDAVIT: 'Transfer to Executor - Estate under $25,000 with Will',
        TRANS_ADMIN: 'Transfer to Administrator - Grant of Administration',
        TRANS_WILL: 'Transfer to Executor - Grant of Probate with Will',

        // Other Transfers
        ABAN: 'Transfer Due to Abandonment and Sale',
        BANK: 'Transfer Due to Bankruptcy',
        COU: 'Transfer Due to Court Order',
        FORE: 'Transfer Due to Foreclosure Order',
        GENT: 'Transfer Due to General Transmission',
        TRANS_LAND_TITLE: 'Transfer Due to Land Title',
        REIV: 'Transfer Due to Repossession - Involuntary',
        REPV: 'Transfer Due to Repossession - Voluntary',
        SZL: 'Transfer Due to Seizure under Land Act',
        TAXS: 'Transfer Due to Tax Sale',
        VEST: 'Transfer Due to Vesting Order'
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
