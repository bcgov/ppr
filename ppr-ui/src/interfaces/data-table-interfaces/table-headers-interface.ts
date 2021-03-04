import { APISearchTypes, UISearchTypes } from '@/enums'

interface BaseHeaderIF {
    text: string
    value: string
    class?: string
}
export interface TableHeadersIF {
    [APISearchTypes.AIRCRAFT]?: Array<BaseHeaderIF>
    [APISearchTypes.BUSINESS_DEBTOR]?: Array<BaseHeaderIF>
    [APISearchTypes.INDIVIDUAL_DEBTOR]?: Array<BaseHeaderIF>
    [APISearchTypes.MHR_NUMBER]?: Array<BaseHeaderIF>
    [APISearchTypes.REGISTRATION_NUMBER]?: Array<BaseHeaderIF>
    [APISearchTypes.SERIAL_NUMBER]?: Array<BaseHeaderIF>
}
