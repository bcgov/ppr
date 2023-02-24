<template>
  <div class="mhr-transfer-details">
    <h4 class="header">
      1. Transfer Details
    </h4>
    <p class="mt-2 mb-7">
      Enter details of the transfer or change of ownership.
    </p>

    <v-card flat class="py-6 px-8 rounded" :class="{ 'border-error-left': showFormError }">
      <v-form ref="transferDetailsForm" v-model="isFormValid">
        <v-row>
          <v-col cols="3">
            <label
              class="generic-label"
              for="consideration"
              :class="{ 'error-text': validateTransferDetails && hasError(considerationRef) }"
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
              :class="{ 'error-text': validateTransferDetails && !transferDate }"
            >
              Bill of Sale Date of Execution
            </label>
          </v-col>
          <v-col cols="9">
            <date-picker
              id="transfer-date"
              clearable
              ref="transferDateRef"
              title="Date"
              :errorMsg="validateTransferDetails && !transferDate ? 'Enter bill of sale date of execution' : ''"
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
        <v-row>
          <v-col cols="3">
            <label class="generic-label" for="lease-own">
              Land Lease or Ownership
            </label>
          </v-col>
          <v-col cols="9">
            <v-checkbox
              id="lease-own"
              label="The manufactured home is located on land that the new homeowners own,
                or on which they have a registered lease of 3 years or more."
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
import { DatePicker } from '@bcrs-shared-components/date-picker'
import { useInputRules } from '@/composables'
import { computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { useActions, useGetters } from 'vuex-composition-helpers'
import { FormIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'TransferDetails',
  emits: ['isValid'],
  components: { DatePicker },
  setup (props, context) {
    const { customRules, required, maxLength } = useInputRules()

    const {
      getMhrTransferDeclaredValue,
      getMhrTransferConsideration,
      getMhrTransferDate,
      getMhrTransferOwnLand
    } = useGetters<any>([
      'getMhrTransferDeclaredValue',
      'getMhrTransferConsideration',
      'getMhrTransferDate',
      'getMhrTransferOwnLand'
    ])

    const {
      setMhrTransferConsideration,
      setMhrTransferDate,
      setMhrTransferOwnLand,
      setUnsavedChanges
    } = useActions([
      'setMhrTransferConsideration',
      'setMhrTransferDate',
      'setMhrTransferOwnLand',
      'setUnsavedChanges'
    ])

    const considerationRef = ref(null)

    const considerationRules = computed(
      (): Array<Function> => customRules(maxLength(80), required('Enter consideration'))
    )

    const updateConsideration = () => {
      // copy Declared Value into Consideration field - the initial time only
      if (!localState.consideration && getMhrTransferDeclaredValue.value) {
        localState.consideration = `$${getMhrTransferDeclaredValue.value}.00`
      }
    }

    const localState = reactive({
      validateTransferDetails: false, // triggered once Review & Confirm clicked
      isFormValid: false, // TransferDetails form without Transfer Date Picker
      isTransferDetailsFormValid: computed((): boolean => localState.isFormValid && !!localState.transferDate),
      consideration: getMhrTransferConsideration.value,
      transferDate: getMhrTransferDate.value,
      isOwnLand: getMhrTransferOwnLand.value || false,
      enableWarningMsg: false,
      showFormError: computed(() => localState.validateTransferDetails && !localState.isTransferDetailsFormValid)
    })

    const hasError = (ref: any): boolean => {
      return ref?.hasError
    }

    // This validate function is called from parent MhrInformation component
    const validateDetailsForm = (): void => {
      localState.validateTransferDetails = true;
      (context.refs.transferDetailsForm as FormIF).validate()
    }

    // Clear the data when hiding Transfer Details (e.g. in Undo)
    const clearTransferDetailsData = () => {
      setMhrTransferConsideration('')
      setMhrTransferDate(null)
      setMhrTransferOwnLand(false)
    }

    watch(
      () => localState.consideration,
      (val: string) => {
        setMhrTransferConsideration(val)
        setUnsavedChanges(true)
      }
    )

    watch(
      () => localState.transferDate,
      (val: string) => {
        setMhrTransferDate(val)
        setUnsavedChanges(true)
      }
    )

    watch(
      () => localState.isOwnLand,
      (val: boolean) => {
        setMhrTransferOwnLand(val)
        setUnsavedChanges(true)
      }
    )

    watch(
      () => localState.isTransferDetailsFormValid,
      (val: boolean) => {
        context.emit('isValid', val)
      }
    )

    return {
      hasError,
      considerationRef,
      considerationRules,
      updateConsideration,
      validateDetailsForm,
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
