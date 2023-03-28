<template>
  <v-container v-if="renewalView && isSummary" id="court-order-component" class="pa-0">
    <h2 class="pt-2 pb-5">Court Order</h2>
    <v-container class="white" style="padding: 40px 30px;">
      <v-row no-gutters class="pb-7">
            <v-col cols="3" class="generic-label">Court Name</v-col>
            <v-col cols="9" id="court-name-display">{{ courtName }}</v-col>
      </v-row>
      <v-row no-gutters class="pb-7">
            <v-col cols="3" class="generic-label">Court Registry</v-col>
            <v-col cols="9" id="court-registry-display">{{ courtRegistry }}</v-col>
      </v-row>
      <v-row no-gutters class="pb-7">
            <v-col cols="3" class="generic-label">Court File Number</v-col>
            <v-col cols="9" id="file-number-display"> {{ fileNumber }}
            </v-col>
      </v-row>
      <v-row no-gutters class="pb-7">
            <v-col cols="3" class="generic-label">Date of Order</v-col>
            <v-col cols="9" id="date-display">{{ computedDateFormatted }}</v-col>
      </v-row>
      <v-row no-gutters>
            <v-col cols="3" class="generic-label">Effect of Order</v-col>
            <v-col cols="9" id="effect-display"><span style="white-space: pre-wrap">{{ effectOfOrder }}</span></v-col>
      </v-row>
    </v-container>
  </v-container>
  <v-container v-else-if="isSummary">
    <v-row no-gutters class="py-2">
      <v-col cols="auto" class="generic-label">
        <label>
          <strong>Court Order</strong>
        </label>
      </v-col>
    </v-row>
    <v-row no-gutters style="padding: 15px 30px;">
          <v-col class="generic-label">Court Name</v-col>
          <v-col cols="9" id="court-name-display">{{ courtName }}</v-col>
    </v-row>
    <v-row no-gutters style="padding: 15px 30px;">
          <v-col class="generic-label">Court Registry</v-col>
          <v-col cols="9" id="court-registry-display">{{ courtRegistry }}</v-col>
    </v-row>
    <v-row no-gutters style="padding: 15px 30px;">
          <v-col class="generic-label">Court File Number</v-col>
          <v-col cols="9" id="file-number-display"> {{ fileNumber }}
          </v-col>
    </v-row>
    <v-row no-gutters style="padding: 15px 30px;">
          <v-col class="generic-label">Date of Order</v-col>
          <v-col cols="9" id="date-display">{{ computedDateFormatted }}</v-col>
    </v-row>
    <v-row no-gutters style="padding: 15px 30px;">
          <v-col class="generic-label">Effect of Order</v-col>
          <v-col cols="9" id="effect-display"><span style="white-space: pre-wrap">{{ effectOfOrder }}</span></v-col>
    </v-row>
  </v-container>
  <v-container v-else fluid no-gutters class="pb-6  px-0 rounded">
    <v-card
      id="court-order"
      class="rounded"
      :class="showErrors && !valid ? 'border-error-left' : ''"
      flat
    >
    <v-row no-gutters class="summary-header pa-2 mb-8">
      <v-col cols="auto" class="pa-2">
        <v-icon color="darkBlue">mdi-gavel</v-icon>
        <label class="pl-3">
          <strong>Court Order</strong>
        </label>
      </v-col>
    </v-row>
    <v-row no-gutters class="summary-text" style="padding: 0 30px;">
      <v-col v-if="requireCourtOrder && registrationType === APIRegistrationTypes.REPAIRERS_LIEN">
        A court order is required to renew a Repairer's Lien. Enter the court
        order information below. A default Effect of Order is provided; you can
        modify this default text if you wish.
      </v-col>
      <v-col v-else>
        If this registration is pursuant to a court order, enter the court order
        information below, otherwise leave the Court Order information empty.
      </v-col>
    </v-row>
      <v-form v-model="valid">
        <v-row no-gutters style="padding: 0 30px;">
          <v-col cols="3" class="generic-label pt-10">Court Name</v-col>
          <v-col cols="9" class="pt-8">
            <v-text-field
              filled
              id="txt-court-name"
              label="Court Name"
              v-model.trim="courtName"
              hint="For example: Supreme Court of British Columbia"
              persistent-hint
              :error-messages="
                errors.courtName.message ? errors.courtName.message : courtNameMessage
              "
            />
          </v-col>
        </v-row>
        <v-row no-gutters style="padding: 0 30px;">
          <v-col cols="3" class="generic-label pt-6">Court Registry</v-col>
          <v-col cols="9" class="pt-4">
            <v-text-field
              filled
              id="txt-court-registry"
              label="Court Registry"
              v-model.trim="courtRegistry"
              hint="The location (city) of the court. For example: Richmond"
              persistent-hint
              :error-messages="
                errors.courtRegistry.message ? errors.courtRegistry.message : courtRegistryMessage
              "
            />
          </v-col>
        </v-row>
        <v-row no-gutters style="padding: 0 30px;">
          <v-col cols="3" class="generic-label pt-6">Court File Number</v-col>
          <v-col cols="9" class="pt-4">
            <v-text-field
              filled
              id="txt-court-file-number"
              label="Court File Number"
              v-model.trim="fileNumber"
              persistent-hint
              :error-messages="
                errors.fileNumber.message ? errors.fileNumber.message : fileNumberMessage
              "
            />
          </v-col>
        </v-row>
        <v-row no-gutters style="padding: 0 30px;">
          <v-col cols="3" class="generic-label pt-6">Date of Order</v-col>
          <v-col cols="9" class="pt-4">
            <SharedDatePicker
              id="court-date-text-field"
              nudge-right="40"
              ref="datePickerRef"
              title="Date of Order"
              clearable
              :errorMsg="errors.orderDate.message ? errors.orderDate.message : ''"
              :initialValue="orderDate"
              :key="datePickerKey"
              :minDate="minCourtDate"
              :maxDate="maxCourtDate"
              :persistentHint="true"
              @emitDate="orderDate = $event"
              @emitCancel="orderDate = ''"
              @emitClear="orderDate = ''"
            />
          </v-col>
        </v-row>
        <v-row no-gutters style="padding: 0 30px;">
          <v-col cols="3" class="generic-label pt-6">Effect of Order</v-col>
          <v-col cols="9" class="pt-4">
            <v-textarea
              v-model.trim="effectOfOrder"
              id="effect-of-order"
              auto-grow
              counter="512"
              filled
              label="Effect of Order"
              class="white pt-2 text-input-field"
              :error-messages="
                errors.effectOfOrder.message ? errors.effectOfOrder.message : effectOfOrderMessage
              "
            />
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </v-container>
</template>

<script lang="ts">
// external
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  computed,
  onMounted
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { isEqual } from 'lodash'
// bcregistry
import { SharedDatePicker } from '@/components/common/index'
// local
import { APIRegistrationTypes } from '@/enums'
import { CourtOrderIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate, localTodayDate } from '@/utils'
import { useCourtOrderValidation } from './composables'

export default defineComponent({
  components: {
    SharedDatePicker
  },
  props: {
    setShowErrors: {
      default: false
    },
    setRequireCourtOrder: {
      default: false
    },
    setSummary: {
      default: false
    },
    isRenewal: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { setCourtOrderInformation, setUnsavedChanges } = useActions<any>([
      'setCourtOrderInformation', 'setUnsavedChanges'
    ])
    const {
      getCourtOrderInformation, getRegistrationType, getRegistrationCreationDate, hasUnsavedChanges
    } = useGetters<any>([
      'getCourtOrderInformation', 'getRegistrationType', 'getRegistrationCreationDate', 'hasUnsavedChanges'
    ])
    const {
      errors,
      valid,
      validateCourtOrderForm,
      isValidCourtOrderForm,
      resetErrors
    } = useCourtOrderValidation()
    const modal = false
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const localState = reactive({
      renewalView: props.isRenewal,
      courtName: '',
      courtRegistry: '',
      fileNumber: '',
      orderDate: '',
      effectOfOrder: '',
      datePickerKey: Math.random(),
      courtOrderInfo: computed(
        (): CourtOrderIF => {
          return getCourtOrderInformation.value as CourtOrderIF
        }
      ),
      computedDateFormatted: computed((): string => {
        if (getCourtOrderInformation.value === null) {
          return ''
        }
        return getCourtOrderInformation.value?.orderDate !== ''
          ? convertDate(
            new Date(getCourtOrderInformation.value.orderDate + 'T09:00:00Z'),
            false,
            false
          )
          : ''
      }),
      requireCourtOrder: computed((): boolean => {
        return props.setRequireCourtOrder
      }),
      isSummary: computed((): boolean => {
        return props.setSummary
      }),
      showErrors: computed((): boolean => {
        if ((props.setShowErrors === true) && (shouldValidate())) {
          validateCourtOrderForm(localState.courtOrderInfo)
        }
        return props.setShowErrors
      }),
      minCourtDate: computed((): string => {
        if (registrationType === APIRegistrationTypes.REPAIRERS_LIEN) {
          const minDate = new Date(getRegistrationCreationDate.value)
          return localTodayDate(minDate)
        } else {
          return '0'
        }
      }),
      maxCourtDate: computed((): string => {
        const maxDate = localTodayDate()
        return maxDate
      }),
      fileNumberMessage: computed((): string => {
        if (localState.fileNumber.length > 20) {
          return 'Maximum 20 characters'
        }
        return ''
      }),
      courtNameMessage: computed((): string => {
        if (localState.courtName.length > 256) {
          return 'Maximum 256 characters'
        }
        return ''
      }),
      courtRegistryMessage: computed((): string => {
        if (localState.courtRegistry.length > 64) {
          return 'Maximum 64 characters'
        }
        return ''
      }),
      effectOfOrderMessage: computed((): string => {
        if (localState.effectOfOrder.length > 512) {
          return 'Maximum 512 characters'
        }
        return ''
      })
    })

    const emitValid = async () => {
      if (!shouldValidate()) {
        resetErrors()
        emit('setCourtOrderValid', valid.value)
      } else {
        await isValidCourtOrderForm(localState.courtOrderInfo)
        emit('setCourtOrderValid', valid.value)
      }
    }

    const shouldValidate = () => {
      if ((localState.courtName) || (localState.courtRegistry) ||
          (localState.fileNumber) || (localState.orderDate) || (localState.effectOfOrder) ||
          (localState.requireCourtOrder)) {
        return true
      }
      return false
    }

    watch(
      () => localState.courtName,
      (val: string) => {
        const newCourtOrderInfo = localState.courtOrderInfo
        newCourtOrderInfo.courtName = val
        setCourtOrderInformation(newCourtOrderInfo)
        emitValid()
      }
    )

    watch(
      () => localState.fileNumber,
      (val: string) => {
        const newCourtOrderInfo = localState.courtOrderInfo
        newCourtOrderInfo.fileNumber = val
        setCourtOrderInformation(newCourtOrderInfo)
        emitValid()
      }
    )

    watch(
      () => localState.courtRegistry,
      (val: string) => {
        const newCourtOrderInfo = localState.courtOrderInfo
        newCourtOrderInfo.courtRegistry = val
        setCourtOrderInformation(newCourtOrderInfo)
        emitValid()
      }
    )

    watch(
      () => localState.orderDate,
      (val: string) => {
        const newCourtOrderInfo = localState.courtOrderInfo
        newCourtOrderInfo.orderDate = val
        // date cannot be in the future

        setCourtOrderInformation(newCourtOrderInfo)
        emitValid()
      }
    )

    watch(
      () => localState.effectOfOrder,
      (val: string) => {
        const newCourtOrderInfo = localState.courtOrderInfo
        newCourtOrderInfo.effectOfOrder = val
        setCourtOrderInformation(newCourtOrderInfo)
        emitValid()
      }
    )

    onMounted(() => {
      const blankCourtOrder: CourtOrderIF = {
        courtName: '',
        courtRegistry: '',
        effectOfOrder: '',
        fileNumber: '',
        orderDate: ''
      }
      if (isEqual(localState.courtOrderInfo, blankCourtOrder)) {
        if (localState.requireCourtOrder && registrationType === APIRegistrationTypes.REPAIRERS_LIEN) {
          localState.effectOfOrder = 'Order directs the effective period of the Repairer\'s Lien be extended' +
                                      ' an additional 180 days.'
        }
      } else {
        // get unsavedChanges to reset it after court order setup
        const unsavedChanges = hasUnsavedChanges.value as Boolean
        if (localState.courtOrderInfo.orderDate?.length > 10) {
          // convert back to local iso date string
          const orderDate = new Date(localState.courtOrderInfo.orderDate)
          localState.orderDate = localTodayDate(orderDate)
        } else {
          localState.orderDate = localState.courtOrderInfo.orderDate
        }
        localState.effectOfOrder = localState.courtOrderInfo.effectOfOrder
        localState.courtName = localState.courtOrderInfo.courtName
        localState.courtRegistry = localState.courtOrderInfo.courtRegistry
        localState.fileNumber = localState.courtOrderInfo.fileNumber
        // rerender date-picker
        localState.datePickerKey = Math.random()
        // reset unsaved changes to what it was before setting up court order
        setTimeout(() => {
          setUnsavedChanges(unsavedChanges)
        }, 100)
      }
    })

    return {
      modal,
      errors,
      valid,
      registrationType,
      APIRegistrationTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
