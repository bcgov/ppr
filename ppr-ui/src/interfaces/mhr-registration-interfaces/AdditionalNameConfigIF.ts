export interface AdditionalNameConfigIF {
  label: string
  hint: string
  isRequired: boolean
  tooltipContent: {
    [key: string]: string
    default?: string
  }
}

export interface AdditionalNameConfigsIF {
  [key: string]: AdditionalNameConfigIF
}
