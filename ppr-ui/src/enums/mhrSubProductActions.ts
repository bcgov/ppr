export enum MhrSubTypes {
    GENERAL_PUBLIC = 'General Public',
    QUALIFIED_SUPPLIER = 'Qualified Supplier',
    LAWYERS_NOTARIES = 'Lawyers and Notaries',
    MANUFACTURER = 'Home Manufacturers',
    DEALERS = 'Home Dealers'
}

export enum MhrActions {
    MHR_SEARCH = 'Searches for manufactured homes and for liens on a home',
    TRANSPORT_PERMITS = 'Transport permits',
    TRANSPORT_PERMITS_NO_CERT = 'Transport permits (where no tax certificate is required)',
    TRANSFER_TRANSACTIONS = 'Transfer due to sale or gift',
    TRANSFER_TRANSACTIONS_SJT = 'Transfer to surviving joint tenant(s)',
    HOME_TRANSFER_TRANSACTIONS = 'Transfer transactions (related to homes manufacturers currently own)',
    RESIDENTIAL_EXEMPTIONS = 'Residential exemptions',
    REGISTRATIONS = 'Registrations',
    APPLICATION_REQUIRED = 'Application process required'
}
