import type { APISearchTypes, FilterTypes } from '@/enums'

//Defines the filter configuration for a table header.
export interface BaseHeaderFilterIF {
    // Display text for the filter (e.g., placeholder or label). 
    text: string
    // Type of filter (e.g., text, select, date).
    type: FilterTypes
}

export interface BaseHeaderIF {
    name?: string
    text?: string
    value: string|Array<string>
    class?: string
    sortable?: boolean
    width?: string
    fixed?: boolean
    display?: boolean
    subHeaders?: Array<string>
    filter?: BaseHeaderFilterIF
}
export interface TableHeadersIF {
    [APISearchTypes.AIRCRAFT]?: Array<BaseHeaderIF>
    [APISearchTypes.BUSINESS_DEBTOR]?: Array<BaseHeaderIF>
    [APISearchTypes.INDIVIDUAL_DEBTOR]?: Array<BaseHeaderIF>
    [APISearchTypes.MHR_NUMBER]?: Array<BaseHeaderIF>
    [APISearchTypes.REGISTRATION_NUMBER]?: Array<BaseHeaderIF>
    [APISearchTypes.SERIAL_NUMBER]?: Array<BaseHeaderIF>
}
