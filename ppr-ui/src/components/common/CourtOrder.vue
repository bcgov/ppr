<template>
  <v-container flat class="pa-0" id="court-order-summary">
    <v-form v-model="valid">
      <v-row no-gutters>
        <v-col class="generic-label"><h2>Court Order</h2></v-col>
      </v-row>
      <v-row no-gutters class="pb-6 pt-4">
        <v-col>
          If this registration is pursuant to a court order, enter the court
          order information below.
        </v-col>
      </v-row>

      <v-row class="no-gutters">
        <v-col
          cols="12"
          class="pa-0"
          :class="showErrors && !valid ? 'border-error-left' : ''"
        >
          <v-card flat>
            <v-row no-gutters style="padding: 0 30px;">
              <v-col cols="3" class="generic-label pt-10">Court Name</v-col>
              <v-col cols="9" class="pt-8">
                <v-text-field
                  filled
                  id="txt-court-name"
                  label="Court Name"
                  v-model="courtName"
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
                  label="Court Registry"
                  v-model="courtRegistry"
                  persistent-hint
                  :error-messages="
                    errors.courtRegistry.message ? errors.courtRegistry.message : ''
                  "
                />
              </v-col>
            </v-row>
            <v-row no-gutters style="padding: 0 30px;">
              <v-col cols="3" class="generic-label pt-6"
                >Court File Number</v-col
              >
              <v-col cols="9" class="pt-4">
                <v-text-field
                  filled
                  id="txt-court-file-number"
                  label="Court File Number"
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
                      label="Date of Order"
                      append-icon="mdi-calendar"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                      v-on:click:append="on.click"
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
              <v-col cols="3" class="generic-label pt-6"
                >Effect of Order</v-col
              >
              <v-col cols="9" class="pt-4">
                <v-textarea
                  v-model="effectOfOrder"
                  id="effect-of-order"
                  auto-grow
                  counter="4000"
                  filled
                  label="Effect of Order"
                  class="white pt-2 text-input-field"
                  :error-messages="
                    errors.effectOfOrder.message ? errors.effectOfOrder.message : ''
                  "
                />
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>
    </v-form>
  </v-container>
</template>

<script lang="ts">
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
    }
  },
  setup (props, { emit }) {
    const { setCourtOrderInformation } = useActions<any>([
      'setCourtOrderInformation'
    ])
    const { getCourtOrderInformation } = useGetters<any>([
      'getCourtOrderInformation'
    ])
    const {
      errors,
      valid,
      validateCourtOrderForm,
      isValidCourtOrderForm
    } = useCourtOrderValidation()
    const modal = false
    const localState = reactive({
      courtName: '',
      courtRegistry: '',
      fileNumber: '',
      orderDate: '',
      effectOfOrder: '',
      courtOrderInfo: computed((): CourtOrderIF => {
        return getCourtOrderInformation.value as CourtOrderIF
      }),
      computedDateFormatted: computed((): string => {
        if (getCourtOrderInformation.value === null) {
          return ''
        }
        return getCourtOrderInformation.value?.orderDate !== ''
          ? convertDate(
            new Date(
              getCourtOrderInformation.value.orderDate + 'T09:00:00Z'
            ),
            false,
            false
          )
          : ''
      }),
      showErrors: computed((): boolean => {
        if (props.setShowErrors === true) {
          validateCourtOrderForm(localState.courtOrderInfo)
        }
        return props.setShowErrors
      })
    })

    const emitValid = async () => {
      await isValidCourtOrderForm(localState.courtOrderInfo)
      emit('setCourtOrderValid', valid.value)
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
