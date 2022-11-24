// Libraries
import { axios } from '@/utils/axios-ppr'
import { StatusCodes } from 'http-status-codes'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { StaffPaymentOptions } from '@bcrs-shared-components/enums'
import {
  ManufacturedHomeSearchResultIF,
  SearchResponseIF,
  MhrSearchCriteriaIF,
  MhRegistrationSummaryIF,
  ErrorIF,
  MhrTransferApiIF,
  MhrDraftTransferApiIF, DraftIF
} from '@/interfaces'
import { APIMhrTypes, ErrorCategories, ErrorCodes } from '@/enums'
import { useSearch } from '@/composables/useSearch'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
const { mapMhrSearchType } = useSearch()

// Create default request base URL and headers.
function getDefaultConfig (): Object {
  const url = sessionStorage.getItem('MHR_API_URL')
  return { baseURL: url, headers: { Accept: 'application/json' } }
}

// Submit an mhr search query request.
export async function mhrSearch (
  searchCriteria: MhrSearchCriteriaIF,
  extraParams: string
): Promise<any> {
  return axios
    .post<SearchResponseIF>(`searches${extraParams}`, searchCriteria, getDefaultConfig())
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }

      // Map query return type to differentiate between ppr & mhr in ui
      data.searchQuery.type = mapMhrSearchType(data.searchQuery.type, true)

      // need a unique value for the data table (can't use the index in the list)
      const results = data.results
      if (results) {
        results.forEach((item, index) => {
          item.id = index + 1
          item.selected = false
        })
        data.results = results
      }
      return data
    })
    .catch(error => {
      if (error?.response?.data) {
        try {
          error.response.data.rootCause = error.response.data.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"statusCode":"')
            .replaceAll(',', '",')
          error.response.data.rootCause = `{${error.response.data.rootCause}"}`
          error.response.data.rootCause = JSON.parse(error.response.data.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        searchId: 'error',
        maxResultsSize: 0,
        totalResultsSize: 0,
        returnedResultsSize: 0,
        searchQuery: searchCriteria, // Echoes request
        results: [],
        error: {
          category: ErrorCategories.SEARCH,
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          detail: error?.response?.data?.rootCause?.detail,
          type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes
        }
      }
    })
}

function mhrStaffPaymentParameters (staffPayment: StaffPaymentIF) {
  let paymentParams = ''
  // filled out staff payment parameters
  if (staffPayment) {
    switch (staffPayment.option) {
      case StaffPaymentOptions.FAS:
        paymentParams = paymentParams + 'routingSlipNumber=' + staffPayment.routingSlipNumber
        break
      case StaffPaymentOptions.BCOL:
        paymentParams = paymentParams + 'bcolAccountNumber=' + staffPayment.bcolAccountNumber
        paymentParams = paymentParams + '&datNumber=' + staffPayment.datNumber
        break
    }
    if (staffPayment.isPriority) {
      paymentParams = paymentParams + '&priority=true'
    }
  }
  return paymentParams
}

// Get registration summary information
export async function getMHRegistrationSummary (
  registrationNum: string,
  refreshing: boolean
): Promise<MhRegistrationSummaryIF> {
  return axios
    .get(`other-registrations/${registrationNum}`, getDefaultConfig())
    .then(response => {
      const data = response?.data as MhRegistrationSummaryIF

      if (!data) throw new Error('Invalid API response')
      if (!refreshing && data.inUserList) {
        data.error = {
          statusCode: StatusCodes.CONFLICT,
          message: 'Registration is already added to this account.'
        }
      }
      return data
    })
    .catch(error => {
      if (error?.response?.data) {
        try {
          error.response.data.rootCause = error.response.data.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"statusCode":"')
            .replaceAll(',', '",')
          error.response.data.rootCause = `{${error.response.data.rootCause}"}`
          error.response.data.rootCause = JSON.parse(error.response.data.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        clientReferenceId: '',
        createDateTime: '',
        mhrNumber: '',
        ownerNames: '',
        path: '',
        registrationDescription: '',
        statusType: '',
        submittingParty: '',
        username: '',
        error: {
          category: ErrorCategories.HISTORY_REGISTRATIONS,
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          detail: error?.response?.data?.rootCause?.detail,
          type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes
        }
      }
    })
}

// Add MHR to My Registrations
export async function addMHRegistrationSummary (registrationNum: string): Promise<MhRegistrationSummaryIF> {
  const url = sessionStorage.getItem('MHR_API_URL')

  const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
  if (!currentAccount) console.error('Error: current account expected, but not found.')
  const currentAccountId = JSON.parse(currentAccount)?.id

  const config = { baseURL: url, headers: { Accept: 'application/json', 'Account-Id': currentAccountId } }

  return axios
    .post(`other-registrations/${registrationNum}`, {}, config)
    .then(response => {
      const data = response?.data as MhRegistrationSummaryIF
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      if (error?.response?.data) {
        try {
          error.response.data.rootCause = error.response.data.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"statusCode":"')
            .replaceAll(',', '",')
          error.response.data.rootCause = `{${error.response.data.rootCause}"}`
          error.response.data.rootCause = JSON.parse(error.response.data.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        clientReferenceId: '',
        createDateTime: '',
        mhrNumber: '',
        ownerNames: '',
        path: '',
        registrationDescription: '',
        statusType: '',
        submittingParty: '',
        username: '',
        error: {
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          detail: error?.response?.data?.rootCause?.detail,
          type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes
        }
      }
    })
}

// Submit selected matches in mhr search results
export async function submitSelectedMhr (
  searchId: string,
  selected: Array<ManufacturedHomeSearchResultIF>,
  folioOrReferenceNumber: string = null,
  staffPayment: StaffPaymentIF = null,
  isCertified: boolean = false
): Promise<number> {
  let extraParams = ''

  if (staffPayment) {
    extraParams += '?'

    // do they want a certified search
    if (isCertified) {
      extraParams += 'certified=True'
    }

    const paymentParams = mhrStaffPaymentParameters(staffPayment)
    if (paymentParams.length > 0) {
      if (isCertified) extraParams += '&'
      extraParams += `${paymentParams}`
    }
  }

  if (selected.length >= 75) {
    if (!extraParams) {
      extraParams += '?'
    }
    if (extraParams.length > 1) {
      extraParams += '&'
    }
    extraParams += 'callbackURL=PPR_UI'
  }

  if (folioOrReferenceNumber) {
    extraParams ? extraParams += '&' : extraParams += '?'
    extraParams += 'clientReferenceId=' + folioOrReferenceNumber
  }

  return axios
    .post(`search-results/${searchId}${extraParams}`, selected, getDefaultConfig())
    .then(response => {
      return response.status
    })
    .catch(error => {
      return error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR
    })
}

// Get pdf for a previous search
export async function searchMhrPDF (searchId: string): Promise<any> {
  const url = sessionStorage.getItem('MHR_API_URL')
  const config = {
    baseURL: url,
    headers: { Accept: 'application/pdf' },
    responseType: 'blob' as 'json'
  }
  return axios
    .get(`search-results/${searchId}`, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        error: {
          category: ErrorCategories.REPORT_GENERATION,
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND
        }
      }
    })
}

export async function submitMhrRegistration (payloadData, queryParamData) {
  try {
    // assuming the queryParamData (staff payment) is always available because of validation
    const queryParamString = new URLSearchParams(queryParamData).toString()

    const result = await axios.post(`registrations?${queryParamString}`, payloadData, getDefaultConfig())
    if (!result?.data) {
      throw new Error('Invalid API response')
    }
    return result.data
  } catch (error) {
    return {
      error: {
        category: ErrorCategories.REGISTRATION_CREATE,
        statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
        msg: error?.response?.data?.errorMesage || 'Unknown Error'
      }
    }
  }
}

export async function mhrRegistrationHistory (withCollapse: boolean = false) {
  try {
    const path = withCollapse ? 'registrations?collapse=true' : 'registrations'
    const result = await axios.get(path, getDefaultConfig())
    if (!result?.data) {
      throw new Error('Invalid API response')
    }

    return result.data
  } catch (error) {
    return {
      error: {
        category: ErrorCategories.REGISTRATION_CREATE,
        statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
        msg: error?.response?.data?.errorMesage || 'Unknown Error'
      }
    }
  }
}

// Get pdf for a registration
export async function mhRegistrationPDF (pdfPath: string): Promise<any> {
  const url = sessionStorage.getItem('MHR_API_URL')
  pdfPath = pdfPath.replace('/mhr/api/v1', '')
  const config = {
    baseURL: url,
    headers: { Accept: 'application/pdf' },
    responseType: 'blob' as 'json'
  }
  return axios
    .get(pdfPath, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      if (error?.response?.data) {
        try {
          error.response.data.rootCause = error.response.data.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"statusCode":"')
            .replaceAll(',', '",')
          error.response.data.rootCause = `{${error.response.data.rootCause}"}`
          error.response.data.rootCause = JSON.parse(error.response.data.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        error: {
          category: ErrorCategories.REPORT_GENERATION,
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          detail: error?.response?.data?.rootCause?.detail,
          type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes
        }
      }
    })
}

// Request to validate Document exists and is unique
export async function validateDocumentID (documentId: string) {
  try {
    const result = await axios.get(`documents/verify/${documentId}`, getDefaultConfig())
    if (!result?.data) {
      throw new Error('Invalid API response')
    }

    return result.data
  } catch (error) {
    return {
      error: {
        category: ErrorCategories.DOCUMENT_ID,
        statusCode: error?.response?.status || StatusCodes.CONFLICT,
        msg: error?.response?.data?.errorMesage || 'Unknown Error'
      }
    }
  }
}

export async function submitMhrTransfer (payloadData, mhrNumber) {
  try {
    const result = await axios.post(`transfers/${mhrNumber}`, payloadData, getDefaultConfig())
    if (!result?.data) {
      throw new Error('Invalid API response')
    }
    return result.data
  } catch (error) {
    return {
      error: {
        category: ErrorCategories.REGISTRATION_TRANSFER,
        statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
        msg: error?.response?.data?.errorMesage || 'Unknown Error'
      }
    }
  }
}

export async function fetchMhRegistration (
  mhRegistrationNum: string
): Promise<any> {
  return axios
    .get(`registrations/${mhRegistrationNum}?current=true`, getDefaultConfig())
    .then(response => {
      return response
    })
    .catch(error => {
      if (error?.response?.data) {
        try {
          error.response.data.rootCause = error.response.data.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"statusCode":"')
            .replaceAll(',', '",')
          error.response.data.rootCause = `{${error.response.data.rootCause}"}`
          error.response.data.rootCause = JSON.parse(error.response.data.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        category: ErrorCategories.REGISTRATION_DELETE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.message,
        detail: error?.response?.data?.rootCause?.detail,
        type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes
      }
    })
}

export async function deleteMhRegistrationSummary (
  mhRegistrationNum: string
): Promise<ErrorIF> {
  return axios
    .delete(`other-registrations/${mhRegistrationNum}`, getDefaultConfig())
    .then(response => {
      return { statusCode: response?.status as StatusCodes }
    })
    .catch(error => {
      if (error?.response?.data) {
        try {
          error.response.data.rootCause = error.response.data.rootCause
            .replace('detail:', '"detail":"')
            .replace('type:', '"type":"')
            .replace('message:', '"message":"')
            .replace('status_code:', '"statusCode":"')
            .replaceAll(',', '",')
          error.response.data.rootCause = `{${error.response.data.rootCause}"}`
          error.response.data.rootCause = JSON.parse(error.response.data.rootCause)
        } catch (error) {
          // continue
        }
      }
      return {
        category: ErrorCategories.REGISTRATION_DELETE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.message,
        detail: error?.response?.data?.rootCause?.detail,
        type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes
      }
    })
}

// Draft Requests
// Save a new draft.
export async function createMhrTransferDraft (draft: MhrTransferApiIF): Promise<MhrTransferApiIF> {
  const payload: MhrDraftTransferApiIF = {
    type: APIMhrTypes.TRANSFER_OF_SALE,
    registration: draft
  }

  return axios
    .post('drafts', payload, getDefaultConfig())
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
}

// Update an existing draft.
export async function updateMhrDraft (draftId: string, draft: MhrTransferApiIF): Promise<MhrTransferApiIF> {
  if (!draftId) {
    draft.error = {
      category: ErrorCategories.REGISTRATION_SAVE,
      statusCode: StatusCodes.BAD_REQUEST,
      message: 'Draft lookup request invalid: no draft ID.'
    }
    return draft
  }
  const payload: MhrDraftTransferApiIF = {
    type: APIMhrTypes.TRANSFER_OF_SALE,
    registration: draft
  }

  return axios
    .put<MhrTransferApiIF>('drafts/' + draftId, payload, getDefaultConfig())
    .then(response => {
      const data: MhrTransferApiIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
}

// Get all existing drafts
export async function getMhrDrafts (): Promise<Array<MhrDraftTransferApiIF>> {
  return axios
    .get<Array<MhrDraftTransferApiIF>>('drafts', getDefaultConfig())
    .then(response => {
      const data: Array<MhrDraftTransferApiIF> = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
}

// Get an existing draft by id.
export async function getMhrTransferDraft (draftId: string): Promise<MhrDraftTransferApiIF> {
  const draft = {} as MhrDraftTransferApiIF
  if (!draftId) {
    draft.error = {
      category: ErrorCategories.DRAFT_LOAD,
      statusCode: StatusCodes.BAD_REQUEST,
      message: 'Draft lookup request invalid: no draft ID.'
    }
    return draft
  }
  return axios
    .get<MhrDraftTransferApiIF>('drafts/' + draftId, getDefaultConfig())
    .then(response => {
      const data: MhrDraftTransferApiIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
}

// Delete an existing draft (any type) by documentId.
export async function deleteMhrDraft (draftID: string): Promise<ErrorIF> {
  if (!draftID) return { statusCode: StatusCodes.BAD_REQUEST, message: 'No draft ID given.' }

  return axios
    .delete<void>(`drafts/${draftID}`, getDefaultConfig())
    .then(response => {
      return { statusCode: response?.status as StatusCodes }
    })
}
