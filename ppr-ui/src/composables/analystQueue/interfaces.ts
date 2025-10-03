import type { OwnerIF, DocumentSummaryList, SubmittingPartyIF } from "@/interfaces"
import type { ReviewRegTypes, ReviewStatusTypes } from "@/composables/analystQueue/enums"

export interface QueueSummaryIF {
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

export interface DateRangeFilterIF {
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

export interface QueueReviewStepIF {
    changeNote: string
    clientNote: string
    createDateTime: string
    staffNote: string
    statusType: ReviewStatusTypes
    username: string
}

export interface QueueOwnerGroupIF {
    groupId: number
    owners: OwnerIF[]
}

export interface QueuePaymentIF {
    invoiceId: string
    priority: boolean
    receipt: string
}
export interface QueueDetailIF {
    accountId?: string
    addOwnerGroups?: QueueOwnerGroupIF[]
    affirmByName?: string
    assigneeName?: string
    clientReferenceId?: string
    consideration?: string
    deathOfOwner?: boolean
    declaredValue?: number
    deleteOwnerGroups?: QueueOwnerGroupIF[]
    documentId?: string
    documents?: DocumentSummaryList
    mhrNumber?: string
    ownLand?: boolean
    payment?: QueuePaymentIF
    registrationType?: ReviewRegTypes
    reviewPending?: boolean
    reviewSteps?: QueueReviewStepIF[]
    status?: ReviewStatusTypes
    submittingParty?: SubmittingPartyIF
    transferDate?: string
    usergroup?: string
    username?: string
}
