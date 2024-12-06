import { describe, it, expect, beforeEach } from 'vitest'
import { SimpleTable } from '@/components/common'
import { createComponent } from './utils'
import { shortPacificDate } from '@/utils'
import { nextTick } from 'vue'

const tableHeadersMock = [
  { name: 'Header 1', class: 'header-class-1', value: 'name' },
  { name: 'Header 2', class: 'header-class-2', value: 'name' },
  { name: 'Header 3', class: 'header-class-3', value: 'dateField' },
  { name: 'Header 4', class: 'header-class-4', value: 'sections[0].serialNumber' },
  { name: 'Header 5', class: 'header-class-5', value: ['baseInformation.make', 'baseInformation.model'] }
]

const tableDataMock = [
  {
    name: 'Row 1',
    dateField: '2024-01-01T00:00:00Z',
    sections: [{ serialNumber: '12345' }],
    baseInformation: { make: 'Make1', model: 'Model1' }
  },
  {
    name: 'Row 2',
    dateField: '2023-12-25T00:00:00Z',
    sections: [{ serialNumber: '67890' }],
    baseInformation: { make: 'Make2', model: 'Model2' }
  }
]

describe('SimpleTable.vue', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(SimpleTable, {
      tableHeaders: tableHeadersMock,
      tableData: tableDataMock,
    })
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('#simple-table').exists()).toBe(true)
    expect(wrapper.findAll('thead th').length).toBe(tableHeadersMock.length)
    expect(wrapper.findAll('tbody tr').length).toBe(tableDataMock.length)
  })

  it('renders table headers correctly', () => {
    const headers = wrapper.findAll('thead th')
    expect(headers.length).toBe(tableHeadersMock.length)
    headers.forEach((header, index) => {
      expect(header.text()).toBe(tableHeadersMock[index].name)
      expect(header.classes()).toContain(tableHeadersMock[index].class)
    })
  })

  it('renders table data correctly', () => {
    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(tableDataMock.length) // considering expanded row
    rows.forEach((row, index) => {
      if (index % 2 === 0) {
        const dataIndex = index / 2
        const cells = row.findAll('td')
        expect(cells.at(1).text()).toBe(tableDataMock[dataIndex].name)
        expect(cells.at(2).text()).toBe(shortPacificDate(tableDataMock[dataIndex].dateField))
        expect(cells.at(3).text()).toBe(tableDataMock[dataIndex].sections[0].serialNumber)
        expect(cells.at(4).text()).toBe(`${tableDataMock[dataIndex].baseInformation.make} ${tableDataMock[dataIndex].baseInformation.model}`)
      }
    })
  })

  it('toggles row expansion correctly', async () => {
    const toggleBtn = await wrapper.findAll('.toggle-expand-row-btn')
    toggleBtn.at(0).trigger('click')
    await nextTick()

    expect(wrapper.findAll('.content-slot-row').length).toBe(1)

    toggleBtn.at(1).trigger('click')
    await nextTick()

    expect(wrapper.findAll('.content-slot-row').length).toBe(2)

    toggleBtn.at(1).trigger('click')
    await nextTick()

    expect(wrapper.findAll('.content-slot-row').length).toBe(1)
  })

  it('getItemValue function works correctly', () => {
    const { getItemValue } = wrapper.vm

    expect(getItemValue(tableDataMock[0], 'name')).toBe('Row 1')
    expect(getItemValue(tableDataMock[0], 'dateField')).toBe(shortPacificDate('2024-01-01T00:00:00Z'))
    expect(getItemValue(tableDataMock[0], 'sections[0].serialNumber')).toBe('12345')
    expect(getItemValue(tableDataMock[0], ['baseInformation.make', 'baseInformation.model'])).toBe('Make1 Model1')
  })
})
