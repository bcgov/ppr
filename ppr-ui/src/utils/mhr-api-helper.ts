// Libraries
import { axios } from '@/utils/axios-ppr'
import { StatusCodes } from 'http-status-codes'
import {
  ErrorDetailIF,
  ErrorIF,
  ExemptionIF,
  ManufacturedHomeSearchResultIF,
  MhrDraftApiIF,
  MhrDraftIF,
  MhRegistrationSummaryIF,
  MhrManufacturerInfoIF,
  MhrQsPayloadIF,
  MhrSearchCriteriaIF,
  RegistrationSortIF,
  SearchResponseIF,
  StaffPaymentIF,
  AdminRegistrationIF,
  MhrHistoryRoIF
} from '@/interfaces'
import { APIMhrTypes, ErrorCategories, ErrorCodes, ErrorRootCauses, StaffPaymentOptions } from '@/enums'
import { useSearch } from '@/composables/useSearch'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { addTimestampToDate } from '@/utils'
import { trim } from 'lodash'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import type { AxiosError } from 'axios'

const { mapMhrSearchType } = useSearch()

// Create default request base URL and headers.
function getDefaultConfig (): object {
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
): Promise<MhRegistrationSummaryIF|any> {
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
export async function addMHRegistrationSummary (registrationNum: string): Promise<MhRegistrationSummaryIF|any> {
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
    extraParams += extraParams ? '&' : '?'
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

export async function submitMhrRegistration (payloadData, staffPayment) {
  try {
    // assuming the staffPayment is always available because of validation
    const paymentParams = mhrStaffPaymentParameters(staffPayment)

    const result = await axios.post(`registrations?${paymentParams}`, payloadData, getDefaultConfig())
    if (!result?.data) {
      throw new Error('Invalid API response')
    }
    return result.data
  } catch (error: any) {
    return {
      error: {
        category: ErrorCategories.REGISTRATION_CREATE,
        statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
        msg: error?.response?.data?.errorMesage || 'Unknown Error',
        detail: error?.response?.data?.rootCause
      }
    }
  }
}
/**
 * Method to return Mhr registrations.
 *
 * @param withCollapse // Used to indicate whether api should return registrations collapsed
 * @returns MhRegistrationSummaryIF
 */
export async function mhrRegistrationHistory (withCollapse: boolean = false, sortOptions: RegistrationSortIF = null) {
  try {
    let path = withCollapse ? 'registrations?collapse=true' : 'registrations'
    if (sortOptions) {
      path = addSortParams(path, sortOptions)
    }

    const result = await axios.get(path, getDefaultConfig())
    if (!result?.data) {
      throw new Error('Invalid API response')
    }

    return result.data.map(item => ({ ...item, expand: false }))
  } catch (error: any) {
    return {
      error: {
        category: ErrorCategories.REGISTRATION_CREATE,
        statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
        msg: error?.response?.data?.errorMessage || 'Unknown Error'
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
  } catch (error: any) {
    return {
      error: {
        category: ErrorCategories.DOCUMENT_ID,
        statusCode: error?.response?.status || StatusCodes.CONFLICT,
        msg: error?.response?.data?.errorMesage || 'Unknown Error'
      }
    }
  }
}

export async function submitMhrTransfer (payloadData, mhrNumber, staffPayment) {
  const paymentParams = `?${mhrStaffPaymentParameters(staffPayment)}`
  try {
    const result = await axios.post(`transfers/${mhrNumber}${paymentParams}`, payloadData, getDefaultConfig())
    if (!result?.data) {
      throw new Error('Invalid API response')
    }
    return result.data
  } catch (error: any) {
    return {
      error: {
        category: new RegExp(ErrorRootCauses.OUT_OF_DATE_OWNERS).test(error?.response?.data?.rootCause)
          ? ErrorCategories.TRANSFER_OUT_OF_DATE_OWNERS
          : ErrorCategories.REGISTRATION_TRANSFER,
        statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
        msg: error?.response?.data?.errorMesage || 'Unknown Error',
        detail: error?.response?.data?.rootCause
      }
    }
  }
}

// Register a Unit Note on an existing manufactured home.
export async function submitAdminRegistration (
  mhrNumber: string,
  payloadData: AdminRegistrationIF,
  staffPayment: StaffPaymentIF
): Promise<any> {
  try {
    const paymentParams = mhrStaffPaymentParameters(staffPayment)
    const result = await axios.post(
      `admin-registrations/${mhrNumber}?${paymentParams}`,
      payloadData,
      getDefaultConfig()
    )
    if (!result?.data) {
      throw new Error('Invalid API response')
    }
    return result.data
  } catch (error: any) {
    return {
      error: {
        category: new RegExp(ErrorRootCauses.OUT_OF_DATE_DRAFT).test(error?.response?.data?.rootCause)
          ? ErrorCategories.DRAFT_OUT_OF_DATE
          : ErrorCategories.ADMIN_REGISTRATION,
        statusCode: error?.response?.status || StatusCodes.BAD_REQUEST,
        message: error?.response?.data?.message || error?.errorMessage,
        detail: error?.response?.data?.rootCause?.detail || error?.rootCause,
        type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes || ErrorCodes.SERVICE_UNAVAILABLE
      } as ErrorIF
    }
  }
}

// Register a Unit Note on an existing manufactured home.
export async function submitMhrUnitNote (mhrNumber, payloadData, isAdminRegistration, staffPayment) {
  try {
    const paymentParams = mhrStaffPaymentParameters(staffPayment)
    // different Unit Notes are submitted to different endpoints
    const endpoint = isAdminRegistration ? `admin-registrations/${mhrNumber}` : `notes/${mhrNumber}`
    const result = await axios.post(`${endpoint}?${paymentParams}`, payloadData, getDefaultConfig())
    if (!result?.data) {
      throw new Error('Invalid API response')
    }
    return result.data
  } catch (error: any) {
    return {
      error: {
        category: ErrorCategories.MHR_UNIT_NOTE_FILING,
        statusCode: error?.response?.status || StatusCodes.BAD_REQUEST,
        message: error?.response?.data?.message || error?.errorMessage,
        detail: error?.response?.data?.rootCause?.detail || error?.rootCause,
        type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes || ErrorCodes.SERVICE_UNAVAILABLE
      } as ErrorIF
    }
  }
}

// File a Transport Permit
export async function submitMhrTransportPermit (mhrNumber, payloadData, staffPayment) {
  try {
    const paymentParams = mhrStaffPaymentParameters(staffPayment)
    const endpoint = `permits/${mhrNumber}`

    const result = await axios.post(`${endpoint}?${paymentParams}`, payloadData, getDefaultConfig())
    if (!result?.data) {
      throw new Error('Invalid API response')
    }
    return result.data
  } catch (error: any) {
    return {
      error: {
        category: ErrorCategories.TRANSPORT_PERMIT_FILING,
        statusCode: error?.response?.status || StatusCodes.BAD_REQUEST,
        message: error?.response?.data?.message || error?.errorMessage,
        detail: error?.response?.data?.rootCause?.detail || error?.rootCause,
        type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes || ErrorCodes.SERVICE_UNAVAILABLE
      } as ErrorIF
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
export async function createMhrDraft (type: APIMhrTypes, draft: any): Promise<MhrDraftIF> {
  const payload = {
    type,
    registration: draft
  }

  return axios
    .post<MhrDraftIF>('drafts', payload, getDefaultConfig())
    .then(response => {
      const data: MhrDraftIF = response?.data
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
      draft.error = {
        category: new RegExp(ErrorRootCauses.OUT_OF_DATE_DRAFT).test(error?.response?.data?.rootCause)
          ? ErrorCategories.DRAFT_OUT_OF_DATE
          : ErrorCategories.REGISTRATION_SAVE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.message,
        detail: error?.response?.data?.rootCause?.detail,
        type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes
      }
      return draft
    })
}

// Update an existing draft.
export async function updateMhrDraft (draftId: string, type: APIMhrTypes, draft: any): Promise<MhrDraftIF> {
  if (!draftId) {
    draft.error = {
      category: ErrorCategories.REGISTRATION_SAVE,
      statusCode: StatusCodes.BAD_REQUEST,
      message: 'Draft lookup request invalid: no draft ID.'
    }
    return draft
  }
  const payload = {
    type,
    draftNumber: draftId,
    registration: draft
  }

  return axios
    .put<MhrDraftIF>('drafts/' + draftId, payload, getDefaultConfig())
    .then(response => {
      const data: MhrDraftIF = response?.data
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
      draft.error = {
        category: new RegExp(ErrorRootCauses.OUT_OF_DATE_DRAFT).test(error?.response?.data?.rootCause)
          ? ErrorCategories.DRAFT_OUT_OF_DATE
          : ErrorCategories.REGISTRATION_SAVE,
        statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
        message: error?.response?.data?.message,
        detail: error?.response?.data?.rootCause?.detail,
        type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes
      }
      return draft
    })
}

// Get all existing drafts
export async function getMhrDrafts (sortOptions?): Promise<Array<MhrDraftIF>|any> {
  let path = 'drafts'
  if (sortOptions) {
    path = addSortParams(
      path + '?',
      sortOptions)
  }
  return axios
    .get<Array<MhrDraftIF>>(path, getDefaultConfig())
    .then(response => {
      const data: Array<MhrDraftIF> = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(() => {
      // Continue
    })
}

// Get an existing draft by id.
export async function getMhrDraft (draftId: string): Promise<MhrDraftApiIF|any> {
  const draft = {} as MhrDraftApiIF
  if (!draftId) {
    draft.error = {
      category: ErrorCategories.DRAFT_LOAD,
      statusCode: StatusCodes.BAD_REQUEST,
      message: 'Draft lookup request invalid: no draft ID.'
    }
    return draft
  }
  return axios
    .get<MhrDraftApiIF>('drafts/' + draftId, getDefaultConfig())
    .then(response => {
      const data: MhrDraftApiIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(() => {
      // Continue
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

// UX util function to delay any actions for defined number of milliseconds
export function delayActions (milliseconds: number): Promise<any> {
  return new Promise(resolve => setTimeout(resolve, milliseconds))
}

// Delete empty properties and objects and used to cleanup payload before API submission
export function deleteEmptyProperties (obj) {
  for (const key in obj) {
    if (typeof obj[key] === 'object') {
      deleteEmptyProperties(obj[key]) // recursively process nested objects
      if (Object.keys(obj[key] || {}).length === 0) {
        delete obj[key] // delete empty nested object
      }
    } else if (obj[key] === null || obj[key] === undefined || trim(obj[key]) === '') {
      delete obj[key] // delete empty property value
    }
  }
}

const UIFilterToApiFilter = {
  endDate: 'endDateTime',
  folNum: 'clientReferenceId',
  orderBy: 'sortCriteriaName',
  orderVal: 'sortDirection',
  regBy: 'username',
  regNum: 'mhrNumber',
  regType: 'registrationType',
  startDate: 'startDateTime',
  status: 'statusType',
  regParty: 'submittingName'
}

// add sorting params for registration history/draft api calls
function addSortParams (url: string, sortOptions: RegistrationSortIF): string {
  const sortKeys = Object.keys(sortOptions)
  // add all set filters as params to the call
  for (const i in sortKeys) {
    if (sortOptions[sortKeys[i]] === 'registeringParty') sortOptions[sortKeys[i]] = 'submittingName'
    if (sortOptions[sortKeys[i]] === 'ownerNames') sortOptions[sortKeys[i]] = 'ownerName'
    if (sortOptions[sortKeys[i]] === 'registrationDescription') sortOptions[sortKeys[i]] = 'registrationType'
    if (sortOptions[sortKeys[i]] === 'registeringName') sortOptions[sortKeys[i]] = 'username'
    // add timestamp onto datetime param values
    if (sortOptions[sortKeys[i]] && ['startDateTime', 'endDateTime'].includes(UIFilterToApiFilter[sortKeys[i]])) {
      sortOptions[sortKeys[i]] =
      addTimestampToDate(sortOptions[sortKeys[i]], sortOptions[sortKeys[i]] === 'endDateTime')
    }
    if (sortOptions[sortKeys[i]]) {
      url += `&${UIFilterToApiFilter[sortKeys[i]]}=${sortOptions[sortKeys[i]]}`
    }
  }
  return url
}

// Get the manufacturer information for a manufacturer MHR
export async function getMhrManufacturerInfo (): Promise<MhrManufacturerInfoIF> {
  try {
    const response = await axios.get<MhrManufacturerInfoIF>('manufacturers', getDefaultConfig())
    const data: MhrManufacturerInfoIF = response?.data
    if (!data) {
      throw new Error('Invalid API response')
    }
    return data
  } catch (error: AxiosError | any) {
    if (error.response && error.response.status === 404) {
      console.error('Resource not found:', error.message)
      // Handle 404 gracefully, returning null
      return null
    } else {
      // Handle other errors differently if needed
      console.error('API Error:', error.message)
      throw error
    }
  }
}

/**
 * Creates a new manufacturer.
 * @returns {Promise<MhrManufacturerInfoIF>} - A Promise that resolves with the created manufacturer information.
 * @throws {Error} - If an invalid API response is received.
 */
export async function createManufacturer (payload: MhrManufacturerInfoIF): Promise<MhrManufacturerInfoIF> {
  return axios
    .post<MhrManufacturerInfoIF>('manufacturers', payload, getDefaultConfig())
    .then(response => {
      const data: MhrManufacturerInfoIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
}

/**
 * Updates an existing manufacturer.
 * @returns {Promise<MhrManufacturerInfoIF>} - A Promise that resolves with the updating manufacturer information.
 * @throws {Error} - If an invalid API response is received.
 */
export async function updateManufacturer (payload: MhrManufacturerInfoIF): Promise<MhrManufacturerInfoIF> {
  return axios
    .put<MhrManufacturerInfoIF>('manufacturers', payload, getDefaultConfig())
    .then(response => {
      const data: MhrManufacturerInfoIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
}

/** Request Qualified Supplier record in MHR */
export async function getQualifiedSupplier (): Promise<MhrQsPayloadIF> {
  try {
    const response = await axios.get<MhrQsPayloadIF>('qualified-suppliers', getDefaultConfig())
    const data: MhrQsPayloadIF = response?.data
    if (!data) {
      throw new Error('Invalid API response')
    }
    return data
  } catch (error: AxiosError | any) {
    if (error.response && error.response.status === 404) {
      console.error('Resource not found:', error.message)
      // Handle 404 gracefully, returning null
      return null
    } else {
      // Handle other errors differently if needed
      console.error('API Error:', error.message)
      throw error
    }
  }
}

/**
 * Request creation of a Qualified Supplier in MHR
 * @param payload The request payload containing the qualified supplier application information
 */
export async function createQualifiedSupplier (payload: MhrQsPayloadIF): Promise<MhrQsPayloadIF> {
  return axios
    .post<MhrQsPayloadIF>('qualified-suppliers', payload, getDefaultConfig())
    .then(response => {
      const data: MhrQsPayloadIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
}

/**
 * Request update or creation of a Qualified Supplier in MHR
 * @param payload The request payload containing the qualified supplier application information
 */
export async function updateQualifiedSupplier (payload: MhrQsPayloadIF): Promise<MhrQsPayloadIF> {
  return axios
    .put<MhrQsPayloadIF>('qualified-suppliers', payload, getDefaultConfig())
    .then(response => {
      const data: MhrQsPayloadIF = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
}

/** Get pdf for a Qualified Supplier Service Agreement **/
export async function getQsServiceAgreements (): Promise<any> {
  const url = sessionStorage.getItem('MHR_API_URL')
  const config = {
    baseURL: url,
    headers: { Accept: 'application/pdf' },
    responseType: 'blob' as 'json'
  }
  return axios
    .get('service-agreements/latest', config)
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

/**
 * Submit Exemption filing request
 * @param payload The request payload containing the exemption information
 * @param mhrNumber The specified Mhr number
 * @param staffPayment The staff payment data
 */
// Function Definition
export async function createExemption (
  payload: ExemptionIF,
  mhrNumber: string,
  staffPayment: StaffPaymentIF
): Promise<ExemptionIF | ErrorDetailIF> {
  try {
    const paymentParams = `?${mhrStaffPaymentParameters(staffPayment)}`

    const response = await axios.post<ExemptionIF>(
      `exemptions/${mhrNumber}${paymentParams}`,
      payload,
      getDefaultConfig()
    )

    // Ensure response data exists
    if (!response.data) {
      throw new Error('Invalid API response')
    }

    // Return exemption data
    return response.data
  } catch (error: AxiosError | any) {
    // If an error occurs, return an ErrorIF object
    return {
      error: {
        category: ErrorCategories.EXEMPTION_SAVE,
        statusCode: error?.response?.status || StatusCodes.NOT_FOUND
      }
    }
  }
}

/**
 * Fetches the MHR (Manufactured Home Registry) history for a given MHR number.
 *
 * @param {string} mhrNumber - The MHR number to fetch history for.
 * @returns {Promise<MhrHistoryRoIF>} - A promise that resolves to the MHR history data.
 *
 * @throws Will throw an error if the API response is invalid or if any non-404 errors occur.
 *         In case of a 404 error, logs the error and returns null.
 */
export async function getMhrHistory (mhrNumber: string): Promise<MhrHistoryRoIF> {
  try {
    const response = await axios.get<MhrHistoryRoIF>(`registrations/history/${mhrNumber}`, getDefaultConfig())
    const data: MhrHistoryRoIF = response?.data
    if (!data) {
      throw new Error('Invalid API response')
    }
    return data
  } catch (error: AxiosError | any) {
    if (error.response && error.response.status === 404) {
      console.error('Resource not found:', error.message)
      // Handle 404 gracefully, returning null
      return null
    } else {
      // Handle other errors differently if needed
      console.error('API Error:', error.message)
      throw error
    }
  }
}
