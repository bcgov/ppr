import { useTableFeatures } from '@/composables'

describe('useTableFeatures', () => {
  let composable
  const mockBaseObject = [
    { id: 1, dateProperty: '2023-05-15T16:30:46+00:00' },
    { id: 2, dateProperty: '2022-08-10T08:15:30+00:00' },
    { id: 3, dateProperty: '2024-01-20T12:45:00+00:00' },
    { id: 4, dateProperty: '2023-02-05T19:00:15+00:00' }
  ]
  const mockSortedAsc = [
    { id: 2, dateProperty: '2022-08-10T08:15:30+00:00' },
    { id: 4, dateProperty: '2023-02-05T19:00:15+00:00' },
    { id: 1, dateProperty: '2023-05-15T16:30:46+00:00' },
    { id: 3, dateProperty: '2024-01-20T12:45:00+00:00' }
  ]
  const mockSortedDesc = [
    { id: 3, dateProperty: '2024-01-20T12:45:00+00:00' },
    { id: 1, dateProperty: '2023-05-15T16:30:46+00:00' },
    { id: 4, dateProperty: '2023-02-05T19:00:15+00:00' },
    { id: 2, dateProperty: '2022-08-10T08:15:30+00:00' }
  ]

  beforeEach(() => {
    composable = useTableFeatures()
  })

  it('should sort objects by date in ascending order', () => {
    composable.sortDates(mockBaseObject, 'dateProperty')

    expect(mockBaseObject).toEqual(mockSortedAsc)
  })

  it('should sort objects by date in descending order', async () => {
    composable.sortDates(mockBaseObject, 'dateProperty', true)

    expect(mockBaseObject).toEqual(mockSortedDesc)
  })

  // Add more test cases as needed when more custom features are implemented..
})
