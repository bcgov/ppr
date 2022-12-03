export interface TitleSummaryIF {
  firstOwner: string
  landTitleDistrict: string
  landTitleDistrictCode: string
  parcelIdentifier: string
  status: string
  titleNumber: string
  error?: any
}

export interface TitleSummariesIF {
 titleSummaries: Array<TitleSummaryIF>
}

export interface LtsaDetailsIF {
  orderId: string
  legalDescription: string
  lot: string
  parcel: string
  block: string
  districtLot: string
  partOf: string
  section: string
  township: string
  range: string
  meridian: string
  landDistrict: string
  plan: string
}

export interface PidInfoIF {
  pidNumber: string
  legalDescription: string
}
