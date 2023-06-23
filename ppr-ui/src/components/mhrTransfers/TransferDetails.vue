<template>
  <div class="mhr-transfer-details">
    <h4 class="header">
      1. Transfer Details
    </h4>
    <p class="mt-2 mb-7">
      Enter details of the transfer or change of ownership.
    </p>

    <v-card flat class="py-6 px-8 rounded" :class="{ 'border-error-left': showFormError }">
      <v-form ref="transferDetailsForm" v-model="isValidForm">
        <template v-if="!isTransferDueToDeath">
          <v-row>
            <v-col cols="3">
              <label
                class="generic-label"
                for="consideration"
                :class="{ 'error-text': showFormError && hasError(considerationRef) }"
              >
                Consideration
              </label>
            </v-col>
            <v-col cols="9">
              <v-text-field
                id="consideration"
                v-model="consideration"
                ref="considerationRef"
                filled
                :rules="considerationRules"
                label="Amount in Canadian Dollars or Description"
                data-test-id="consideration"
                @mousedown="updateConsideration()"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="3">
              <label
                class="generic-label"
                for="transfer-date"
                :class="{ 'error-text': showFormError && !transferDate }"
              >
                Bill of Sale Date of Execution
              </label>
            </v-col>
            <v-col cols="9">
              <SharedDatePicker
                id="transfer-date"
                clearable
                ref="transferDateRef"
                title="Date"
                :errorMsg="showFormError && !transferDate ? 'Enter bill of sale date of execution' : ''"
                :initialValue="transferDate"
                :key="Math.random()"
                @emitDate="transferDate = $event"
                @emitCancel="transferDate = null"
                @emitClear="transferDate = null"
                data-test-id="transfer-date"
              />
            </v-col>
          </v-row>
          <v-divider class="mx-0 mt-2 mb-7" />
        </template>
        <v-row>
          <v-col cols="3">
            <label class="generic-label" for="lease-own">
              Land Lease or Ownership
            </label>
          </v-col>
          <v-col cols="9" class="pl-1">
            <v-checkbox
              id="lease-own"
              :label="landOrLeaseLabel"
              v-model="isOwnLand"
              class="mt-0 pt-0 lease-own-checkbox"
              data-test-id="lease-own-checkbox"
            />
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { useStore } from '@/store/store'
import { useInputRules, useTransferOwners } from '@/composables'
import { SharedDatePicker } from '@/components/common'
import { FormIF } from '@/interfaces'
import { storeToRefs } from 'pinia' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'TransferDetails',
  emits: ['isValid'],
  components: { SharedDatePicker },
  props: {
    validate: {
      type: Boolean,
      default: false
    },
    disablePrefill: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { customRules, required, maxLength } = useInputRules()
    const {
      // Actions
      setMhrTransferConsideration,
      setMhrTransferDate,
      setMhrTransferOwnLand,
      setUnsavedChanges
    } = useStore()
    const {
      // Getters
      getMhrTransferDeclaredValue,
      getMhrTransferConsideration,
      getMhrTransferDate,
      getMhrTransferOwnLand
    } = storeToRefs(useStore())
    const {
      isTransferDueToDeath,
      isTransferToExecutorProbateWill
    } = useTransferOwners()

    const transferDetailsForm = ref(null) as FormIF
    const considerationRef = ref(null)

    const updateConsideration = () => {
      if (props.disablePrefill) return
      // copy Declared Value into Consideration field - the initial time only
      if (!localState.consideration && getMhrTransferDeclaredValue.value) {
        localState.consideration = `$${getMhrTransferDeclaredValue.value}.00`
      }
    }

    const localState = reactive({
      isValidForm: false, // TransferDetails form without Transfer Date Picker
      consideration: getMhrTransferConsideration.value,
      transferDate: getMhrTransferDate.value,
      isOwnLand: getMhrTransferOwnLand.value || false,
      enableWarningMsg: false,
      landOrLeaseLabel: computed(() => {
        return `The manufactured home is located on land that the ${!isTransferDueToDeath.value ||
            isTransferToExecutorProbateWill.value ? 'new' : ''} homeowners
         own, or on which they have a registered lease of 3 years or more.`
      }),
      isValidTransferDetails: computed(() => localState.isValidForm && !!localState.transferDate),
      showFormError: computed(() => props.validate && !localState.isValidTransferDetails),
      considerationRules: computed((): Array<Function> => {
        return customRules(required('Enter consideration'), maxLength(80))
      })
    })

    const hasError = (ref: any): boolean => {
      return ref?.hasError
    }

    // Clear the data when hiding Transfer Details (e.g. in Undo)
    const clearTransferDetailsData = () => {
      setMhrTransferConsideration('')
      setMhrTransferDate(null)
      setMhrTransferOwnLand(false)
    }

    watch(() => props.validate, (val: boolean) => {
      transferDetailsForm.value?.validate()
    })

    watch(() => localState.consideration, (val: string) => {
      setMhrTransferConsideration(val)
      setUnsavedChanges(true)
    })

    watch(() => localState.transferDate, (val: string) => {
      setMhrTransferDate(val)
      setUnsavedChanges(true)
    })

    watch(() => localState.isOwnLand, (val: boolean) => {
      setMhrTransferOwnLand(val)
      setUnsavedChanges(true)
    })

    watch(() => localState.isValidTransferDetails, (val: boolean) => {
      context.emit('isValid', val)
    })

    return {
      hasError,
      considerationRef,
      isTransferDueToDeath,
      transferDetailsForm,
      updateConsideration,
      clearTransferDetailsData,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.mhr-transfer-details::v-deep {
  margin: 43px 0;

  .generic-label {
    line-height: 24px;
  }

  hr {
    border-top: 1px solid $gray3;
  }

  .lease-own-checkbox {
    label {
      line-height: 24px;
    }
    .v-input__slot {
      align-items: flex-start;
    }
  }
}
</style>
