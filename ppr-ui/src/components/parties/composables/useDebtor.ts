import { reactive, toRefs } from '@vue/composition-api'
import { PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useGetters, useActions } from 'vuex-composition-helpers'
import { Months } from '@/resources/months'
import { PartyAddressSchema } from '@/schemas'
import { useParty } from '@/composables/useParty'

const initPerson = { first: '', middle: '', last: '' }
const initAddress = {
  street: '',
  streetAdditional: '',
  city: '',
  region: '',
  country: '',
  postalCode: '',
  deliveryInstructions: ''
}
const { getDay, getMonth, getMonthFull, getYear } = useParty()

export const useDebtor = (props, context) => {
  const { setAddSecuredPartiesAndDebtors } = useActions<any>([
    'setAddSecuredPartiesAndDebtors'
  ])
  const { getAddSecuredPartiesAndDebtors } = useGetters<any>([
    'getAddSecuredPartiesAndDebtors'
  ])
  const localState = reactive({
    currentDebtor: {
      businessName: '',
      personName: initPerson,
      birthDate: '',
      address: initAddress
    } as PartyIF,
    year: '',
    day: '',
    monthValue: 0,
    months: Months,
    currentIsBusiness: props.isBusiness,
    showAllAddressErrors: false
  })

  const getDebtor = () => {
    const debtors: PartyIF[] = getAddSecuredPartiesAndDebtors.value.debtors
    if (props.activeIndex >= 0) {
      localState.currentDebtor = debtors[props.activeIndex]
      localState.currentIsBusiness = false
      if (localState.currentDebtor.businessName) {
        localState.currentIsBusiness = true
      } else {
        localState.year = getYear(localState.currentDebtor)
        localState.day = getDay(localState.currentDebtor)
      }
    } else {
      const blankDebtor = {
        businessName: '',
        personName: Object.assign({}, initPerson),
        birthDate: '',
        address: Object.assign({}, initAddress)
      }
      localState.currentDebtor = blankDebtor
    }
  }

  const addressSchema = PartyAddressSchema

  const resetFormAndData = (emitEvent: boolean): void => {
    if (emitEvent) {
      context.emit('resetEvent')
    }
  }
  const removeDebtor = (): void => {
    context.emit('removeDebtor', props.activeIndex)
    resetFormAndData(true)
  }

  const getMonthObject = () => {
    const partyMonth = {
      value: getMonth(localState.currentDebtor),
      text: getMonthFull(localState.currentDebtor)
    }
    return partyMonth
  }

  const addDebtor = () => {
    if (!localState.currentIsBusiness) {
      const dateOfBirth = new Date()
      // @ts-ignore - returned by toRef
      dateOfBirth.setFullYear(
        parseInt(localState.year),
        localState.monthValue - 1,
        parseInt(localState.day)
      )
      if (dateOfBirth instanceof Date && !isNaN(dateOfBirth.valueOf())) {
        localState.currentDebtor.birthDate = dateOfBirth.toUTCString()
      }
    }
    let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
    let newList: PartyIF[] = parties.debtors // eslint-disable-line
    // New debtor
    if (props.activeIndex === -1) {
      // localState.currentDebtor.id = newList.length + 1
      newList.push(localState.currentDebtor)
    } else {
      // Edit vehicle
      newList.splice(props.activeIndex, 1, localState.currentDebtor)
    }
    parties.debtors = newList
    // collateral.valid = true
    setAddSecuredPartiesAndDebtors(parties)
    context.emit('resetEvent')
  }

  return {
    getDebtor,
    addDebtor,
    resetFormAndData,
    removeDebtor,
    addressSchema,
    getMonthObject,
    ...toRefs(localState)
  }
}
