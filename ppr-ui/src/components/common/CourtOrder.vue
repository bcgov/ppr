<template>
  <v-container fluid no-gutters class="pb-6  px-0 rounded">
    <v-row no-gutters class="summary-header pa-2 mb-8">
      <v-col cols="auto" class="pa-2">
        <v-icon color="darkBlue">mdi-message-text</v-icon>
        <label class="pl-3">
          <strong>Court Order</strong>
        </label>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-6">
      <v-col>
        If this registration is pursuant to a court order, enter the court order
        information below, otherwise leave the Court Order information empty.
      </v-col>
    </v-row>
    <v-card
      id="court-order"
      :class="showErrors && !valid ? 'border-error-left' : ''"
      flat
    >
      <v-form v-model="valid">
        <v-row no-gutters style="padding: 0 30px;">
          <v-col cols="3" class="generic-label pt-10">Court Name</v-col>
          <v-col cols="9" class="pt-8">
            <v-text-field
              filled
              id="txt-court-name"
              label="Enter the court name"
              v-model="courtName"
              hint="For example: Supreme Court of British Columbia"
              persistent-hint
              :error-messages="
                errors.courtName.message ? errors.courtName.message : ''
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
              label="Enter the court registry"
              v-model="courtRegistry"
              hint="The location (city) of the court. For example: Richmond"
              persistent-hint
              :error-messages="
                errors.courtRegistry.message ? errors.courtRegistry.message : ''
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
              label="Enter the court file number"
              v-model="fileNumber"
              persistent-hint
              :error-messages="
                errors.fileNumber.message ? errors.fileNumber.message : ''
              "
            />
          </v-col>
        </v-row>
        <v-row no-gutters style="padding: 0 30px;">
          <v-col cols="3" class="generic-label pt-6">Date of Order</v-col>
          <v-col cols="9" class="pt-4">
            <v-dialog
              ref="dialog"
              v-model="modal"
              :return-value.sync="orderDate"
              persistent
              width="450px"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-text-field
                  id="court-date-text-field"
                  :value="computedDateFormatted"
                  filled
                  persistent-hint
                  label="Select the date of the order"
                  append-icon="mdi-calendar"
                  clearable
                  v-bind="attrs"
                  v-on="on"
                  v-on:click:append="on.click"
                  @click:clear="orderDate = ''"
                  :error-messages="
                    errors.orderDate.message ? errors.orderDate.message : ''
                  "
                >
                </v-text-field>
              </template>
              <v-date-picker
                id="court-date-picker-calendar"
                v-model="orderDate"
                elevation="15"
                scrollable
                :min="minCourtDate"
                :max="maxCourtDate"
                width="450px"
              >
                <v-spacer></v-spacer>
                <v-btn
                  text
                  color="primary"
                  @click="$refs.dialog.save(orderDate)"
                >
                  <strong>OK</strong>
                </v-btn>
                <v-btn text color="primary" @click="modal = false">
                  Cancel
                </v-btn>
              </v-date-picker>
            </v-dialog>
          </v-col>
        </v-row>
        <v-row no-gutters style="padding: 0 30px;">
          <v-col cols="3" class="generic-label pt-6">Effect of Order</v-col>
          <v-col cols="9" class="pt-4">
            <v-textarea
              v-model="effectOfOrder"
              id="effect-of-order"
              auto-grow
              counter="512"
              filled
              label="Enter the effect of order"
              class="white pt-2 text-input-field"
              :error-messages="
                errors.effectOfOrder.message ? errors.effectOfOrder.message : ''
              "
            />
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { APIRegistrationTypes } from '@/enums'
import { CourtOrderIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate } from '@/utils'
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  computed,
  onMounted
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { useCourtOrderValidation } from './composables'

export default defineComponent({
  props: {
    setShowErrors: {
      default: false
    },
    setRequireCourtOrder: {
      default: false
    }
  },
  setup (props, { emit }) {
    const { setCourtOrderInformation } = useActions<any>([
      'setCourtOrderInformation'
    ])
    const { getCourtOrderInformation, getRegistrationType, getRegistrationCreationDate } = useGetters<any>([
      'getCourtOrderInformation', 'getRegistrationType', 'getRegistrationCreationDate'
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
      courtName: '',
      courtRegistry: '',
      fileNumber: '',
      orderDate: '',
      effectOfOrder: '',
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
      showErrors: computed((): boolean => {
        if ((props.setShowErrors === true) && (shouldValidate())) {
          validateCourtOrderForm(localState.courtOrderInfo)
        }
        return props.setShowErrors
      }),
      minCourtDate: computed((): string => {
        if (registrationType === APIRegistrationTypes.REPAIRERS_LIEN) {
          var minDate = new Date(getRegistrationCreationDate.value)
          return minDate.toISOString()
        } else {
          return '0'
        }
      }),
      maxCourtDate: computed((): string => {
        var maxDate = new Date()
        return maxDate.toISOString()
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
      // initialize to blanks
      if (localState.courtOrderInfo === null) {
        const newCourtOrderInfo = {
          orderDate: '',
          effectOfOrder: '',
          courtName: '',
          courtRegistry: '',
          fileNumber: ''
        }
        if (registrationType === APIRegistrationTypes.REPAIRERS_LIEN) {
          localState.effectOfOrder = 'Order directs the effective life of the Repairer\'s Lien be extended' +
                                      ' an additional 180 days'
        }
        setCourtOrderInformation(newCourtOrderInfo)
      } else {
        localState.orderDate = localState.courtOrderInfo.orderDate
        localState.effectOfOrder = localState.courtOrderInfo.effectOfOrder
        localState.courtName = localState.courtOrderInfo.courtName
        localState.courtRegistry = localState.courtOrderInfo.courtRegistry
        localState.fileNumber = localState.courtOrderInfo.fileNumber
      }
    })

    return {
      modal,
      errors,
      valid,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
