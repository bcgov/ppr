import { ConnectPaymentMethod } from '~/enums/connect-payment-method'

export const useConnectFeeStore = defineStore('connect/fee', () => {
  const { $payApi } = useNuxtApp()
  const { t } = useI18n()

  const feeOptions = ref({
    showFutureEffectiveFees: false,
    showPriorityFees: false,
    showProcessingFees: false,
    showGst: false,
    showPst: false,
    showServiceFees: true
  })

  const fees = ref<ConnectFees>({})
  const placeholderFeeItem = ref<ConnectFeeItem>({
    isPlaceholder: true,
    filingFees: 0,
    filingType: 'placeholder',
    filingTypeCode: 'PLACEHOLDER',
    futureEffectiveFees: 0,
    priorityFees: 0,
    processingFees: 0,
    serviceFees: 0,
    tax: {
      gst: 0,
      pst: 0
    },
    total: 0
  })

  const getTotalFromFees = (feeValue: string, isTax = false) => {
    let total = 0
    for (const key of Object.keys(fees.value)) {
      if (fees.value[key]?.waived) {
        // if waived then total value for is 0
        continue
      }
      const quantity = fees.value[key]?.quantity ?? 1
      // @ts-ignore
      if (isTax && fees.value[key].tax[feeValue]) {
        // @ts-ignore
        total += fees.value[key].tax[feeValue] * quantity
      // @ts-ignore
      } else if (fees.value[key][feeValue]) {
        // @ts-ignore
        if (feeValue === 'total') {
          // ignore service fee and processing fee
          // - (otherwise incorrectly adding it for each item instead of once at the end)
          // @ts-ignore
          total += (fees.value[key].total - fees.value[key].serviceFees - fees.value[key].processingFees) * quantity
        } else {
          // @ts-ignore
          total += fees.value[key][feeValue] * quantity
        }
      }
    }
    return total
  }

  const getMaxFromFees = (feeValue: string) => {
    let maxFee = 0
    for (const key of Object.keys(fees.value)) {
      // @ts-ignore
      const itemFee = fees.value[key][feeValue]
      if (itemFee && (itemFee > maxFee)) {
        maxFee = itemFee
      }
    }
    return maxFee
  }

  const totalFutureEffectiveFees = computed(() => getTotalFromFees('futureEffectiveFees'))
  const totalPriorityFees = computed(() => getTotalFromFees('priorityFees'))
  const totalProcessingFees = computed(() => getMaxFromFees('processingFees'))
  const totalServiceFees = computed(() => getMaxFromFees('serviceFees'))
  const totalGst = computed(() => getTotalFromFees('gst', true))
  const totalPst = computed(() => getTotalFromFees('pst', true))
  const total = computed(() => getTotalFromFees('total') + totalServiceFees.value + totalProcessingFees.value)

  /**
   * Fetches the Fee info for the given entity type / fee code combination.
   *
   * @returns {Promise<Fee | undefined>} Fee data or undefined if an error occurs.
   */
  const getFee = async (
    entityType: string,
    code: string
  ): Promise<ConnectFeeItem | undefined> => {
    try {
      return await $payApi<ConnectFeeItem>(`/fees/${entityType}/${code}`)
    } catch (error) {
      console.error('Error fetching Fee: ', error)
    }
  }

  const addReplaceFee = (fee: ConnectFeeItem) => {
    fees.value[fee.filingTypeCode] = fee
  }
  const removeFee = (key: string) => {
    delete fees.value[key]
  }
  const setFeeQuantity = (key: string, quantity: number) => {
    if (fees.value[key]) {
      fees.value[key].quantity = quantity
    }
  }

  const setPlaceholderFilingTypeCode = (code: string) => {
    placeholderFeeItem.value.filingTypeCode = code
  }

  const setPlaceholderServiceFee = (fees: number) => {
    placeholderFeeItem.value.serviceFees = fees
  }

  // alternate payment option stuff
  const PAD_PENDING_STATES = [ConnectPayCfsStatus.PENDING, ConnectPayCfsStatus.PENDING_PAD_ACTIVATION]
  const userPaymentAccount = ref<ConnectPayAccount>({} as ConnectPayAccount)
  const userSelectedPaymentMethod = ref<ConnectPaymentMethod>(ConnectPaymentMethod.DIRECT_PAY)
  const allowAlternatePaymentMethod = ref<boolean>(false)
  const allowedPaymentMethods = ref<{ label: string, value: ConnectPaymentMethod }[]>([])

  watch(userSelectedPaymentMethod, () => {
    // if pad in confirmation period then set selected payment to CC
    if (PAD_PENDING_STATES.includes(userPaymentAccount.value?.cfsAccount?.status)) {
      userSelectedPaymentMethod.value = ConnectPaymentMethod.DIRECT_PAY
      // show modal for user
      useStrrModals().openErrorModal(
        t('modal.padConfirmationPeriod.title'),
        t('modal.padConfirmationPeriod.content'),
        false
      )
    }
  })

  const $resetAlternatePayOptions = () => {
    userPaymentAccount.value = {} as ConnectPayAccount
    userSelectedPaymentMethod.value = ConnectPaymentMethod.DIRECT_PAY
    allowAlternatePaymentMethod.value = false
    allowedPaymentMethods.value = []
  }

  const initAlternatePaymentMethod = async () => {
    $resetAlternatePayOptions()
    const accountId = useConnectAccountStore().currentAccount.id
    try {
      // get payment account
      const res = await $payApi<ConnectPayAccount>(`/accounts/${accountId}`)
      userPaymentAccount.value = res

      // add options to allowedPaymentMethods
      let defaultMethod = userPaymentAccount.value.paymentMethod
      if (defaultMethod !== undefined) {
        const accountNum = userPaymentAccount.value.cfsAccount?.bankAccountNumber ?? ''
        allowedPaymentMethods.value.push({
          label: t(`ConnectFeeWidget.paymentMethod.${defaultMethod}`, { account: accountNum }),
          value: defaultMethod
        })

        // only add direct pay if not default option
        if (defaultMethod !== ConnectPaymentMethod.DIRECT_PAY) {
          allowedPaymentMethods.value.push({
            label: t(`ConnectFeeWidget.paymentMethod.${ConnectPaymentMethod.DIRECT_PAY}`),
            value: ConnectPaymentMethod.DIRECT_PAY
          })
          // if pad in confirmation period then set default payment to CC
          if (PAD_PENDING_STATES.includes(res.cfsAccount.status)) {
            defaultMethod = ConnectPaymentMethod.DIRECT_PAY
          }
        }
      }
      userSelectedPaymentMethod.value = defaultMethod

      // only set allowed flag to true if previous steps didnt cause an error
      allowAlternatePaymentMethod.value = true
    } catch (e) {
      logFetchError(e, 'Error initializing user payment account')
    }
  }

  return {
    feeOptions,
    fees,
    placeholderFeeItem,
    totalFutureEffectiveFees,
    totalPriorityFees,
    totalProcessingFees,
    totalGst,
    totalPst,
    totalServiceFees,
    total,
    getFee,
    addReplaceFee,
    removeFee,
    setFeeQuantity,
    setPlaceholderFilingTypeCode,
    setPlaceholderServiceFee,
    initAlternatePaymentMethod,
    userPaymentAccount,
    userSelectedPaymentMethod,
    allowedPaymentMethods,
    allowAlternatePaymentMethod
  }
})
