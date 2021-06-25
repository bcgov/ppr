// Libraries
import { axios } from '@/utils/axios-auth'
import { StatusCodes } from 'http-status-codes'

import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'

// Interfaces
import { AddressIF, PartyIF } from '@/interfaces'

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
