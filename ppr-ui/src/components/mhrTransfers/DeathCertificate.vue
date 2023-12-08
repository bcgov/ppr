<template>
  <v-card
    id="death-certificate"
    flat
    class="rounded death-certificate"
  >
    <v-form
      ref="deathCertificateForm"
      v-model="isFormValid"
    >
      <v-row>
        <v-col cols="3">
          <div
            class="generic-label"
            :class="{ 'error-text': validate && hasError(deathCertificateNumberRef) }"
          >
            Death Certificate Registration Number
          </div>
        </v-col>
        <v-col
          cols="9"
          class="pl-2"
        >
          <v-text-field
            id="death-certificate-number"
            ref="deathCertificateNumberRef"
            v-model="deathCertificateNumber"
            variant="filled"
            color="primary"
            :rules="deathCertificateNumberRules"
            label="Death Certificate Registration Number"
            data-test-id="death-certificate-number"
            :disabled="isDisabled"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="3">
          <div
            class="generic-label"
            :class="{ 'error-text': validate && !deathDateTime }"
          >
            Date of Death
          </div>
        </v-col>
        <v-col
          cols="9"
          class="pl-2"
        >
          <InputFieldDatePicker
            id="death-date-time"
            ref="deathDateTimeRef"
            clearable
            title="Date of Death"
            :errorMsg="validate && !deathDateTime ? 'Enter date of death' : ''"
            :initialValue="deathDateTime"
            :maxDate="localTodayDate(maxDeathDate)"
            :disablePicker="isDisabled"
            data-test-id="death-date-time"
            @emitDate="deathDateTime = $event"
            @emitCancel="deathDateTime = null"
            @emitClear="deathDateTime = null"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-spacer />
        <v-col
          cols="9"
          class="pl-1"
        >
          <v-checkbox
            id="has-certificate-checkbox"
            v-model="hasDeathCertificate"
            label="I have an original or certified copy of the death certificate, and confirm
              that it was issued from Canada or the United States, and the name on
              the death certificate matches the name displayed above exactly."
            class="mt-0 pt-0 has-certificate-checkbox"
            :error="validate && !hasDeathCertificate"
            data-test-id="has-certificate-checkbox"
            hideDetails
            :disabled="isDisabled"
          />
        </v-col>
      </v-row>
    </v-form>
  </v-card>
</template>

<script lang="ts">
import { useInputRules, useHomeOwners } from '@/composables'
import { computed, defineComponent, nextTick, reactive, ref, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { FormIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { InputFieldDatePicker } from '@/components/common'
import { localTodayDate } from '@/utils'

export default defineComponent({
  name: 'DeathCertificate',
  components: { InputFieldDatePicker },
  props: {
    deceasedOwner: {
      type: Object as () => MhrRegistrationHomeOwnerIF,
      default: null
    },
    validate: {
      type: Boolean,
      default: false
    },
    // used to disable the form when adding or editing an owner
    isDisabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['isValid'],
  setup (props) {
    const { customRules, required, maxLength } = useInputRules()
    const { editHomeOwner } = useHomeOwners(true)
    const { setUnsavedChanges } = useStore()
    const deathCertificateForm: FormIF = ref(null)
    const deathCertificateNumberRef: FormIF = ref(null)
    const deathCertificateNumberRules = computed(
      (): Array<()=>string|boolean> => customRules(
        maxLength(20),
        required('Enter Death Certificate Registration Number')
      )
    )

    const localState = reactive({
      isFormValid: false, // Death Certificate form without Death Date Picker
      isDeathCertificateFormValid: computed((): boolean => {
        return localState.isFormValid && !!localState.deathDateTime && localState.hasDeathCertificate
      }),
      deathCertificateNumber: props.deceasedOwner?.deathCertificateNumber,
      deathDateTime: props.deceasedOwner?.deathDateTime,
      hasDeathCertificate: props.deceasedOwner?.hasDeathCertificate,
      showFormError: computed(() => {
        return props.validate && !localState.isDeathCertificateFormValid
      }),
      maxDeathDate: computed((): Date => {
        const dateOffset = 24 * 60 * 60 * 1000 // 1 day in milliseconds
        const maxDate = new Date()
        maxDate.setTime(maxDate.getTime() - dateOffset)
        return maxDate
      }),
      deathCertificateNumberRules: computed((): Array<()=>string|boolean> => {
        return customRules(
          maxLength(20),
          required('Enter Death Certificate Registration Number')
        )
      })
    })

    const hasError = (ref: any): boolean => {
      return ref?.hasError
    }

    // Validate form when prompted
    watch(() => props.validate, async (validate: boolean) => {
      await nextTick()
      validate && deathCertificateForm.value.validate()
    }, { immediate: true })

    // Update deceased owner deathCertificateNumber when value changes
    watch(() => localState.deathCertificateNumber, async (val: string) => {
      await nextTick()
      editHomeOwner(
        { ...props.deceasedOwner, deathCertificateNumber: val },
        props.deceasedOwner.groupId
      )
      setUnsavedChanges(true)
    })

    // Update deceased owner deathDateTime when value changes
    watch(() => localState.deathDateTime, async (val: string) => {
      await nextTick()
      editHomeOwner(
        { ...props.deceasedOwner, deathDateTime: val },
        props.deceasedOwner.groupId
      )
      setUnsavedChanges(true)
    })

    // Update deceased owner death certificate confirmation when value changes
    watch(() => localState.hasDeathCertificate, async (val: boolean) => {
      await nextTick()
      editHomeOwner(
        { ...props.deceasedOwner, hasDeathCertificate: val },
        props.deceasedOwner.groupId
      )
      setUnsavedChanges(true)
    })

    return {
      hasError,
      deathCertificateForm,
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
:deep(.death-certificate) {
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
