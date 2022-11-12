<template>
  <div class="mhr-transfer-details">
    <h4 class="header">
      1. Transfer Details
    </h4>
    <p class="mt-2 mb-7">
      Enter details of the transfer of ownership due to sale.
    </p>

    <v-card flat class="py-6 px-8 rounded" :class="{ 'border-error-left': showFormError }">
      <v-form ref="transferDetailsForm" v-model="isFromValid">
        <v-row>
          <v-col cols="3">
            <label
              class="generic-label"
              for="declared-value"
              :class="{ 'error-text': validateTransferDetails && hasError(declaredValueRef) }"
            >
              Declared Value of Home
            </label>
          </v-col>
          <v-col cols="9" class="declared-value-container">
            <span class="mt-4 mr-3">$</span>
            <v-text-field
              id="declared-value"
              class="declared-value"
              :class="enableWarningMsg ? 'red-error' : 'warning-msg'"
              ref="declaredValueRef"
              v-model="declaredValue"
              filled
              :rules="declaredValueRules"
              :messages="
                enableWarningMsg && declaredValue && declaredValue < 500
                  ? 'The declared value entered appears to be low. Confirm this is the correct market value.'
                  : null
              "
              label="Amount in Canadian Dollars"
              @blur="
                updateConsideration($event.target.value), $refs.declaredValueRef.validate(), (enableWarningMsg = true)
              "
              @focus="enableWarningMsg = false"
              data-test-id="declared-value"
            />
            <span class="mt-4 ml-3">.00</span>
          </v-col>
        </v-row>
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
  components: { DatePicker },
  setup (props, context) {
    const { customRules, required, isNumber, maxLength } = useInputRules()

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
      setMhrTransferDeclaredValue,
      setMhrTransferConsideration,
      setMhrTransferDate,
      setMhrTransferOwnLand,
      setUnsavedChanges
    } = useActions([
      'setMhrTransferDeclaredValue',
      'setMhrTransferConsideration',
      'setMhrTransferDate',
      'setMhrTransferOwnLand',
      'setUnsavedChanges'
    ])

    const declaredValueRef = ref(null)
    const considerationRef = ref(null)

    const declaredValueRules = computed(
      (): Array<Function> => customRules(maxLength(7, true), isNumber(), required('Enter declared value of home'))
    )

    const considerationRules = computed(
      (): Array<Function> => customRules(maxLength(80), required('Enter consideration'))
    )

    const updateConsideration = (declaredValue: string) => {
      // copy Declared Value into Consideration field - the initial time only
      if (!localState.consideration && localState.declaredValue && parseInt(declaredValue)) {
        localState.consideration = `$${declaredValue}.00`
      }
    }

    const localState = reactive({
      validateTransferDetails: false, // triggered once Review & Confirm clicked
      isFromValid: false, // TransferDetails form without Transfer Date Picker
      isTransferDetailsFormValid: computed((): boolean => localState.isFromValid && !!localState.transferDate),
      declaredValue: getMhrTransferDeclaredValue.value?.toString(),
      consideration: getMhrTransferConsideration.value,
      transferDate: getMhrTransferDate.value,
      isOwnLand: getMhrTransferOwnLand.value,
      enableWarningMsg: false,
      showFormError: computed(() => localState.validateTransferDetails && !localState.isTransferDetailsFormValid)
    })

    const hasError = (ref: any): boolean => {
      return ref?.hasError
    }

    // This validate function is called from parent MhrInformation component
    const validateDetailsForm = async (): Promise<boolean> => {
      localState.validateTransferDetails = true
      await (context.refs.transferDetailsForm as FormIF).validate()
      return localState.isTransferDetailsFormValid
    }

    watch(
      () => localState.declaredValue,
      async (val: string) => {
        await setMhrTransferDeclaredValue(parseInt(val) ? parseInt(val) : null)
        setUnsavedChanges(true)
      }
    )

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

    return {
      hasError,
      declaredValueRef,
      considerationRef,
      declaredValueRules,
      considerationRules,
      updateConsideration,
      validateDetailsForm,
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
  .declared-value-container {
    display: flex;

    .declared-value {
      .warning-msg > .v-messages__message {
        color: $gray7;
      }
      .red-error > .v-messages__message {
        color: red;
      }
    }
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
