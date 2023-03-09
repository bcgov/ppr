<template>
  <div class="mhr-death-certificate">
    <v-card flat class="pl-8 rounded" :class="{ 'border-error-left': showFormError }">
      <v-form ref="deathCertificateForm" v-model="isFormValid">
        <v-row>
          <v-col cols="3">
            <label
              class="generic-label"
              for="deathCertificate"
              :class="{ 'error-text': validateTransferDetails && hasError(deathCertificateRef) }"
            >
              Death Certificate Number
            </label>
          </v-col>
          <v-col cols="9">
            <v-text-field
              id="deathCertificate"
              v-model="deathCertificate"
              ref="deathCertificateRef"
              filled
              :rules="deathCertificateRules"
              label="Death Certificate Number"
              data-test-id="deathCertificate"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="3">
            <label
              class="generic-label"
              for="transfer-date"
              :class="{ 'error-text': validateTransferDetails && !deathCertificateDate }"
            >
              Date of Death Certificate
            </label>
          </v-col>
          <v-col cols="9">
            <date-picker
              id="death-certificate-date"
              clearable
              ref="deathCertificateDateRef"
              title="Date of Death Certificate"
              :errorMsg="validateTransferDetails && !deathCertificateDate ? 'Enter date of death certificate' : ''"
              :initialValue="deathCertificateDate"
              :key="Math.random()"
              :maxDate="localTodayDate(maxDeathDate)"
              @emitDate="deathCertificateDate = $event"
              @emitCancel="deathCertificateDate = null"
              @emitClear="deathCertificateDate = null"
              data-test-id="death-certificate-date"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-spacer></v-spacer>
          <v-col cols="9">
            <v-checkbox
              id="has-certificate"
              label="I have an original or certified copy of the death certificate, and confirm
              that it was issued from Canada or the United States, and the name on
              the death certificate matches the name displayed above exactly."
              v-model="hasCertificate"
              class="mt-0 pt-0 has-certificate-checkbox"
              data-test-id="has-certificate-checkbox"
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
import { useActions } from 'vuex-composition-helpers'
import { FormIF, MhrRegistrationHomeOwnerIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { localTodayDate } from '@/utils'
// import { useHomeOwners } from '@/composables/mhrRegistration'

export default defineComponent({
  name: 'DeathCertificate',
  emits: ['isValid'],
  props: {
    homeOwner: {
      type: Object as () => MhrRegistrationHomeOwnerIF,
      default: null
    }
  },
  components: { DatePicker },
  setup (props, context) {
    const { customRules, required, maxLength } = useInputRules()

    const {
      setUnsavedChanges
    } = useActions([
      'setUnsavedChanges'
    ])

    const deathCertificateRef = ref(null)

    const deathCertificateRules = computed(
      (): Array<Function> => customRules(maxLength(20), required('Enter Death Certificate Number'))
    )

    const localState = reactive({
      validateDeathCertificate: false, // NEW VALIDATOR REQUIRED
      isFormValid: false, // Death Certificate form without Death Date Picker
      isDeathCertificateFormValid: computed((): boolean => localState.isFormValid && !!localState.deathCertificateDate),
      deathCertificate: null,
      deathCertificateDate: null,
      hasCertificate: false, // Will be used for validation on UI side only (original certificate checkbox)
      deceasedOwner: props.homeOwner,
      showFormError: computed(() => localState.validateTransferDetails && !localState.isDeathCertificateFormValid),
      maxDeathDate: computed((): Date => {
        var dateOffset = 24 * 60 * 60 * 1000 // 1 day in milliseconds
        var maxDate = new Date()
        maxDate.setTime(maxDate.getTime() - dateOffset)
        return maxDate
      })
    })

    const hasError = (ref: any): boolean => {
      return ref?.hasError
    }

    // Need function to validate

    // Need function to clear data on undo/cancel

    // Update deceased owner deathCertificateNumber when value changes
    watch(
      () => localState.deathCertificate,
      (val: number) => {
        localState.deceasedOwner.deathCertificateNumber = val
        setUnsavedChanges(true)
      }
    )

    // Update deceased owner deathDateTime when value changes
    watch(
      () => localState.deathCertificateDate,
      (val: string) => {
        localState.deceasedOwner.deathDateTime = val
        setUnsavedChanges(true)
      }
    )

    watch(
      () => localState.isDeathCertificateFormValid,
      (val: boolean) => {
        context.emit('isValid', val)
      }
    )

    return {
      hasError,
      deathCertificateRef,
      deathCertificateRules,
      localTodayDate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.row {
  height: 90px;
}
.mhr-death-certificate::v-deep {
  margin: 43px 0;

  .generic-label {
    line-height: 24px;
  }

  hr {
    border-top: 1px solid $gray3;
  }

  .has-certificate-checkbox {
    label {
      line-height: 24px;
    }
    .v-input__slot {
      align-items: flex-start;
    }
  }
}
</style>
