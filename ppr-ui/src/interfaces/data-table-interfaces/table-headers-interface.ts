import type { APISearchTypes } from '@/enums'

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
}
export interface TableHeadersIF {
    [APISearchTypes.AIRCRAFT]?: Array<BaseHeaderIF>
    [APISearchTypes.BUSINESS_DEBTOR]?: Array<BaseHeaderIF>
    [APISearchTypes.INDIVIDUAL_DEBTOR]?: Array<BaseHeaderIF>
    [APISearchTypes.MHR_NUMBER]?: Array<BaseHeaderIF>
    [APISearchTypes.REGISTRATION_NUMBER]?: Array<BaseHeaderIF>
    [APISearchTypes.SERIAL_NUMBER]?: Array<BaseHeaderIF>
}
