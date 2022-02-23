// Libraries
import { axios } from '@/utils/axios-auth'
import { StatusCodes } from 'http-status-codes'

import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'

// Interfaces, Enums
import { AccountProductCodes, AccountProductMemberships, AccountProductRoles } from '@/enums'
import { AccountProductSubscriptionIF, AddressIF, PartyIF, SearchPartyIF } from '@/interfaces'
import { partyCodeSearch } from '@/utils'

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

export async function getStaffegisteringParty (isBcOnline: boolean): Promise<PartyIF> {
  let partyCode = sessionStorage.getItem(SessionStorageKeys.PprStaffPartyCode)
  if (isBcOnline) {
    partyCode = sessionStorage.getItem(SessionStorageKeys.BcolStaffPartyCode)
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
          address: address
        }
        return party
      }
    ).catch(
      error => {
        throw new Error('Auth API error getting Registering Party: status code = ' +
                        error?.response?.status?.toString() || StatusCodes.NOT_FOUND.toString())
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
        const branchName = data?.branchName
        if (branchName?.includes('Service BC')) {
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
