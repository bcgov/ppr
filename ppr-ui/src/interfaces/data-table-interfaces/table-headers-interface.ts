import { APISearchTypes, UISearchTypes } from '@/enums'

interface BaseHeaderIF {
    text: string
    value: string
    class?: string
}
export interface TableHeadersIF {
    [UISearchTypes.AIRCRAFT]?: Array<BaseHeaderIF>
    [UISearchTypes.BUSINESS_DEBTOR]?: Array<BaseHeaderIF>
    [UISearchTypes.INDIVIDUAL_DEBTOR]?: Array<BaseHeaderIF>
    [UISearchTypes.MHR_NUMBER]?: Array<BaseHeaderIF>
    [UISearchTypes.REGISTRATION_NUMBER]?: Array<BaseHeaderIF>
    [APISearchTypes.SERIAL_NUMBER]?: Array<BaseHeaderIF>
}
