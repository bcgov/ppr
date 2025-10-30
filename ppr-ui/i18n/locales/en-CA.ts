export default {
  ConnectHeader: {
    title: 'BC Registries and Online Services'
  },
  ConnectFeeWidget: {
    feeSummary: {
      title: 'Fee Summary',
      total: 'Total Fees',
      noFee: 'No Fee',
      priorityFees: 'Priority Fees',
      futureEffectiveFees: 'Future Effective Fees',
      serviceFees: 'Service Fee',
      processingFees: 'Staff Processing Fee',
      certifiedSearch: 'Certified Search',
      itemLabels: {
        PLACEHOLDER: '-',
        TEST: 'This is test entry',
        undefined: '-',
        // PPR Filing Types
        new: 'New Registration',
        amend: 'Registration Amendment',
        renew: 'Registration Renewal',
        discharge: 'Total Discharge',
        SA: 'Security Agreement',
        SE: 'Securities Order or Proceeding',
        RL: 'Repairers Lien',
        CL: 'Commercial Lien',
        FR: 'Marriage / Separation Agreement affecting Manufactured Home under Family Law Act',
        SG: 'Possession under S.30 of the Sale of Goods Act',
        LT: 'Land Tax Deferment Lien on a Manufactured Home',
        MH: 'Tax Lien under S.27/28 of the Manufactured Home Act',
        FL: 'Forestry - Contractor Lien',
        FA: 'Forestry - Contractor Charge',
        FS: 'Forestry - Sub-contractor Charge',
        CT: 'Crown Charge - Carbon Tax Act',
        ET: 'Crown Charge - Excise Tax Act',
        FO: 'Crown Charge - Forest Act',
        IT: 'Crown Charge - Income Tax Act',
        IP: 'Crown Charge - Insurance Premium Tax Act',
        LO: 'Crown Charge - Logging Tax Act',
        MD: 'Crown Charge - Mineral Land Tax Act',
        FT: 'Crown Charge - Motor Fuel Tax Act',
        PG: 'Crown Charge - Petroleum and Natural Gas Act',
        PT: 'Crown Charge - Property Transfer Tax Act',
        PS: 'Crown Charge - Provincial Sales Tax Act',
        RA: 'Crown Charge - Taxation (Rural Area) Act',
        SC: 'Crown Charge - School Act',
        SV: 'Crown Charge - Speculation and Vacancy Tax Act',
        TO: 'Crown Charge - Tobacco Tax Act',
        OT: 'Crown Charge - Other',
        WL: 'Lien for Unpaid Wages',
        HN: 'Heritage Conservation Notice',
        MN: 'Manufactured Home Notice',
        MHR: 'Manufactured Home Registration',
        ML: 'Maintenance Lien',
        PN: 'Proceeds of Crime Notice',
        MR: 'Mineral Resource Tax Act',
        MI: 'Mining Tax Act',
        CC: 'Corporation Capital Tax Act',
        DP: 'Consumption, Transition Tax Act',
        HR: 'Hotel Room Tax Act',
        SS: 'Social Service Tax Act',
        TA: 'Security Agreement Transition',
        TF: 'PPSA Transition',
        TG: 'Sales of Goods Transition',
        TL: 'Tax Lien Transition Social Service/Hotel Room',
        TM: 'M.H. Transition',
        TRANS: 'Sale or Gift',
        TRAND: 'Sale or Gift due to death',
        EXEMPTION_NON_RES: 'Non-Residential Exemption',
        EXEMPTION_RES: 'Residential Exemption',
        PERMIT: 'Transport Permit',
        CANCEL_PERMIT: 'Transport Permit',
        STAT: 'Registered Location Change',
        REGC_STAFF: 'Staff Error or Omission',
        REGC_CLIENT: 'Client Error or Omission',
        PUBA: 'Public Amendment',
        EXRE: 'Re-Register Manufactured Home',
        SA_GOV: 'Security Agreement',
        TA_GOV: 'Security Agreement Transition',
        TM_GOV: 'M.H. Transition',
        SA_TAX: 'Security Agreement',
        TA_TAX: 'Security Agreement Transition',
        TM_TAX: 'M.H. Transition',

        // MHR Filing Types
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

        // Party Code
        party_code: 'Create Party Code(s)'
      },
      feeDesc: {
        // PPR Filing Types
        new: 'Select registration length',
        mhr_transfer: 'Select transfer type',

        // MHR Filing Types
        mhr_staff_correction: 'Staff Error or Omission',
        mhr_client_correction: 'Client Error or Omission',
        mhr_permit_default: 'Select location change type',
        mhr_owner_default: 'Select transfer type',
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
