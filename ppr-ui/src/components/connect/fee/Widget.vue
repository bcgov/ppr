<script setup lang="ts">
const { t } = useI18n()
const fwConfig = useAppConfig().connect.feeWidget
const rtc = useRuntimeConfig().public
const {
  feeOptions,
  fees,
  placeholderFeeItem,
  total,
  totalServiceFees,
  totalFutureEffectiveFees,
  totalPriorityFees,
  totalProcessingFees,
  totalGst,
  totalPst,
  userSelectedPaymentMethod,
  allowedPaymentMethods,
  userPaymentAccount,
  allowAlternatePaymentMethod
} = storeToRefs(useConnectFeeStore())

const isPlaceholderActive = ref(false)

const feeItems = computed<ConnectFeeItem[]>(() => {
  if (fees.value && (Object.keys(fees.value).length > 0)) {
    isPlaceholderActive.value = false
    return Object.values(fees.value)
  }
  isPlaceholderActive.value = true
  return [placeholderFeeItem.value]
})

// folding stuff
const folded = ref(false)

const isFoldable = useMediaQuery('(max-width: 1024px)')
watch(isFoldable, (val) => {
  if (!val) {
    folded.value = false
  }
})

const toggleFolded = () => {
  if (isFoldable.value) {
    folded.value = !folded.value
  }
}

const getItemFee = (feeItem: ConnectFeeItem) => {
  if (feeItem.isPlaceholder) {
    return '$ -'
  }
  if (feeItem.waived) {
    return t('ConnectFeeWidget.feeSummary.noFee')
  }
  return `$${(feeItem.filingFees * (feeItem.quantity || 1)).toFixed(2)}`
}

const getFeeItemLabelTooltip = (typeCode: string) => {
  const tooltip = fwConfig?.itemLabelTooltip[typeCode]
  if (tooltip) {
    let link: string | undefined
    if (tooltip?.hrefRtcKey && tooltip?.hrefRtcKey in rtc) {
      link = rtc[tooltip.hrefRtcKey] as string
    }
    return {
      keypath: tooltip.i18nkey,
      link
    }
  }
  return undefined
}
</script>
<template>
  <div
    data-testid="fee-widget"
    class="z-10 mr-5 w-full rounded bg-white shadow-md lg:mr-0 lg:w-[320px]"
  >
    <UButton
      :tabindex="isFoldable ? 0 : -1"
      :role="isFoldable ? 'button' : 'title'"
      class="flex w-full bg-midnightBlue-900 py-2 pl-4 text-lg font-bold transition-all"
      :class="[folded ? 'rounded' : 'rounded-b-none rounded-t', isFoldable ? '' : 'pointer-events-none']"
      :aria-label="$t('ConnectFeeWidget.feeSummary.title')"
      :label="$t('ConnectFeeWidget.feeSummary.title')"
      @click="toggleFolded"
    >
      <template #trailing>
        <div class="flex grow justify-end pr-1">
          <UIcon
            v-if="isFoldable"
            class="size-7"
            :name="folded ? 'i-mdi-chevron-down' : 'i-mdi-chevron-up'"
          />
        </div>
      </template>
    </UButton>
    <ConnectTransitionCollapse>
      <div v-if="!folded">
        <div class="divide-y divide-bcGovGray-300 px-4 pt-1 text-sm">
          <div
            v-for="feeItem in feeItems"
            :key="feeItem.filingTypeCode"
            class="flex justify-between py-3"
          >
            <div>
              <p class="flex items-center gap-1 font-bold">
                <span>{{ $t(`ConnectFeeWidget.feeSummary.itemLabels.${feeItem.filingTypeCode}`) }}</span>
                <UPopover
                  v-if="getFeeItemLabelTooltip(feeItem.filingTypeCode)"
                  mode="hover"
                  :popper="{ placement: 'right' }"
                  :ui="{
                    rounded: 'rounded',
                    background: 'bg-gray-700/90',
                    base: 'overflow-hidden focus:outline-none relative'
                  }"
                >
                  <UIcon name="i-mdi-info-outline" class="size-5 shrink-0 translate-y-0.5 text-blue-500" />

                  <template #panel>
                    <div class="p-4 text-sm font-normal text-white">
                      <UButton
                        v-if="getFeeItemLabelTooltip(feeItem.filingTypeCode)?.link"
                        :label="$t(`${getFeeItemLabelTooltip(feeItem.filingTypeCode)?.keypath}`)"
                        :to="getFeeItemLabelTooltip(feeItem.filingTypeCode)?.link"
                        variant="link"
                        color="white"
                        target="_blank"
                        :padded="false"
                        class="underline"
                      />
                      <span v-else>{{ $t(`${getFeeItemLabelTooltip(feeItem.filingTypeCode)?.keypath}`) }}</span>
                    </div>
                  </template>
                </UPopover>
              </p>
              <p v-if="feeItem.quantity !== undefined && feeItem.quantityDesc" class="pl-4 text-gray-600">
                x {{ feeItem.quantity }} {{ feeItem.quantityDesc }}
              </p>
            </div>
            <p>{{ getItemFee(feeItem) }}</p>
          </div>
          <ConnectFeeExtraFee
            v-if="feeOptions.showFutureEffectiveFees"
            :description="$t('ConnectFeeWidget.feeSummary.futureEffectiveFees')"
            :fee="totalFutureEffectiveFees"
            :show-fee-value="isPlaceholderActive"
          />
          <ConnectFeeExtraFee
            v-if="feeOptions.showPriorityFees"
            :description="$t('ConnectFeeWidget.feeSummary.priorityFees')"
            :fee="totalPriorityFees"
            :show-fee-value="isPlaceholderActive"
          />
          <ConnectFeeExtraFee
            v-if="feeOptions.showProcessingFees"
            :description="$t('ConnectFeeWidget.feeSummary.processingFees')"
            :fee="totalProcessingFees"
            :show-fee-value="isPlaceholderActive"
          />
          <ConnectFeeExtraFee
            v-if="feeOptions.showServiceFees"
            :description="$t('ConnectFeeWidget.feeSummary.serviceFees')"
            :fee="isPlaceholderActive ? placeholderFeeItem.serviceFees : totalServiceFees"
            show-fee-value
          />
          <ConnectFeeExtraFee
            v-if="feeOptions.showPst"
            :description="$t('ConnectFeeWidget.feeSummary.pst')"
            :fee="totalPst"
            :show-fee-value="isPlaceholderActive"
          />
          <ConnectFeeExtraFee
            v-if="feeOptions.showGst"
            :description="$t('ConnectFeeWidget.feeSummary.gst')"
            :fee="totalGst"
            :show-fee-value="isPlaceholderActive"
          />
        </div>

        <div class="flex flex-row items-end justify-between border-y border-gray-300 p-3">
          <p class="mb-1 font-bold">
            {{ $t("ConnectFeeWidget.feeSummary.total") }}
          </p>
          <p class="flex items-end text-sm text-bcGovGray-700">
            <span class="mb-1">{{ $t("currency.cad") }}</span>
            <b class="ml-[5px] flex items-end text-2xl text-black">
              {{ !isPlaceholderActive ? `$${total.toFixed(2)}` : '$ -' }}
            </b>
          </p>
        </div>

        <USelectMenu
          v-if="allowAlternatePaymentMethod && allowedPaymentMethods.length > 1"
          v-model="userSelectedPaymentMethod"
          :items="allowedPaymentMethods"
          :search-input="false"
          value-key="value"
          :trailing="true"
          icon="i-mdi-caret-down"
          :ui="{
            base: 'flex w-full bg-white',
            trailingIcon: 'size-5 text-blue-500 group-data-[state=open]:rotate-180 transition-transform duration-200'
          }"
          :ui-menu="{
            option: {
              base: 'cursor-pointer',
              size: 'text-xs'
            },
            base: '-mt-1',
            rounded: 'rounded-b'
          }"
        >
          <button
            class="flex w-full items-center justify-between gap-4 py-2 pl-1 text-left bg-white cursor-pointer"
          >
            <span class="text-xs">
              {{
                $t(`ConnectFeeWidget.payingWith.${userSelectedPaymentMethod}`, {
                  account: userPaymentAccount?.cfsAccount?.bankAccountNumber }
                )
              }}
            </span>
          </button>
        </USelectMenu>
      </div>
    </ConnectTransitionCollapse>
  </div>
</template>
