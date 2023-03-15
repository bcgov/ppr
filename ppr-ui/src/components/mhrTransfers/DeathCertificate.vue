<template>
    <v-card
      id="death-certificate"
      flat
      class="pl-8 rounded death-certificate"
      :class="{ 'border-error-left': showFormError }"
      >
      <v-form ref="deathCertificateForm" v-model="isFormValid">
        <v-row>
          <v-col cols="3">
            <label
              class="generic-label"
              for="deathCertificateNumber"
              :class="{ 'error-text': validateDeathCertificate && hasError(deathCertificateNumberRef) }"
            >
              Death Certificate Registration Number
            </label>
          </v-col>
          <v-col cols="9">
            <v-text-field
              id="death-certificate-number"
              v-model="deathCertificateNumber"
              ref="deathCertificateNumberRef"
              filled
              :rules="deathCertificateNumberRules"
              label="Death Certificate Registration Number"
              data-test-id="death-certificate-number"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="3">
            <label
              class="generic-label"
              for="death-date-time"
              :class="{ 'error-text': validateDeathCertificate && !deathDateTime }"
            >
              Date of Death
            </label>
          </v-col>
          <v-col cols="9">
            <date-picker
              id="death-date-time"
              clearable
              ref="deathDateTimeRef"
              title="Date of Death"
              :errorMsg="validateDeathCertificate && !deathDateTime ? 'Enter date of death' : ''"
              :initialValue="deathDateTime"
              :key="Math.random()"
              :maxDate="localTodayDate(maxDeathDate)"
              @emitDate="deathDateTime = $event"
              @emitCancel="deathDateTime = null"
              @emitClear="deathDateTime = null"
              data-test-id="death-date-time"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-spacer></v-spacer>
          <v-col cols="9">
            <v-checkbox
              id="has-certificate-checkbox"
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
</template>

<script lang="ts">
import { DatePicker } from '@bcrs-shared-components/date-picker'
import { useInputRules, useHomeOwners } from '@/composables'
import { computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { useActions } from 'vuex-composition-helpers'
import { FormIF, MhrRegistrationHomeOwnerIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { localTodayDate } from '@/utils'

export default defineComponent({
  name: 'DeathCertificate',
  props: {
    deceasedOwner: {
      type: Object as () => MhrRegistrationHomeOwnerIF,
      default: null
    }
  },
  components: { DatePicker },
  setup (props, context) {
    const { customRules, required, maxLength } = useInputRules()

    const { editHomeOwner } = useHomeOwners(true)

    const {
      setUnsavedChanges
    } = useActions([
      'setUnsavedChanges'
    ])

    const deathCertificateNumberRef = ref(null)

    const deathCertificateNumberRules = computed(
      (): Array<Function> => customRules(maxLength(20), required('Enter Death Certificate Registration Number'))
    )

    const localState = reactive({
      validateDeathCertificate: false, // NEW VALIDATOR REQUIRED
      isFormValid: false, // Death Certificate form without Death Date Picker
      isDeathCertificateFormValid: computed((): boolean => localState.isFormValid && !!localState.deathDateTime),
      deathCertificateNumber: props.deceasedOwner?.deathCertificateNumber,
      deathDateTime: props.deceasedOwner?.deathDateTime,
      hasCertificate: false, // Will be used for validation on UI side only (original certificate checkbox)
      showFormError: computed(() => localState.validateDeathCertificate && !localState.isDeathCertificateFormValid),
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
      () => localState.deathCertificateNumber,
      (val: string) => {
        editHomeOwner(
          { ...props.deceasedOwner, deathCertificateNumber: val },
          props.deceasedOwner.groupId
        )
        setUnsavedChanges(true)
      }
    )

    // Update deceased owner deathDateTime when value changes
    watch(
      () => localState.deathDateTime,
      (val: string) => {
        editHomeOwner(
          { ...props.deceasedOwner, deathDateTime: val },
          props.deceasedOwner.groupId
        )
        setUnsavedChanges(true)
      }
    )

    return {
      hasError,
      deathCertificateNumberRef,
      deathCertificateNumberRules,
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
.death-certificate::v-deep {
  margin-bottom: 43px;

  .generic-label {
    line-height: 24px;
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
