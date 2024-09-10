<template>
  <div class="mhr-transfer-details">
    <h2>
      1. Transfer Details
    </h2>
    <p class="mt-2 mb-7">
      Enter details of the transfer or change of ownership.
    </p>

    <v-card
      flat
      class="py-6 px-8 rounded"
      :class="{ 'border-error-left': showFormError }"
    >
      <v-form
        ref="transferDetailsForm"
        v-model="isValidForm"
      >
        <template v-if="!isTransferDueToDeath && !isTransferWithoutBillOfSale">
          <v-row>
            <v-col cols="3">
              <label
                class="generic-label"
                for="consideration"
                :class="{ 'error-text': showFormError && (!isTransferNonGiftBillOfSale && !consideration) }"
              >
                Consideration
              </label>
            </v-col>
            <v-col cols="9">
              <v-text-field
                id="consideration"
                ref="considerationRef"
                v-model="consideration"
                variant="filled"
                color="primary"
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
                :class="{ 'error-text': showFormError && (!isTransferNonGiftBillOfSale && !transferDate) }"
              >
                Bill of Sale Date of Execution
              </label>
            </v-col>
            <v-col cols="9">
              <InputFieldDatePicker
                id="transfer-date"
                ref="transferDateRef"
                title="Date"
                :errorMsg="showFormError &&
                  (!isTransferNonGiftBillOfSale && !transferDate) ? 'Enter bill of sale date of execution' : ''"
                :initialValue="transferDate"
                :maxDate="isRoleQualifiedSupplier ? localTodayDate(new Date(), true) : null"
                data-test-id="transfer-date"
                @emitDate="transferDate = $event"
                @emitCancel="transferDate = null"
                @emitClear="transferDate = null"
              />
            </v-col>
          </v-row>
          <v-divider class="mx-0 mt-2 mb-7" />
        </template>
        <v-row>
          <v-col cols="3">
            <h4
              class="fs-16 lh-22"
              :class="{ 'error-text': showFormError && isOwnLand === null }"
            >
              Land Lease or Ownership
            </h4>
          </v-col>
          <v-col
            cols="9"
            class="pl-3"
          >
            <p>
              Is the manufactured home located on land that the
              {{ isNewHomeOwner ? 'new' : '' }} homeowners own or on land that
              they have a registered lease of 3 years or more?
            </p>
          </v-col>
        </v-row>
        <v-row class="mb-n5 mt-6">
          <v-col
            cols="9"
            offset="3"
          >
            <v-radio-group
              id="lease-own-option"
              v-model="isOwnLand"
              class="mt-0 mb-5"
              inline
              :rules="isNotNull('')"
              data-test-id="lease-own-radio"
            >
              <v-radio
                id="yes-option"
                class="radio-one"
                label="Yes"
                :class="{'selected-radio': isOwnLand === true}"
                :value="true"
                data-test-id="yes-ownership-radio-btn"
              />
              <v-radio
                id="no-option"
                class="radio-two"
                label="No"
                :class="{'selected-radio': isOwnLand === false}"
                :value="false"
                data-test-id="no-ownership-radio-btn"
              />
            </v-radio-group>

            <div v-if="isOwnLand">
              <v-divider class="" />
              <p
                class="pt-10 pb-5"
                data-test-id="yes-paragraph"
              >
                <b>Note:</b> Land ownership or registered lease of the land for 3 years or more
                must be verifiable through the BC Land Title and Survey Authority (LTSA)
                or other authorized land authority.
              </p>
            </div>

            <div v-if="!isOwnLand && isOwnLand!=null">
              <v-divider class="" />
              <p
                class="pt-10 pb-5"
                data-test-id="no-paragraph"
              >
                <b>Note:</b> Written permission and tenancy agreements from the landowner
                may be required for the home to remain on the land.
                <br><br>
                Relocation of the home onto land that the homeowner does not own or hold a
                registered lease of 3 years or more may require additional permits from
                authorities such as the applicable Municipality, Regional District, First
                Nation, or Provincial Crown Land Office.
              </p>
            </div>
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { useInputRules, useTransferOwners } from '@/composables'
import { InputFieldDatePicker } from '@/components/common'
import { FormIF } from '@/interfaces'
import { storeToRefs } from 'pinia'
import { localTodayDate } from '@/utils'

export default defineComponent({
  name: 'TransferDetails',
  components: { InputFieldDatePicker },
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
  emits: ['isValid'],
  setup (props, context) {
    const { customRules, required, maxLength, isNotNull, isGreaterThanZero } = useInputRules()
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
      getMhrTransferOwnLand,
      isRoleQualifiedSupplier
    } = storeToRefs(useStore())
    const {
      isTransferDueToDeath,
      isTransferBillOfSale,
      isTransferNonGiftBillOfSale,
      isTransferWithoutBillOfSale
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
      isOwnLand: getMhrTransferOwnLand.value,
      enableWarningMsg: false,
      isNewHomeOwner: computed(() =>
        isTransferBillOfSale.value || isTransferWithoutBillOfSale.value
      ),
      isValidTransferDetails: computed((): boolean =>
        (isTransferDueToDeath.value || isTransferWithoutBillOfSale.value || isTransferNonGiftBillOfSale.value)
          ? localState.isValidForm // validate the form without transfer date
          : (localState.isValidForm && !!localState.transferDate)),
      showFormError: computed((): boolean => props.validate && !localState.isValidTransferDetails),
      considerationRules: computed((): Array<()=>string|boolean> => {
        return isTransferNonGiftBillOfSale.value
          ? customRules(maxLength(80), isGreaterThanZero())
          : customRules(required('Enter consideration'), maxLength(80), isGreaterThanZero())
      })
    })

    // Clear the data when hiding Transfer Details (e.g. in Undo)
    const clearTransferDetailsData = () => {
      setMhrTransferConsideration('')
      setMhrTransferDate(null)
      setMhrTransferOwnLand(null)
      context.emit('isValid', false)
    }

    watch(() => props.validate, () => {
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
      localTodayDate,
      isRoleQualifiedSupplier,
      isNotNull,
      considerationRef,
      isTransferDueToDeath,
      isTransferNonGiftBillOfSale,
      isTransferWithoutBillOfSale,
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
:deep(.mhr-transfer-details) {
  margin: 43px 0;

  .generic-label {
    line-height: 24px;
  }

  hr {
    border-top: 1px solid $gray3;
  }

.paragraph-mt{
  margin-top: 39px;
}

.divider-mt{
  margin-top: 13px;
}
}
</style>
