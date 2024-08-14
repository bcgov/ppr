<template>
  <v-card
    id="death-certificate"
    flat
    class="rounded death-certificate pt-4"
  >
    <v-form
      ref="deathCertificateForm"
      v-model="isFormValid"
    >
      <v-row noGutters>
        <v-col cols="3">
          <div
            class="generic-label"
            :class="{ 'error-text': validate && hasError(deathCertificateNumberRef) }"
          >
            <span class="fs-14">Death Certificate Registration Number</span>
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
      <v-row
        noGutters
        class="mt-4"
      >
        <v-col cols="3">
          <div
            class="generic-label"
            :class="{ 'error-text': validate && !deathDateTime }"
          >
            <span class="fs-14">Date of Death</span>
          </div>
        </v-col>
        <v-col
          cols="9"
          class="pl-2"
        >
          <InputFieldDatePicker
            id="death-date-time"
            ref="deathDateTimeRef"
            title="Date of Death"
            :errorMsg="validate && !deathDateTime ? 'Enter date of death' : ''"
            :initialValue="deathDateTime"
            :maxDate="localTodayDate(new Date(), true)"
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
            class="has-certificate-checkbox"
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
      deathCertificateNumberRules: computed((): Array<()=>string|boolean> => {
        return customRules(
          maxLength(20),
          required('Enter death certificate registration number')
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
:deep(.v-selection-control) {
  align-items: flex-start;
}
:deep(.v-selection-control .v-label) {
  margin-top: 6px;
}
:deep(.death-certificate) {
  .has-certificate-checkbox {
    label {
      line-height: 22px;
    }
  }
}
</style>
