import type { ReviewRegTypes, ReviewStatusTypes } from "@/composables/analystQueue/enums"

export interface ReviewIF {
    reviewId: string
    mhrNumber: string
    documentId: string
    priority: boolean
    registrationDescription: string
    registrationType: ReviewRegTypes
    statusType: ReviewStatusTypes
    createDateTime: string
    submittingName: string
    assigneeName: string
}

export interface DateRangeFilter {
    start: {
        year: number
        month: number
        day: number
    }
    end: {
        year: number
        month: number
        day: number
    }
}