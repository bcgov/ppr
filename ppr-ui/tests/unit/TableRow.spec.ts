import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import { DraftResultIF, MhrDraftIF, MhRegistrationSummaryIF, RegistrationSummaryIF } from '@/interfaces'
import {
  mockedDraft1,
  mockedDraftAmend,
  mockedLockedMhRegistration,
  mockedManufacturerAuthRoles,
  mockedMhDraft,
  mockedMhRegistration, mockedMhRegistrationWithCancelNote,
  mockedRegistration1,
  mockedRegistration1Collapsed,
  mockedRegistration2Child,
  mockedRegistration2Collapsed,
  mockedRegistration3,
  mockedResidentialExemptionMhRegistration
} from './test-data'
import { createComponent, getLastEvent, getTestId, setupMockStaffUser } from './utils'
import { TableRow } from '@/components/tables/common'
import { mhRegistrationTableHeaders, registrationTableHeaders } from '@/resources'
import flushPromises from 'flush-promises'
import { APIStatusTypes, AuthRoles, MhApiStatusTypes, MhUIStatusTypes, ProductCode, TableActions } from '@/enums'
import { expect } from 'vitest'
import { DOMWrapper } from '@vue/test-utils'
import { defaultFlagSet } from '@/utils'

const store = useStore()

const btnExpArr = '.btn-row-expand-arr'
const btnExpTxt = '.btn-row-expand-txt'
const tableRow = '.registration-row'
const tableRowBaseReg = '.base-registration-row'
const tableRowDraft = '.draft-registration-row'

describe('TableRow tests', () => {
  let wrapper
  const registrationHistory: (RegistrationSummaryIF | DraftResultIF)[] = [
    mockedDraft1,
    mockedRegistration1Collapsed,
    mockedDraftAmend,
    mockedRegistration2Collapsed,
    mockedRegistration2Child,
    mockedRegistration3
  ]

  beforeEach(async () => {
    wrapper = await createComponent(
      TableRow,
      {
        isPpr: true,
        setAddRegEffect: false,
        setDisableActionShadow: false,
        setChild: false,
        setHeaders: [...registrationTableHeaders],
        setIsExpanded: false,
        setItem: mockedRegistration1
      }
    )
  })

  afterEach(() => {
    // Remove specific elements added during tests
    const appendedElements = document.querySelectorAll('.v-overlay__content')
    appendedElements.forEach((el) => el.remove())

    // Clean up the DOM after each test
    document.body.innerHTML = ''; // Clear the body's inner HTML
  })


  it('renders the row', async () => {
    expect(wrapper.findComponent(TableRow).exists()).toBe(true)
    expect(wrapper.vm.item).toEqual(mockedRegistration1)
    expect(wrapper.findAll(tableRow).length).toBe(1)
    expect(wrapper.findAll(tableRowBaseReg).length).toBe(1)
  })

  it('updates shown row cells when given new one headers', async () => {
    expect(wrapper.vm.$props.setHeaders).toEqual(registrationTableHeaders)
    expect(wrapper.findAll('td').length).toEqual(registrationTableHeaders.length)
    const newHeaders = [
      registrationTableHeaders[1],
      registrationTableHeaders[3],
      registrationTableHeaders[6],
      registrationTableHeaders[10]
    ]
    wrapper = await createComponent(
      TableRow,
      {
        isPpr: true,
        setAddRegEffect: false,
        setDisableActionShadow: false,
        setChild: false,
        setHeaders: [...newHeaders],
        setIsExpanded: false,
        setItem: mockedRegistration1
      }
    )
    await flushPromises()

    expect(wrapper.vm.$props.setHeaders).toEqual(newHeaders)
    await flushPromises()
    const rowCells = wrapper.findAll('td')
    expect(rowCells.length).toBe(newHeaders.length)
  })

  it('displays properly in the row for all types of items', async () => {
    for (let i = 0; i < registrationHistory.length; i++) {
      // both below are the same variable, but typed differently
      const baseReg = registrationHistory[i] as RegistrationSummaryIF
      const draftReg = registrationHistory[i] as DraftResultIF

      const isChild = (draftReg.type && draftReg.baseRegistrationNumber) ||
        (baseReg.registrationNumber && baseReg.registrationNumber !== baseReg.baseRegistrationNumber)
      wrapper = await createComponent(
        TableRow,
        {
          isPpr: true,
          setAddRegEffect: false,
          setDisableActionShadow: false,
          setChild: isChild,
          setHeaders: [...registrationTableHeaders],
          setIsExpanded: false,
          setItem: baseReg
        }
      )
      await flushPromises()
      expect(wrapper.vm.item).toEqual(baseReg)

      // it sets addRegEffect when given
      const applyAddedRegEffect = '.added-reg-effect'
      expect(wrapper.findAll(applyAddedRegEffect).length).toBe(0)
      wrapper = await createComponent(
        TableRow,
        {
          isPpr: true,
          setAddRegEffect: true,
          setDisableActionShadow: false,
          setChild: isChild,
          setHeaders: [...registrationTableHeaders],
          setIsExpanded: false,
          setItem: baseReg
        }
      )
      await flushPromises()
      expect(wrapper.vm.applyAddedRegEffect).toBe(true)
      expect(wrapper.findAll(applyAddedRegEffect).length).toBe(1)
      // changes when updated
      wrapper = await createComponent(
        TableRow,
        {
          isPpr: true,
          setAddRegEffect: false,
          setDisableActionShadow: false,
          setChild: isChild,
          setHeaders: [...registrationTableHeaders],
          setIsExpanded: false,
          setItem: baseReg
        }
      )
      expect(wrapper.vm.applyAddedRegEffect).toBe(false)
      expect(wrapper.findAll(applyAddedRegEffect).length).toBe(0)

      // check things specific to state / heirarchy of the item
      if (!draftReg.type) {
        // not a draft
        let rowData
        if (!isChild) {
          // parent registration
          rowData = wrapper.findAll(tableRowBaseReg + ' td')
          expect(rowData.length).toBe(11)
          // reg num
          if (baseReg.changes) {
            expect(rowData.at(0).find(btnExpArr).exists()).toBe(true)
          } else {
            expect(rowData.at(0).find(btnExpArr).exists()).toBe(false)
          }
          // base reg num
          expect(rowData.at(0).text()).not.toContain('Base Registration:')
          expect(rowData.at(0).text()).toContain(baseReg.baseRegistrationNumber)
          // reg type
          expect(rowData.at(1).text()).toContain('- Base Registration')
          if (baseReg.changes) {
            expect(rowData.at(1).find(btnExpTxt).exists()).toBe(true)
            expect(rowData.at(1).find(btnExpTxt).text()).toContain('View')
          } else {
            expect(rowData.at(1).find(btnExpTxt).exists()).toBe(false)
          }
          // status type
          expect(rowData.at(3).text()).toContain(wrapper.vm.getStatusDescription(baseReg.statusType, false, true))
          // expire days
          if ([APIStatusTypes.DISCHARGED, APIStatusTypes.EXPIRED].includes(baseReg.statusType as APIStatusTypes)) {
            expect(rowData.at(8).text()).toContain('—')
          } else {
            expect(rowData.at(8).text()).toContain(wrapper.vm.showExpireDays(baseReg))
          }
          // action btn
          if (![APIStatusTypes.DISCHARGED, APIStatusTypes.EXPIRED].includes(baseReg.statusType as APIStatusTypes)) {
            expect(rowData.at(10).text()).toContain('Amend')
          } else {
            expect(rowData.at(10).text()).toContain('Remove From Table')
          }
        } else {
          // child registration
          rowData = wrapper.findAll(tableRow + ' td')
          expect(rowData.length).toBe(11)
          // regNum
          expect(rowData.at(0).text()).toContain(baseReg.registrationNumber)
          expect(rowData.at(0).text()).toContain(`Base Registration: ${baseReg.baseRegistrationNumber}`)
          // reg type
          expect(rowData.at(1).text()).not.toContain('- Base Registration')
          expect(rowData.at(1).find(btnExpTxt).exists()).toBe(false)
          // status type
          expect(rowData.at(3).text()).toEqual('')
          // expiry days
          expect(rowData.at(8).text()).toEqual('')
          // action btn is not there
          expect(rowData.at(10).text()).toContain('')
        }
        // reg type
        expect(rowData.at(1).text()).toContain(wrapper.vm.getRegistrationType(baseReg.registrationType))
        // submitted date
        expect(rowData.at(2).text()).toContain(wrapper.vm.getFormattedDate(baseReg.createDateTime))
        // registering name
        expect(rowData.at(4).text()).toContain(baseReg.registeringName)
        // registering party
        expect(rowData.at(5).text()).toContain(baseReg.registeringParty)
        // secured party
        expect(rowData.at(6).text()).toContain(baseReg.securedParties)
        // pdf
        if (baseReg.path) expect(rowData.at(9).text()).toContain('PDF')
        else expect(rowData.at(9).find('.mdi-information-outline').exists()).toBe(true)
      } else {
        // draft registration
        let rowData
        if (!isChild) rowData = wrapper.findAll(tableRowDraft + ' td')
        else rowData = wrapper.findAll(tableRow + ' td')
        expect(rowData.length).toBe(11)
        // reg num
        if (isChild) expect(rowData.at(0).text()).toBe(`Pending Base Registration: ${baseReg.baseRegistrationNumber}`)
        else expect(rowData.at(0).text()).toBe('Pending')
        // submitted date
        expect(rowData.at(2).text()).toBe('Not Registered')
        // status type
        expect(rowData.at(3).text()).toContain(wrapper.vm.getStatusDescription(baseReg.statusType, isChild, true))
        // expire days
        if (isChild) expect(rowData.at(8).text()).toEqual('')
        else expect(rowData.at(8).text()).toBe('N/A')
        // pdf
        expect(rowData.at(9).text()).toEqual('')
        // action btn
        expect(rowData.at(10).text()).toContain('Edit')
      }
      // check things that apply to all items
      const rowData = wrapper.findAll(tableRow + ' td')
      // folio
      expect(rowData.at(7).text()).toContain(baseReg.clientReferenceId)
    }
  })

  it('emits button actions from TableRow', async () => {
    expect(wrapper.vm.item).toEqual(mockedRegistration1)
    // main button: active reg
    const activeRegButton = wrapper.findAll('.edit-action .v-btn')
    expect(activeRegButton.length).toBe(1)
    expect(activeRegButton.at(0).text()).toContain('Amend')
    activeRegButton.at(0).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.AMEND, regNum: mockedRegistration1.baseRegistrationNumber }
    )
    // dropdown buttons
    let buttons = wrapper.findAll('.actions__more-actions__btn')
    expect(buttons.length).toBe(1)

    // click dropdown for active reg
    buttons.at(0).trigger('click')
    await nextTick()

    // Query the document body for the menu content
    const menuContent = document.querySelector('.v-overlay__content')
    expect(menuContent).toBeTruthy()

    // Query and create wrappers of the menu content items
    const menuItems = menuContent.querySelectorAll('.v-list-item')
    expect(menuItems).toBeTruthy()
    const menuItemWrappers = Array.from(menuItems).map((element) => new DOMWrapper(element))

    expect(menuItemWrappers.length).toBe(3)
    expect(menuItemWrappers[0].text()).toContain('Total Discharge')
    expect(menuItemWrappers[1].text()).toContain('Renew')
    expect(menuItemWrappers[2].text()).toContain('Remove From Table')

    // click items and check emit
    const actions = [TableActions.DISCHARGE, TableActions.RENEW, TableActions.REMOVE]
    for (let i = 0; i < actions.length; i++) {
      await menuItemWrappers[i].trigger('click')
      expect(getLastEvent(wrapper, 'action')).toEqual(
        { action: actions[i], regNum: mockedRegistration1.baseRegistrationNumber }
      )
    }

    // main buttons: discharged/expired
    expect(mockedRegistration3.statusType).toBe(APIStatusTypes.DISCHARGED)
    wrapper = await createComponent(
      TableRow,
      {
        isPpr: true,
        setAddRegEffect: false,
        setDisableActionShadow: false,
        setChild: false,
        setHeaders: [...registrationTableHeaders],
        setIsExpanded: false,
        setItem: mockedRegistration3
      }
    )
    await flushPromises()


    const dischargedRegButton = wrapper.findAll('.edit-action .v-btn')
    expect(dischargedRegButton.length).toBe(1)
    expect(dischargedRegButton.at(0).text()).toContain('Remove From Table')
    // FUTURE: test it emits the correct thing here once built
    activeRegButton.at(0).trigger('click')

    // click dropdown for discharged reg
    buttons = wrapper.findAll('.actions__more-actions__btn')
    expect(buttons.length).toBe(0)
    await dischargedRegButton.at(0).trigger('click')
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.REMOVE, regNum: mockedRegistration3.baseRegistrationNumber }
    )
  })

  it('emits button actions properly for draft registrations', async () => {
    wrapper = await createComponent(
      TableRow,
      {
        isPpr: true,
        setAddRegEffect: false,
        setDisableActionShadow: false,
        setChild: false,
        setHeaders: [...registrationTableHeaders],
        setIsExpanded: false,
        setItem: mockedDraft1
      }
    )
    await flushPromises()

    // main buttons: new
    const draftNewRegButton = wrapper.findAll('.edit-action .v-btn')
    expect(draftNewRegButton.length).toBe(1)
    expect(draftNewRegButton.at(0).text()).toContain('Edit')
    draftNewRegButton.at(0).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.EDIT_NEW, docId: mockedDraft1.documentId }
    )

    // drop down buttons
    let dropButtons = wrapper.findAll('.actions__more-actions__btn.reg-table')
    expect(dropButtons.length).toBe(1)
    dropButtons.at(0).trigger('click')
    await nextTick()

    // Query the document body for the menu content
    let menuContent2 = document.querySelector('.v-overlay__content')
    expect(menuContent2).toBeTruthy()

    // it renders the delete action in drop down
    const menuItems2 = menuContent2.querySelectorAll('.v-list-item')
    expect(menuItems2).toBeTruthy()
    const menuItemWrappers2 = Array.from(menuItems2).map((element) => new DOMWrapper(element))

    expect(menuItemWrappers2.length).toBe(1)
    expect(menuItemWrappers2.at(0).text()).toContain('Delete Draft')
    await menuItemWrappers2.at(0).trigger('click')
    expect(getLastEvent(wrapper, 'action')).toEqual(
      { action: TableActions.DELETE, docId: mockedDraft1.documentId, regNum: '' }
    )

    // main buttons: amend draft
    wrapper = await createComponent(
      TableRow,
      {
        isPpr: true,
        setAddRegEffect: false,
        setDisableActionShadow: false,
        setChild: true,
        setHeaders: [...registrationTableHeaders],
        setIsExpanded: false,
        setItem: mockedDraftAmend
      }
    )
    await flushPromises()
    const draftAmendRegButton = wrapper.findAll('.edit-action .v-btn')
    expect(draftAmendRegButton.length).toBe(1)
    expect(draftAmendRegButton.at(0).text()).toContain('Edit')
    draftAmendRegButton.at(0).trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'action'))
      .toEqual(
        {
          action: TableActions.EDIT_AMEND,
          docId: mockedDraftAmend.documentId,
          regNum: mockedDraftAmend.baseRegistrationNumber
        }
      )

    dropButtons = wrapper.findAll('.actions__more-actions__btn')
    expect(dropButtons.length).toBe(1)
    dropButtons.at(0).trigger('click')
    await nextTick()

    // it renders the delete action in drop down
    const menuContent3 = document.querySelector('.v-overlay__content')
    const menuItemsDelete = menuContent3.querySelectorAll('.draft-actions  .v-list-item')
    const menuItemsDeleteWrappers = Array.from(menuItemsDelete).map((element) => new DOMWrapper(element))

    expect(menuItemsDeleteWrappers.length).toBe(1)
    expect(menuItemsDeleteWrappers.at(0).text()).toContain('Delete Draft')
    await menuItemsDeleteWrappers.at(0).trigger('click')
  })
})

describe('Mhr TableRow tests', () => {
  let wrapper
  const registrationHistory: (MhRegistrationSummaryIF | MhrDraftIF)[] = [
    mockedMhDraft,
    mockedMhRegistration
  ]
  defaultFlagSet['mhr-exemption-enabled'] = true

  beforeEach(async () => {
    setupMockStaffUser()
    wrapper = await createComponent(
      TableRow,
      {
        isPpr: false,
        setAddRegEffect: false,
        setDisableActionShadow: false,
        setChild: false,
        setHeaders: [...mhRegistrationTableHeaders],
        setIsExpanded: false,
        setItem: mockedMhRegistration
      }
    )
    await flushPromises()
  })

  afterEach(() => {
    // Remove specific elements added during tests
    const appendedElements = document.querySelectorAll('.v-overlay__content')
    appendedElements.forEach((el) => el.remove())

    // Clean up the DOM after each test
    document.body.innerHTML = ''; // Clear the body's inner HTML
  })

  it('renders the row', async () => {
    expect(wrapper.findComponent(TableRow).exists()).toBe(true)
    expect(wrapper.vm.item).toEqual(mockedMhRegistration)
    expect(wrapper.findAll(tableRow).length).toBe(1)
    expect(wrapper.findAll(tableRowBaseReg).length).toBe(1)
  })

  for (let i = 0; i < registrationHistory.length; i++) {
    it(`displays properly in the row for all types of items: ${registrationHistory[i].statusType}`, async () => {
        // both below are the same variable, but typed differently
        const baseReg = registrationHistory[i] as MhRegistrationSummaryIF
        const draftReg = registrationHistory[i] as MhrDraftIF

        const isChild = (draftReg.type && draftReg.mhrNumber) ||
          (baseReg.mhrNumber && baseReg.mhrNumber !== baseReg.baseRegistrationNumber)

        wrapper = await createComponent(
          TableRow,
          {
            isPpr: false,
            setAddRegEffect: false,
            setDisableActionShadow: false,
            setChild: isChild,
            setHeaders: [...mhRegistrationTableHeaders],
            setIsExpanded: false,
            setItem: baseReg
          }
        )
        await flushPromises()

        expect(wrapper.vm.item).toEqual(baseReg)

        // it sets addRegEffect when given
        const applyAddedRegEffect = '.added-reg-effect'
        expect(wrapper.findAll(applyAddedRegEffect).length).toBe(0)
        wrapper = await createComponent(
          TableRow,
          {
            isPpr: false,
            setAddRegEffect: true,
            setDisableActionShadow: false,
            setChild: isChild,
            setHeaders: [...mhRegistrationTableHeaders],
            setIsExpanded: false,
            setItem: baseReg
          }
        )
        await flushPromises()

        expect(wrapper.vm.applyAddedRegEffect).toBe(true)
        expect(wrapper.findAll(applyAddedRegEffect).length).toBe(1)
        // changes when updated
        wrapper = await createComponent(
          TableRow,
          {
            isPpr: false,
            setAddRegEffect: false,
            setDisableActionShadow: false,
            setChild: isChild,
            setHeaders: [...mhRegistrationTableHeaders],
            setIsExpanded: false,
            setItem: baseReg
          }
        )
        await flushPromises()

        expect(wrapper.vm.applyAddedRegEffect).toBe(false)
        expect(wrapper.findAll(applyAddedRegEffect).length).toBe(0)

        // check things specific to state / hierarchy of the item
        if (!draftReg.type) {
          // not a draft
          let rowData
          if (!isChild) {
            // parent registration
            rowData = wrapper.findAll(tableRowBaseReg + ' td')
            expect(rowData.length).toBe(11)
            // reg num
            if (baseReg.changes) {
              expect(rowData.at(0).find(btnExpArr).exists()).toBe(true)
            } else {
              expect(rowData.at(0).find(btnExpArr).exists()).toBe(false)
            }
            // base reg num
            expect(rowData.at(0).text()).toContain(baseReg.baseRegistrationNumber)
            // reg type
            if (baseReg.changes) {
              expect(rowData.at(1).find(btnExpTxt).exists()).toBe(true)
              expect(rowData.at(1).find(btnExpTxt).text()).toContain('View')
            } else {
              expect(rowData.at(1).find(btnExpTxt).exists()).toBe(false)
            }
            // status type
            expect(rowData.at(3).text()).toContain(wrapper.vm.getStatusDescription(baseReg.statusType, isChild, false))
            // expire days
            expect(rowData.at(8).text()).toContain(wrapper.vm.showExpireDays(baseReg))
            // action btn
            expect(rowData.at(10).text()).toContain('Remove From Table')
          } else {
            // child registration
            rowData = await wrapper.findAll(tableRow + ' td')
            expect(rowData.length).toBe(11)

            // regNum
            expect(rowData.at(0).text()).toContain(`${baseReg.baseRegistrationNumber}`)
            // reg type
            expect(rowData.at(1).find(btnExpTxt).exists()).toBe(false)
            // status type
            expect(rowData.at(3).text()).toEqual('') // child status should be empty
            // expiry days
            expect(rowData.at(8).text()).toEqual('1 year 135 days')
            // action btn is not there
            expect(rowData.at(10).text()).toContain('')
          }
          // reg type
          expect(rowData.at(1).text()).toContain(wrapper.vm.getRegistrationType(baseReg.registrationType))
          // submitted date
          expect(rowData.at(2).text()).toContain(wrapper.vm.getFormattedDate(baseReg.createDateTime))
          // pdf
          if (baseReg.path) expect(rowData.at(9).text()).toContain('PDF')
          else expect(rowData.at(9).find('.mdi-information-outline').exists()).toBe(true)
        }
        // check things that apply to all items
        const rowData = wrapper.findAll(tableRow + ' td')
        // folio
        expect(rowData.at(7).text()).toContain(baseReg.clientReferenceId)
    })
  }

  it('displays caution icon for Frozen Affidavit Mhrs', async () => {
    const frozenRegistrationHistory: (MhRegistrationSummaryIF)[] = [
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.FROZEN, frozenDocumentType: 'AFFE' }
    ]

    for (let i = 0; i < frozenRegistrationHistory.length; i++) {
      // both below are the same variable, but typed differently
      const baseReg = frozenRegistrationHistory[i] as MhRegistrationSummaryIF

      wrapper = await createComponent(
        TableRow,
        {
          isPpr: false,
          setAddRegEffect: false,
          setDisableActionShadow: false,
          setChild: false,
          setHeaders: [...mhRegistrationTableHeaders],
          setIsExpanded: false,
          setItem: baseReg
        }
      )
      await flushPromises()
      expect(wrapper.vm.item).toEqual(baseReg)

      const rowData = wrapper.findAll(tableRowBaseReg + ' td')
      expect(rowData.length).toBe(11)
      // base reg num
      expect(rowData.at(0).text()).toContain(baseReg.baseRegistrationNumber)
      const alertIcon = rowData.at(0).find(getTestId('alert-icon'))
      expect(alertIcon.exists()).toBeTruthy()
    }
  })

  it('displays locked badge for MHR that has a frozen Unit Note', async () => {
    const lockedRegistrationHistory: (MhRegistrationSummaryIF)[] = [mockedLockedMhRegistration]

    await store.setMhrTableHistory(lockedRegistrationHistory)
    // Set user as Qualified Supplier
    await store.setAuthRoles([AuthRoles.MHR_TRANSFER_SALE])
    await store.setUserProductSubscriptionsCodes([ProductCode.MANUFACTURER])
    await nextTick()

    const rowData = await wrapper.findAll(tableRowBaseReg + ' td')
    const lockedIcon = rowData.at(0).find(getTestId('LOCKED-badge'))
    expect(lockedIcon.exists()).toBeTruthy()
    expect(rowData.at(0).text()).toContain('LOCKED')
  })

  it('displays the correct status for all mhStatusTypes', async () => {
    const registrations: (MhRegistrationSummaryIF)[] = [
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.EXEMPT },
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.CANCELLED },
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.ACTIVE },
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.DRAFT },
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.FROZEN }
    ]

    for (const reg of registrations) {
      wrapper = await createComponent(
        TableRow,
        {
          isPpr: false,
          setAddRegEffect: false,
          setDisableActionShadow: false,
          setChild: false,
          setHeaders: [...mhRegistrationTableHeaders],
          setIsExpanded: false,
          setItem: reg
        }
      )
      await flushPromises()

      expect(wrapper.vm.item).toEqual(reg)
      const rowData = wrapper.findAll(tableRow + ' td')
      switch (reg.statusType) {
        case MhApiStatusTypes.ACTIVE:
          expect(rowData.at(3).text()).toContain(MhUIStatusTypes.ACTIVE)
          break
        case MhApiStatusTypes.DRAFT:
          expect(rowData.at(3).text()).toContain(MhUIStatusTypes.DRAFT)
          expect(rowData.at(rowData.length - 1).text()).toContain('Edit')
          break
        case MhApiStatusTypes.EXEMPT:
          expect(rowData.at(3).text()).toContain(MhUIStatusTypes.EXEMPT)
          break
        case MhApiStatusTypes.FROZEN:
          expect(rowData.at(3).text()).toContain(MhUIStatusTypes.ACTIVE)
          break
        case MhApiStatusTypes.CANCELLED:
          expect(rowData.at(3).text()).toContain(MhUIStatusTypes.CANCELLED)
          break
        default:
          fail('No/Unknown MhStatusType')
      }
    }
  })

  it('displays the correct status (empty) for all mhStatusTypes as children', async () => {
    const registrations: (MhRegistrationSummaryIF)[] = [
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.EXEMPT },
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.CANCELLED },
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.ACTIVE },
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.DRAFT },
      { ...mockedMhRegistration, statusType: MhApiStatusTypes.FROZEN }
    ]

    for (const reg of registrations) {
      wrapper = await createComponent(
        TableRow,
        {
          isPpr: false,
          setAddRegEffect: false,
          setDisableActionShadow: false,
          setChild: true,
          setHeaders: [...mhRegistrationTableHeaders],
          setIsExpanded: false,
          setItem: reg
        }
      )
      await flushPromises()

      expect(wrapper.vm.item).toEqual(reg)
      const rowData = wrapper.findAll(tableRow + ' td')
      switch (reg.statusType) {
        case MhApiStatusTypes.ACTIVE:
        case MhApiStatusTypes.EXEMPT:
        case MhApiStatusTypes.FROZEN:
        case MhApiStatusTypes.CANCELLED:
          expect(rowData.at(3).text()).toContain('')
          break
        case MhApiStatusTypes.DRAFT:
          expect(rowData.at(3).text()).toContain('')
          expect(rowData.at(rowData.length - 1).text()).toContain('Edit')
          break
        default:
          fail('No/Unknown MhStatusType')
      }
    }
  })

  it('should displays correct dropdown options for Exempt MHR (Staff and Qualified Supplier)', async () => {
    await store.setAuthRoles([AuthRoles.PPR_STAFF])
    const registration: MhRegistrationSummaryIF = mockedResidentialExemptionMhRegistration

    wrapper = await createComponent(
      TableRow,
      {
        isPpr: false,
        setAddRegEffect: false,
        setDisableActionShadow: false,
        setChild: false,
        setHeaders: [...mhRegistrationTableHeaders],
        setIsExpanded: false,
        setItem: registration
      }
    )
    await flushPromises()

    expect(wrapper.vm.item).toEqual(registration)

    const rowData = wrapper.findAll(tableRow + ' td')

    expect(rowData.at(3).text()).toContain(MhUIStatusTypes.EXEMPT) // Status column data
    expect(rowData.at(rowData.length - 1).text()).toContain('Open')

    wrapper.find('.actions__more-actions__btn').trigger('click')
    await nextTick()

    const staffMenu = document.querySelector('.v-overlay__content')
    expect(staffMenu).toBeTruthy()

    // Query and create wrappers of the menu content items
    const staffMenuItems = staffMenu.querySelectorAll('.v-list-item')
    expect(staffMenuItems).toBeTruthy()
    const staffMenuItemWrappers = Array.from(staffMenuItems).map((element) => new DOMWrapper(element))

    expect(staffMenuItemWrappers.length).toBe(4)
    expect(staffMenuItemWrappers.at(0).text()).toBe('Re-Register Manufactured Home')
    expect(staffMenuItemWrappers.at(1).text()).toBe('Non-Residential Exemption')
    expect(staffMenuItemWrappers.at(2).text()).toBe('Historical Home Information')
    expect(staffMenuItemWrappers.at(3).text()).toBe('Remove From Table')

    // Left in for future reference or implementation
    // expect(staffMenuItems.find(getTestId('res-exemption-btn')).exists()).toBeFalsy() // res exemption already filed
    // expect(staffMenuItems.find(getTestId('non-res-exemption-btn')).exists()).toBeTruthy()
    // expect(staffMenuItems.find(getTestId('remove-mhr-row-btn')).exists()).toBeTruthy()

    // Change role to Qualified Supplier
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.MANUFACTURER])
    await nextTick()

    wrapper.find('.actions__more-actions__btn').trigger('click')
    await nextTick()

    const qsMenuItems = staffMenu.querySelectorAll('.v-list-item')
    expect(staffMenuItems).toBeTruthy()
    const qsMenuItemsWrappers = Array.from(qsMenuItems).map((element) => new DOMWrapper(element))
    expect(qsMenuItemsWrappers.length).toBe(1)
    expect(qsMenuItemsWrappers.at(0).text()).toBe('Remove From Table')

    // Left in for future reference or implementation
    // expect(qsMenuItems.find(getTestId('rescind-exemption-btn')).exists()).toBeFalsy() // staff only
    // expect(qsMenuItems.find(getTestId('res-exemption-btn')).exists()).toBeFalsy() // res exemption already filed
    // expect(qsMenuItems.find(getTestId('non-res-exemption-btn')).exists()).toBeFalsy() // staff only
    // expect(qsMenuItems.find(getTestId('remove-mhr-row-btn')).exists()).toBeTruthy()
  })

  it('correctly displays a cancel note', async () => {
    const cancelNote = mockedMhRegistrationWithCancelNote.changes
      .find(change => change.registrationDescription === 'CANCEL NOTE')

    wrapper = await createComponent(
      TableRow,
      {
        isPpr: false,
        setAddRegEffect: false,
        setDisableActionShadow: false,
        setChild: true,
        setHeaders: [...mhRegistrationTableHeaders],
        setIsExpanded: false,
        setItem: cancelNote
      }
    )
    await flushPromises()



    expect(wrapper.vm.item).toEqual(cancelNote)
    const rowData = wrapper.findAll(tableRow + ' td')

    // reg type
    expect(rowData.at(1).text()).toContain('Cancel Note')
    expect(rowData.at(1).text()).toContain('Notice of Caution')
  })
})
