import { reactive, toRefs, computed } from '@vue/composition-api'
import { PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { useGetters, useActions } from 'vuex-composition-helpers'

export const useDebtor = (props, context) => {
  const { setAddSecuredPartiesAndDebtors } = useActions<any>(['setAddSecuredPartiesAndDebtors'])
  const { getAddSecuredPartiesAndDebtors } = useGetters<any>(['getAddSecuredPartiesAndDebtors'])
  const localState = reactive({
    currentDebtor: {} as PartyIF
  })

  const getDebtor = () => {
    const debtors: PartyIF[] = getAddSecuredPartiesAndDebtors.value.debtors
    if (props.activeIndex >= 0) {
      localState.currentDebtor = debtors[props.activeIndex]
    } else {
      const initPerson = { first: '', middle: '', last: '' }
      const initAddress = {
        street: '',
        streetAdditional: '',
        city: '',
        region: '',
        country: '',
        postalCode: ''
      }
      localState.currentDebtor = { businessName: '', personName: initPerson, birthDate: '', address: initAddress }
    }
    console.log(localState.currentDebtor)
  }

  const resetFormAndData = (emitEvent: boolean): void => {
    if (emitEvent) {
      context.emit('resetEvent')
    }
  }
  const removeDebtor = (): void => {
    context.emit('removeDebtor', props.activeIndex)
    resetFormAndData(true)
  }

  const addDebtor = () => {
    let parties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
    let newList: PartyIF[] = parties.debtors // eslint-disable-line
    // New vehicle
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
    ...toRefs(localState)
  }
}
