/* eslint-disable no-useless-constructor */
// Libraries
import { axios } from '@/utils/axios-von'

// Interfaces
import { AutoCompleteResponseIF } from '@/interfaces'

const HttpStatus = require('http-status-codes')

export async function getAutoComplete (searchValue: string): Promise<any> {
  if (!searchValue) return
  const url = sessionStorage.getItem('VON_API_URL')
  const config = { baseURL: url }
  return axios.get<AutoCompleteResponseIF>(`search/autocomplete?q=${searchValue}`, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      return error
    })
}
