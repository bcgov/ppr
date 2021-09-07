import { ExistingRegFeeSummaryTypes, NewRegFeeSummaryTypes } from "@/enums/feeSummaryTypes";
import { feeDefault10, feeDefault5, feeDefaultNoFee, feeSelect5 } from "./feeSummaries";

export const fees = {
  [NewRegFeeSummaryTypes.DEFAULT_180]: {
    feeSummary: feeDefault5,
    hint: "180 Day Registration (default)"
  },
  [NewRegFeeSummaryTypes.DEFAULT_INFINITE_0]: {
    feeSummary: feeDefaultNoFee,
    hint: "Infinite Registration (default)"
  },
  [NewRegFeeSummaryTypes.DEFAULT_INFINITE_10]: {
    feeSummary: feeDefault10,
    hint: "Infinite Registration (default)"
  },
  [NewRegFeeSummaryTypes.SELECT_YEARS_OR_INFINITE]: {
    feeSummary: feeSelect5,
    hint: "" // calculated based on selection
  },
  [ExistingRegFeeSummaryTypes.DISCHARGE]: {
    feeSummary: feeDefaultNoFee,
    hint: ""
  }
}