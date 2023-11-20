<template>
  <div class="mhr-transfer-details">
    <h4 class="header">
      1. Transfer Details{{ isOwnLand }}
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
            <label class="generic-label"
                   for="lease-own-option"
                   :class="{ 'error-text': showFormError }"
                   >
              Land Lease or Ownership
            </label>
          </v-col>
          <v-col cols="9" class="pl-3">
            <p>Is the manufactured home located on land that the
               {{isTransferDueToSaleOrGift ? 'new' : ''}} homeowners own or on land that
               they have a registered lease of 3 years or more?</p>
          </v-col>
        </v-row>
        <v-row class="mt-n1 mb-n5">
          <v-col cols="9" offset="3">
            <v-radio-group
              id="lease-own-option"
              v-model="isOwnLand"
              class="mt-0"
              row
              required
              data-test-id="lease-own-radio"
            >
              <v-radio
                id="yes-option"
                class="yes-radio"
                label="Yes"
                active-class="active-radio"
                :value="true"
                data-test-id="yes-ownership-radiobtn"
              />
              <v-radio
                id="no-option"
                class="no-radio"
                label="No"
                active-class="active-radio"
                :value="false"
                data-test-id="no-ownership-radiobtn"
              />
            </v-radio-group>
          </v-col>
        </v-row>
        <v-row v-if="isOwnLand">
          <v-col cols="9" offset="3">
            <v-divider class="mx-0 divider-mt" />
            <p class="mb-1 paragraph-mt" data-test-id="yes-paragraph">
              <b>Note:</b> Land ownership or registered lease of the land for 3 years or more
              must be verifiable through the BC Land Title and Survey Authority (LTSA)
              or other authorized land authority.
            </p>
          </v-col>
        </v-row>
        <v-row v-if="!isOwnLand && isOwnLand!==null">
          <v-col cols="9" offset="3">
            <v-divider class="mx-0 divider-mt" />
            <p class="mb-1 paragraph-mt" data-test-id="no-paragraph">
              <b>Note:</b> Written permission and tenancy agreements from the landowner
              may be required for the home to remain on the land.
              <br><br>
              Relocation of the home onto land that the homeowner does not own or hold a
              registered lease of 3 years or more may require additional permits from
              authorities such as the applicable Municipality, Regional District, First
              Nation, or Provincial Crown Land Office.
            </p>
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
      isTransferDueToSaleOrGift
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
      isValidTransferDetails: computed(() =>
        localState.isValidForm && !!localState.transferDate && localState.isOwnLand !== null),
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
      setMhrTransferOwnLand(null)
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
      isTransferDueToSaleOrGift,
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

.yes-radio {
  width: 47%;
  margin-right: 20px !important;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 20px;
}

.no-radio {
  width: 50%;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 20px;
  margin-right: 0px !important;
}

.active-radio {
  border: 1px solid $app-blue;
  background-color: white;
  color: #212529 !important;
}

.paragraph-mt{
  margin-top: 39px;
}

.divider-mt{
  margin-top: 13px;
}
}
</style>
