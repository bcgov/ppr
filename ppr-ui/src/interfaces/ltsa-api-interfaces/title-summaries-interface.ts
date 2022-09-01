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
