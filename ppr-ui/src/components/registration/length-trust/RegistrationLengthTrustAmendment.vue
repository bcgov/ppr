<template>
  <div id="length-trust-amendment">
    <header
      v-if="!isSummary"
      class="summary-header"
    >
      <v-icon color="darkBlue">
        mdi-calendar-clock
      </v-icon>
      <h3 class="fs-16 lh-24 ml-3 pr-2">
        Current Expiry
        <span v-if="showTrustIndenture"> and Trust Indenture</span>
        <span v-if="displayHistoricalLienInfo"> and Historical Information</span>
      </h3>
    </header>
    <v-card
      v-if="!summaryView"
      flat
      class="bg-white pb-6 px-8 rounded-bottom"
      :class="{ 'border-error-left': showErrorBar && editInProgress }"
    >
      <v-row
        no-gutters
        class="pt-6"
      >
        <v-col
          cols="3"
          class="generic-label pr-2"
        >
          Current Expiry Date and Time
        </v-col>
        <v-col
          id="current-expiry"
          cols="9"
        >
          {{ computedExpiryDateFormatted }}
        </v-col>
      </v-row>
      <v-row
        v-if="showTrustIndenture && !showEditTrustIndenture"
        no-gutters
        class="pt-6"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Trust Indenture
          <div v-if="trustIndentureModified">
            <v-chip
              x-small
              variant="elevated"
              color="primary"
            >
              AMENDED
            </v-chip>
          </div>
        </v-col>
        <v-col
          cols="7"
          class="summary-text"
        >
          {{ trustIndentureSummary }}
        </v-col>
        <v-col
          cols="2"
          class="text-right"
        >
          <span
            v-if="trustIndentureModified"
            class="edit-action"
          >
            <v-btn
              id="trust-indenture-undo-btn"
              variant="plain"
              color="primary"
              class="smaller-button edit-btn pb-4"
              :disabled="editInProgress"
              @click="undoTrustIndenture()"
            >
              <v-icon size="small">mdi-undo</v-icon>
              <span>Undo</span>
            </v-btn>
          </span>
          <span
            v-else
            class="edit-action"
          >
            <v-btn
              id="trust-indenture-amend-btn"
              variant="plain"
              color="primary"
              class="smaller-button edit-btn pb-4"
              :disabled="editInProgress"
              @click="initEdit()"
            >
              <v-icon size="small">mdi-pencil</v-icon>
              <span>Amend</span>
            </v-btn>
          </span>
        </v-col>
      </v-row>
      <!-- Edit -->
      <v-row
        v-if="showEditTrustIndenture"
        no-gutters
      >
        <v-col
          cols="12"
          class="edit-debtor-container pa-0"
        >
          <edit-trust-indenture
            :current-trust-indenture="trustIndenture"
            @edit-trust-indenture="resetEdit"
            @reset-event="resetEdit"
          />
        </v-col>
      </v-row>
    </v-card>

    <v-container
      v-else
      class="bg-white pa-0 noGutters"
      fluid
    >
      <v-row
        no-gutters
        class="py-8"
      >
        <v-col
          cols="3"
          class="generic-label pl-3"
        >
          Trust Indenture
          <div v-if="trustIndentureModified">
            <v-chip
              x-small
              variant="elevated"
              color="primary"
            >
              AMENDED
            </v-chip>
          </div>
        </v-col>
        <v-col
          cols="9"
          class="summary-text"
        >
          {{ trustIndentureSummary }}
        </v-col>
      </v-row>
    </v-container>

    <!-- Historical Repairers Lien Information -->
    <v-card
      v-if="displayHistoricalLienInfo"
      flat
      class="mt-1 pl-8 bg-white py-6 rounded"
    >
      <v-row
        no-gutters
        class="pt-1"
      >
        <v-col
          cols="12"
          class="generic-label"
        >
          Historical Information
        </v-col>
        <p>Surrender Date and Lien Amount are kept for historical reference from the original Repairers Lien.</p>
      </v-row>
      <v-row no-gutters class="mt-4">
        <v-col cols="3" class="generic-label-14">
          Surrender Date
        </v-col>
        <v-col cols="9">
          {{ convertDate(new Date(getLengthTrust.surrenderDate), false, false) }}
        </v-col>
      </v-row>
      <v-row no-gutters class="mt-4">
        <v-col cols="3" class="generic-label-14">
          Amount of Lien
        </v-col>
        <v-col cols="9">
          {{ lienAmountSummary }}
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch,
  onMounted
} from 'vue'
import { useStore } from '@/store/store'
import type { LengthTrustIF } from '@/interfaces'
import { convertDate, formatExpiryDate } from '@/utils'
import { APIRegistrationTypes } from '@/enums'
import { storeToRefs } from 'pinia'

export default defineComponent({
  props: {
    isSummary: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  emits: ['lengthTrustOpen'],
  setup (props, context) {
    const { setLengthTrust } = useStore()
    const {
      // Getters
      displayHistoricalLienInfo,
      getLengthTrust,
      getOriginalLengthTrust,
      getRegistrationType,
      getRegistrationExpiryDate
    } = storeToRefs(useStore())
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const modal = false

    const localState = reactive({
      showEditTrustIndenture: false,
      editInProgress: false,
      originalTrustIndenture: getOriginalLengthTrust.value.trustIndenture,
      lifeInfinite: getLengthTrust.value.valid ? getLengthTrust.value.lifeInfinite.toString() : '',
      trustIndentureHint: '',
      showTrustIndenture: computed((): boolean => {
        return registrationType === APIRegistrationTypes.SECURITY_AGREEMENT
      }),
      summaryView: computed((): boolean => {
        return props.isSummary
      }),
      computedExpiryDateFormatted: computed((): string => {
        if (getLengthTrust.value.lifeInfinite) {
          return 'No Expiry'
        }
        if ((getRegistrationExpiryDate.value)) {
          return formatExpiryDate(new Date(new Date(getRegistrationExpiryDate.value)
            .toLocaleString('en-US', { timeZone: 'America/Vancouver' })))
        }
        return ''
      }),
      lengthTrust: computed((): LengthTrustIF => {
        return getLengthTrust.value as LengthTrustIF || null
      }),
      trustIndenture: computed((): boolean => {
        return localState.lengthTrust.trustIndenture
      }),
      trustIndentureSummary: computed((): string => {
        return localState.lengthTrust.trustIndenture ? 'Yes' : 'No'
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      }),
      trustIndentureModified: computed((): boolean => {
        return localState.lengthTrust.trustIndenture !== localState.originalTrustIndenture
      }),
      lienAmountSummary: computed((): string => {
        if (getLengthTrust.value.lienAmount) {
          // Format as CDN currency.
          const currency = getLengthTrust.value.lienAmount
            ?.replace('$', '')
            ?.replaceAll(',', '')
          const lienFloat = parseFloat(currency)
          if (isNaN(lienFloat)) {
            return getLengthTrust.value.lienAmount
          }
          return '$' + lienFloat.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
        }
        return 'Not entered'
      })
    })

    const undoTrustIndenture = (): void => {
      const lt = getLengthTrust.value
      lt.trustIndenture = localState.originalTrustIndenture
      delete lt.action
      setLengthTrust(lt)
    }

    const initEdit = () => {
      localState.editInProgress = true
      localState.showEditTrustIndenture = true
      context.emit('lengthTrustOpen', true)
    }

    const resetEdit = () => {
      localState.editInProgress = false
      localState.showEditTrustIndenture = false
      context.emit('lengthTrustOpen', false)
    }

    onMounted(() => {
      const lt = localState.lengthTrust
      lt.valid = true
      setLengthTrust(lt)
    })

    watch(
      () => localState.trustIndenture,
      (val: boolean) => {
        const lt = localState.lengthTrust
        lt.trustIndenture = val
        setLengthTrust(lt)
      }
    )

    return {
      getLengthTrust,
      APIRegistrationTypes,
      resetEdit,
      initEdit,
      registrationType,
      undoTrustIndenture,
      modal,
      displayHistoricalLienInfo,
      ...toRefs(localState)
    }
  },
  methods: { convertDate }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
</style>
