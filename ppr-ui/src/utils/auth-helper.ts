// Libraries
import { axios } from '@/utils/axios-auth'
import { StatusCodes } from 'http-status-codes'

import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'

// Interfaces, Enums
import {
  AccountProductCodes,
  AccountProductMemberships,
  AccountProductRoles,
  AccountTypes,
  ErrorCategories,
  ErrorCodes,
  ProductCode
} from '@/enums'
import {
  AccountProductSubscriptionIF, AddressIF, PartyIF, SearchPartyIF, UserProductSubscriptionIF
} from '@/interfaces'
import { partyCodeSearch } from '@/utils'
import { AccountInfoIF } from '@/interfaces/account-interfaces/account-info-interface'

/** Gets Keycloak JWT and parses it. */
function getJWT (): any {
  const token = sessionStorage.getItem(SessionStorageKeys.KeyCloakToken)
  if (token) {
    return parseToken(token)
  }
  throw new Error('Error getting Keycloak token')
}

/** Decodes and parses Keycloak token. */
function parseToken (token: string): any {
  try {
    const base64Url = token.split('.')[1]
    const base64 = decodeURIComponent(window.atob(base64Url).split('').map(function (c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    }).join(''))
    return JSON.parse(base64)
  } catch (err) {
    throw new Error('Error parsing Keycloak token - ' + err)
  }
}

/** Gets Keycloak roles from JWT. */
export function getKeycloakRoles (): Array<string> {
  const jwt = getJWT()
  const keycloakRoles = jwt.roles
  if (keycloakRoles && keycloakRoles.length > 0) {
    return keycloakRoles
  }
  throw new Error('Error getting Keycloak roles')
}

export async function getStaffRegisteringParty (isBcOnline: boolean): Promise<PartyIF> {
  let partyCode = sessionStorage.getItem('PPR_STAFF_PARTY_CODE')
  if (isBcOnline) {
    partyCode = sessionStorage.getItem('BCOL_STAFF_PARTY_CODE')
  }
  const response: [SearchPartyIF] = await partyCodeSearch(
    partyCode,
    true
  )
  if (response?.length > 0) {
    const party: PartyIF = {
      businessName: response[0].businessName,
      emailAddress: response[0].emailAddress,
      code: response[0].code,
      address: response[0].address
    }
    return party
  }
  throw new Error('Auth API error getting Registering Party: status code = ' + StatusCodes.NOT_FOUND.toString())
}

// Get Account Info from from auth api /api/v1/orgs/{org_id}
export async function getAccountInfoFromAuth (): Promise<AccountInfoIF> {
  const url = sessionStorage.getItem(SessionStorageKeys.AuthApiUrl)
  const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
  const accountId = JSON.parse(currentAccount)?.id

  const config = { baseURL: url, headers: { Accept: 'application/json' } }

  const accountInfo = await axios
    .get(`orgs/${accountId}`, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Unable to obtain Registering Party from Account Information.')
      }
      return {
        id: data.id,
        isBusinessAccount: data.isBusinessAccount,
        name: data.businessName || data.name,
        mailingAddress: data.mailingAddress as AddressIF
      }
    })
    .catch(error => {
      throw new Error(
        'Auth API error getting Account Info: status code = ' + error?.response?.status?.toString() ||
          StatusCodes.NOT_FOUND.toString()
      )
    })

  const accountAdminInfo = await axios
    .get(`orgs/${accountId}/members?membershipTypeCode=ADMIN&status=ACTIVE`, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Unable to get Admin details from Account Information.')
      }
      const adminInfo = data.members[0].user
      return {
        firstName: adminInfo.firstname,
        lastName: adminInfo.lastname,
        email: adminInfo.contacts[0].email,
        phone: adminInfo.contacts[0].phone,
        phoneExtension: adminInfo.contacts[0].phoneExtension
      }
    })
    .catch(error => {
      throw new Error(
        'Auth API error getting Account Admin details: status code = ' + error?.response?.status?.toString() ||
          StatusCodes.NOT_FOUND.toString()
      )
    })

  return {
    ...accountInfo,
    accountAdmin: accountAdminInfo
  } as AccountInfoIF
}

// Get registering party from auth api /api/v1/orgs/{org_id}
export async function getRegisteringPartyFromAuth (): Promise<PartyIF> {
  const url = sessionStorage.getItem('AUTH_API_URL')
  const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
  const accountInfo = JSON.parse(currentAccount)
  const accountId = accountInfo.id

  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.get(`orgs/${accountId}`, config)
    .then(
      response => {
        const data = response?.data
        if (!data) {
          throw new Error('Unable to obtain Registering Party from Account Information.')
        }
        // If no api address registering party validation should fail.
        const address: AddressIF = {
          street: data?.mailingAddress?.street || '',
          streetAdditional: data?.mailingAddress?.streetAdditional,
          city: data?.mailingAddress?.city || '',
          region: data?.mailingAddress?.region || '',
          postalCode: data?.mailingAddress?.postalCode || '',
          country: data?.mailingAddress?.country || '',
          deliveryInstructions: '' // Not used by PPR or returned by the api.
        }
        // Auth API account name is always business name.
        // No client party code or email is available via the auth api.
        const party: PartyIF = {
          businessName: data.businessName || data.name,
          emailAddress: '',
          code: '',
          address
        }
        return party
      }
    ).catch(
      error => {
        throw new Error('Auth API error getting Registering Party: status code = ' +
                        error?.response?.status?.toString() || StatusCodes?.NOT_FOUND.toString())
      }
    )
}

// Get SBC info from auth api /api/v1/orgs/{org_id}
export async function getSbcFromAuth (): Promise<boolean> {
  const url = sessionStorage.getItem('AUTH_API_URL')
  const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
  const accountInfo = JSON.parse(currentAccount)
  const accountId = accountInfo.id

  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.get(`orgs/${accountId}`, config)
    .then(
      response => {
        const data = response?.data
        if (!data) {
          return false
        }
        if (data.orgType === AccountTypes.SBC_STAFF) {
          return true
        }
        return false
      }
    ).catch(
      error => {
        throw new Error('Auth API error getting SBC: status code = ' +
                        error?.response?.status?.toString() || StatusCodes.NOT_FOUND.toString())
      }
    )
}

/**
 * Fetches product subscription authorizations from Auth API.
 */
export async function fetchAccountProducts (accountId: number): Promise<Array<UserProductSubscriptionIF>> {
  const config = {
    baseURL: sessionStorage.getItem(SessionStorageKeys.AuthApiUrl),
    headers: { Accept: 'application/json' }
  }

  return axios.get(`orgs/${accountId}/products`, config)
    .then(response => {
      const data = response?.data as Array<UserProductSubscriptionIF>
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      throw new Error('Error fetching account products, status code = ' +
        error?.response?.status?.toString() || StatusCodes.NOT_FOUND.toString())
    })
}

/**
 * Request auth product access
 * If requested type requires review, will create a Staff Task in Auth Web.
 *
 * @param productCode The specified auth product code
 */
export async function requestProductAccess (productCode: ProductCode): Promise<any> {
  const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
  const accountInfo = JSON.parse(currentAccount)
  const accountId = accountInfo.id

  const config = {
    baseURL: sessionStorage.getItem(SessionStorageKeys.AuthApiUrl),
    headers: { Accept: 'application/json' }
  }

  const payload = {
    subscriptions: [{
      productCode,
      externalSourceId: accountId.toString()
    }]
  }

  return axios.post(`orgs/${accountId}/products`, payload, config)
    .then(response => {
      const data: UserProductSubscriptionIF[] = response?.data as Array<UserProductSubscriptionIF>
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      return {
        error: {
          category: ErrorCategories.USER_ACCESS_PRODUCT_REQUEST,
          statusCode: error?.response?.status,
          message: error?.response?.data?.message,
          detail: error?.response?.data?.rootCause?.detail,
          type: error?.response?.data?.rootCause?.type?.trim() as ErrorCodes
        }
      }
    })
}

/**
 * Update auth product access
 * If requested type requires review, will create a Staff Task in Auth Web.
 *
 * @param productCode The specified auth product code to update
 */
export async function updateProductAccess (productCode: ProductCode): Promise<any> {
  const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
  const accountInfo = JSON.parse(currentAccount)
  const accountId = accountInfo.id

  const config = {
    baseURL: sessionStorage.getItem(SessionStorageKeys.AuthApiUrl),
    headers: { Accept: 'application/json' }
  }

  const payload = {
    subscriptions: [{
      productCode
    }]
  }

  return axios.patch(`orgs/${accountId}/products`, payload, config)
    .then(response => {
      const data: UserProductSubscriptionIF[] = response?.data as Array<UserProductSubscriptionIF>
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    })
    .catch(error => {
      throw new Error('Error requesting account product, status code = ' +
        error?.response?.status?.toString() || StatusCodes.NOT_FOUND.toString())
    })
}

// get product subscription authorizations
export async function getProductSubscription (
  productCode: AccountProductCodes.RPPR
): Promise<AccountProductSubscriptionIF> {
  const url = sessionStorage.getItem('AUTH_API_URL')
  const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
  const accountInfo = JSON.parse(currentAccount)
  const accountId = accountInfo.id

  const config = { baseURL: url, headers: { Accept: 'application/json' } }
  return axios.get(`accounts/${accountId}/products/${productCode}/authorizations`, config)
    .then(
      response => {
        const data = response?.data as { membership: AccountProductMemberships, roles: Array<AccountProductRoles> }
        if (!data) {
          throw new Error('Unable to obtain Account Product Subscription Information.')
        }
        return {
          [productCode]: {
            membership: data.membership,
            roles: data.roles
          }
        }
      }
    ).catch(
      error => {
        throw new Error('Auth API error getting Account Product Subscription: status code = ' +
                        error?.response?.status?.toString() || StatusCodes.NOT_FOUND.toString())
      }
    )
}
