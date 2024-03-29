// Interface describing sub-product selector tool configuration
export interface SubProductConfigIF {
    type: string
    label: string
    productBullets: Array<string>
    hasImportantBullet?: boolean
    note?: string
}
