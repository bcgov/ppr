import { MHRSearchTypes, SearchTypes } from '@/resources'

export const useSearch = () => {
  const isMHRSearchType = (type: string): boolean => {
    const mhi = MHRSearchTypes.findIndex(mh => mh.searchTypeAPI === type)
    return mhi >= 0
  }
  const isPPRSearchType = (type: string): boolean => {
    const sti = SearchTypes.findIndex(st => st.searchTypeAPI === type)
    return sti >= 0
  }

  return {
    isMHRSearchType,
    isPPRSearchType
  }
}
