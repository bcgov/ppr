import { describe, it, expect, beforeEach } from 'vitest'
import { SimpleTable } from '@/components/common'
import { createComponent } from './utils'

const tableHeadersMock = [
  { name: 'Header 1', class: 'header-class-1' },
  { name: 'Header 2', class: 'header-class-2' },
]

const tableDataMock = [
  { name: 'Row 1' },
  { name: 'Row 2' },
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
    expect(rows.length).toBe(tableDataMock.length)
    rows.forEach((row, index) => {
      expect(row.find('td').text()).toBe(tableDataMock[index].name)
    })
  })
})
