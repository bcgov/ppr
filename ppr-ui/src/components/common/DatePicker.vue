<template>
  <v-card class="date-selection registration-date" elevation="6" ref="datePicker">
    <v-row no-gutters>
      <v-col
        class="picker-title"
        :class="{ 'picker-err': startDate === null && datePickerErr }"
        cols="6"
      >
        Select Start Date:
      </v-col>
      <v-col
        class="picker-title pl-4"
        :class="{ 'picker-err': endDate === null && datePickerErr && !disableEndDate }"
        cols="6"
      >
        Select End Date:
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="6">
        <v-date-picker
          color="primary"
          :max="endDate ? endDate : today"
          v-model="startDate"
        />
      </v-col>
      <v-col cols="6">
        <v-date-picker
          color="primary"
          :min="startDate ? startDate : null"
          :max="today"
          v-model="endDate"
        />
      </v-col>
    </v-row>
    <v-row no-gutters justify="end">
      <v-col cols="auto pr-4">
        <v-btn
          class="date-selection-btn bold"
          ripple
          small
          text
          @click="submitDateRange()"
        >
          OK
        </v-btn>
        <v-btn
          class="date-selection-btn ml-4"
          ripple
          small
          text
          @click="resetDateRange()"
        >
          Cancel
        </v-btn>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'

export default defineComponent({
  name: 'DatePicker',
  props: {
    setEndDate: { type: Date },
    setStartDate: { type: Date }
  },
  emits: ['submit'],
  setup (props, { emit }) {
    const localState = reactive({
      datePickerErr: false,
      endDate: null,
      startDate: null,
      defaultMonth: computed(() => {
        const todayDate = new Date()
        return todayDate.toISOString().substring(0, 8)
      }),
      today: computed(() => {
        const todayDate = new Date()
        return todayDate.toLocaleDateString('en-CA')
      })
    })
    const emitDateRange = (): void => {
      if (
        localState.startDate === localState.defaultMonth ||
        localState.endDate === localState.defaultMonth
      ) {
        emit('submit', { endDate: null, startDate: null })
      } else {
        emit(
          'submit',
          { endDate: localState.endDate, startDate: localState.startDate }
        )
      }
    }
    const resetDateRange = (): void => {
      // reset dates by setting year/month with no day (defaults back to current month)
      localState.endDate = localState.defaultMonth
      localState.startDate = localState.defaultMonth
      // set to null after to clear
      setTimeout(() => {
        localState.endDate = null
        localState.startDate = null
      }, 10)
      localState.datePickerErr = false
      emitDateRange()
    }
    const submitDateRange = (): void => {
      if (!localState.startDate || !localState.endDate) {
        localState.datePickerErr = true
        return
      }
      localState.datePickerErr = false
      emitDateRange()
    }

    watch(() => props.setEndDate, (val) => {
      if (!val) {
        localState.endDate = localState.defaultMonth
        setTimeout(() => {
          localState.endDate = null
        }, 10)
      } else localState.endDate = val
    })
    watch(() => props.setStartDate, (val) => {
      if (!val) {
        localState.startDate = localState.defaultMonth
        setTimeout(() => {
          localState.startDate = null
        }, 10)
      } else localState.startDate = val
    })

    return {
      emitDateRange,
      resetDateRange,
      submitDateRange,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.date-selection {
  border-radius: 5px;
  z-index: 10;
  left: 50%;
  margin-top: 120px;
  overflow: auto;
  padding: 24px 34px 24px 34px;
  position: absolute;
  transform: translate(-50%, 0);
  background-color: white;
  width: 700px;
  td {
    padding: 0;
  }
}
</style>
