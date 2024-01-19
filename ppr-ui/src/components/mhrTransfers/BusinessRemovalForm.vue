<template>
  <v-form
    id="business-removal-form"
    ref="businessRemovalFormRef"
    class="pt-4"
  >
    <v-row noGutters>
      <v-col cols="3">
        <div
          class="generic-label pr-2"
          :class="{ 'error-text': validate && !state?.deathCorpNumber }"
        >
          <span class="fs-14">Incorporation or Registration Number</span>
        </div>
      </v-col>
      <v-col
        cols="9"
        class="pl-2"
      >
        <v-text-field
          id="corp-or-reg-num"
          ref="corpOrRegNumRef"
          v-model="state.deathCorpNumber"
          variant="filled"
          label="Incorporation or Registration Number"
          :rules="state?.corpNumRules"
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
          :class="{ 'error-text': validate && !state?.dateOfDissolution }"
        >
          <span class="fs-14">Date of Dissolution or Cancellation</span>
        </div>
      </v-col>
      <v-col
        cols="9"
        class="pl-2"
      >
        <InputFieldDatePicker
          id="date-of-dissolution"
          ref="dateOfDissolutionRef"
          title="Date of Dissolution or Cancellation"
          :errorMsg="validate && !state?.dateOfDissolution ? 'Date of Dissolution or Cancellation' : ''"
          :initialValue="state?.dateOfDissolution"
          :maxDate="state?.todayDate"
          @emitDate="state.dateOfDissolution = $event"
          @emitCancel="state.dateOfDissolution = null"
          @emitClear="state.dateOfDissolution = null"
        />
      </v-col>
    </v-row>
  </v-form>
</template>
<script setup lang="ts">
import { InputFieldDatePicker } from '@/components/common'
import { computed, reactive, ref, watch } from 'vue'
import { useHomeOwners, useInputRules } from '@/composables'
import { FormIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { localTodayDate } from '@/utils'
import { useStore } from '@/store/store'

// Refs
const businessRemovalFormRef: FormIF = ref(null)

// Props
const props = defineProps<{
  validate?: boolean,
  historicalOwner: MhrRegistrationHomeOwnerIF
}>()

// Composables
const { setUnsavedChanges } = useStore()
const { customRules, required, maxLength } = useInputRules()
const { editHomeOwner } = useHomeOwners(true)

// Local State
const state = reactive({
  deathCorpNumber: props.historicalOwner?.deathCorpNumber || '',
  dateOfDissolution: props.historicalOwner?.deathDateTime || null,
  corpNumRules: computed((): Array<()=>string|boolean> => {
    return customRules(
      maxLength(20),
      required('Enter an Incorporation or Registration Number')
    )
  }),
  todayDate: computed((): string => {
    return localTodayDate(new Date(), true)
  })
})

// Validate form when prompted
watch(() => props.validate, async (validate: boolean) => {
  validate && businessRemovalFormRef.value.validate()
})

// Update historical owner deathCorpNumber when value changes
watch(() => state.deathCorpNumber, async (val: string) => {
  editHomeOwner(
    { ...props.historicalOwner, deathCorpNumber: val },
    props.historicalOwner?.groupId
  )
  setUnsavedChanges(true)
})

// Update historical owner deathDateTime when value changes
watch(() => state.dateOfDissolution, async (val: string) => {
  editHomeOwner(
    { ...props.historicalOwner, deathDateTime: val },
    props.historicalOwner?.groupId
  )
  setUnsavedChanges(true)
})
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
