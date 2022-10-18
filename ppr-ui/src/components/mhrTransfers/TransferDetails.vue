<template>
  <div class="mhr-transfer-details">
    <h4 class="header">
      1. Transfer Details
    </h4>
    <p class="mt-2 mb-7">
      Enter details of the transfer of ownership due to sale.
    </p>

    <v-card flat class="py-6 px-8 rounded" :class="{ 'border-error-left': showFormError }">
      <v-form ref="transferDetailsForm" v-model="transferDetailsValid">
        <v-row>
          <v-col cols="3">
            <label class="generic-label" for="declared-value" :class="{ 'error-text': showFormError }">
              Declared Value of Home
            </label>
          </v-col>
          <v-col cols="9" class="declared-value-container">
            <span class="mt-4 mr-3">$</span>
            <v-text-field
              id="declared-value"
              class="declared-value"
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
                updateCompensation($event.target.value), $refs.declaredValueRef.validate(), (enableWarningMsg = true)
              "
              @focus="enableWarningMsg = false"
              data-test-id="declared-value"
            />
            <span class="mt-4 ml-3">.00</span>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="3">
            <label class="generic-label" for="consideration" :class="{ 'error-text': showFormError }">
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
            <label class="generic-label" for="transfer-date" :class="{ 'error-text': showFormError }">
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
              @emitCancel="transferDate = ''"
              @emitClear="transferDate = ''"
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
import { useInputRules, useMhrInformation } from '@/composables'
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useActions } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'TransferDetails',
  components: { DatePicker },
  props: {
    validateTransferDetails: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { customRules, required, isNumber, maxLength } = useInputRules()

    const {
      setMhrTransferDeclaredValue,
      setMhrTransferConsideration,
      setMhrTransferDate,
      setMhrTransferOwnLand
    } = useActions([
      'setMhrTransferDeclaredValue',
      'setMhrTransferConsideration',
      'setMhrTransferDate',
      'setMhrTransferOwnLand'
    ])

    const { setTransferDetailsValid } = useMhrInformation()

    const declaredValueRules = computed(
      (): Array<Function> =>
        customRules(
          maxLength(7, true),
          isNumber(),
          props.validateTransferDetails ? required('Enter declared value of home') : []
        )
    )

    const considerationRules = computed(
      (): Array<Function> =>
        customRules(maxLength(80), props.validateTransferDetails ? required('Enter consideration') : [])
    )

    const updateCompensation = (declaredValue: any) => {
      // copy Declared Value into Consideration field - the initial time only
      if (!localState.consideration && localState.declaredValue && parseInt(declaredValue)) {
        localState.consideration = `$${declaredValue}.00`
      }
    }

    const localState = reactive({
      transferDetailsValid: false,
      declaredValue: null,
      consideration: null,
      transferDate: null,
      isOwnLand: false,
      enableWarningMsg: false,
      showFormError: computed(() => props.validateTransferDetails && !localState.transferDetailsValid)
    })

    watch(
      () => localState.declaredValue,
      async (val: any) => {
        await setMhrTransferDeclaredValue(parseInt(val) ? parseInt(val) : null)
      }
    )

    watch(
      () => localState.consideration,
      (val: string) => {
        setMhrTransferConsideration(val)
      }
    )

    watch(
      () => localState.transferDate,
      (val: string) => {
        setMhrTransferDate(val)
      }
    )

    watch(
      () => localState.isOwnLand,
      (val: boolean) => {
        setMhrTransferOwnLand(val)
      }
    )

    watch(
      () => localState.transferDetailsValid,
      (isFormValid: boolean) => {
        setTransferDetailsValid(isFormValid)
      }
    )

    watch(
      () => props.validateTransferDetails,
      () => {
        // @ts-ignore - function exists
        context.refs.transferDetailsForm.validate()
      }
    )

    return {
      declaredValueRules,
      considerationRules,
      updateCompensation,
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
      .v-messages__message {
        color: $gray7;
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
