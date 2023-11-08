<template>
  <div
    class="base-date-picker"
    :class="{ 'base-date-picker__err': error }"
  >
    <div class="base-date-picker__header">
      <v-btn
        class="base-date-picker__header__year"
        variant="text"
        @click="openYearsSelection = true"
      >
        {{ selectedYear }}
      </v-btn>
      <div
        v-if="selectedDate"
        class="base-date-picker__header__date"
      >
        {{ getWeekDay(selectedDate) }}, {{ getMonth(selectedDate) }} {{ selectedDate.getDate() }}
      </div>
    </div>
    <VueDatePicker
      v-model="selectedDate"
      autoApply
      :actionRow="{ showCancel: false, showNow: false, showPreview: false, showSelect: false }"
      calendarCellClassName="base-date-picker__calendar__day"
      calendarClassName="base-date-picker__calendar"
      :dayNames="['SUN', 'MON','TUE','WED','THU','FRI','SAT']"
      :enableTimePicker="false"
      format="yyyy-MM-dd"
      hideOffsetDates
      inline
      :maxDate="maxDate"
      :minDate="minDate"
      :monthChangeOnScroll="false"
      :weekStart="0"
    >
      <template
        #month-year="{
          month,
          year,
          months,
          years,
          handleMonthYearChange,
          updateMonthYear
        } : {
          month: number,
          year: number,
          months: { text: string, value: number }[],
          years: { text: string, value: number }[],
          handleMonthYearChange: (isNext: boolean) => void,
          updateMonthYear: (month: number, year: number) => void
        }"
      >
        <v-row
          v-if="!openMonthsSelection"
          class="base-date-picker__month-year"
          noGutters
        >
          <v-col cols="2">
            <v-btn
              class="base-date-picker__month-year__prev-btn"
              variant="flat"
              icon
              style="float: right;"
              @click="handleMonthYearChange(false); headerMonthYearChange(month, false);"
            >
              <v-icon>mdi-chevron-left</v-icon>
            </v-btn>
          </v-col>
          <v-col alignSelf="center">
            <v-btn
              class="base-date-picker__month-year__date-btn"
              variant="text"
              style="width: 100%;"
              @click="openMonthsSelection = true"
            >
              <b>{{ localMonths[month] }} {{ year }}</b>
            </v-btn>
          </v-col>
          <v-col cols="2">
            <v-btn
              class="base-date-picker__month-year__next-btn"
              variant="flat"
              icon
              style="float: left;"
              @click="handleMonthYearChange(true); headerMonthYearChange(month, true);"
            >
              <v-icon>mdi-chevron-right</v-icon>
            </v-btn>
          </v-col>
        </v-row>
        <div
          v-if="openMonthsSelection || openYearsSelection"
          ref="selectRef"
          class="base-date-picker__select"
        >
          <div
            v-if="openMonthsSelection"
            class="base-date-picker__select__month"
          >
            <v-row
              v-for="monthGrp, i in [months.slice(0,3), months.slice(3,6), months.slice(6,9), months.slice(9,12)]"
              :key="i + 'monthgrp'"
              justify="center"
              noGutters
            >
              <v-col
                v-for="m in monthGrp"
                :key="m.value + 'month'"
              >
                <v-btn
                  class="base-date-picker__select__month__btn"
                  :class="m.value === selectedMonth ? 'selected' : ''"
                  variant="outlined"
                  @click="selectMonth(m.value, updateMonthYear)"
                >
                  {{ m.text }}
                </v-btn>
              </v-col>
            </v-row>
          </div>
          <v-list
            v-else-if="openYearsSelection"
            class="base-date-picker__select__year"
          >
            <v-list-item
              v-for="y in years"
              :key="y.value"
            >
              <v-btn
                ref="yearRef"
                class="base-date-picker__select__year__btn"
                :class="y.value === selectedYear ? 'selected' : ''"
                variant="text"
                @click="updateMonthYear(selectedMonth, y.value); selectedYear = y.value; openYearsSelection = false;"
              >
                {{ y.text }}
              </v-btn>
            </v-list-item>
          </v-list>
        </div>
      </template>
    </VueDatePicker>
  </div>
</template>

<script setup lang="ts">
import { ComponentPublicInstance, Ref, computed, nextTick, ref, watch } from 'vue'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

// props / emits
const props = defineProps<{
  defaultSelectedDate?: Date
  error?: boolean
  setMaxDate?: Date
  setMinDate?: Date
  resetTrigger?: boolean
}>()
const emit = defineEmits<{ (e: 'selectedDate', value: Date): void }>()

// date selection
const selectedDate: Ref<Date> = ref(props.defaultSelectedDate || null)

// date defaults
const defaultMonth = selectedDate.value?.getMonth() || (new Date()).getMonth()
const defaultYear = selectedDate.value?.getFullYear() || (new Date()).getFullYear()

// date month/year selections
const selectedMonth = ref(defaultMonth)
const selectedYear = ref(defaultYear)

watch(() => props.resetTrigger, () => {
  selectedDate.value = props.defaultSelectedDate || null
  selectedMonth.value = defaultMonth
  selectedYear.value = defaultYear
})

watch(() => selectedDate.value, (val) => {
  if (val) selectedYear.value = val.getFullYear()
  emit('selectedDate', val)
})

// month / year menus
const selectRef:Ref<HTMLInputElement> = ref(null)
const yearRef:Ref<ComponentPublicInstance<HTMLInputElement>[]> = ref(null)

const openMonthsSelection = ref(false)
const openYearsSelection = ref(false)
watch(() => openYearsSelection.value, (val) => {
  if (val) {
    openMonthsSelection.value = false
    scrollToSelectedYear()
  }
})

const scrollToSelectedYear = async () => {
  // wait for refs to exist
  await nextTick()
  if (selectRef.value && yearRef.value) {
    // find selected ref
    for (const i in yearRef.value) {
      if (yearRef.value[i].$el?.className.includes('selected')) {
        const selectRefTop = (selectRef.value?.getBoundingClientRect())?.top
        const refTop = (yearRef.value[i].$el?.getBoundingClientRect())?.top
        if (selectRefTop && refTop) {
          selectRef.value.scroll(0, refTop - selectRefTop - 135)
          return
        }
      }
    }
  }
  // log error so we know to debug this
  console.error(`Datepicker YEAR scroll error.`)
}

// max/min
const maxDate: Ref<Date> = ref(props.setMaxDate || null)
watch(() => props.setMaxDate, (val) => maxDate.value = val)

const minDate: Ref<Date> = ref(props.setMinDate || null)
watch(() => props.setMinDate, (val) => minDate.value = val)

// error
const error = computed(() => props.error)

// template functions
const selectMonth = (m: number, updateMonthYear: (month: number, year: number) => void) => {
  updateMonthYear(m, selectedYear.value)
  selectedMonth.value = m
  openYearsSelection.value = true
  openMonthsSelection.value = false
}

const headerMonthYearChange = (month: number, next: boolean) => {
  if (!selectedDate.value) {
    if (month === 0 && !next) {
      selectedYear.value--
      selectedMonth.value = 11
    } else if (month === 11 && next) {
      selectedYear.value++
      selectedMonth.value = 0
    } else {
      selectedMonth.value += next ? 1 : -1
    }
  }
}

// utility text functions
const getWeekDay = (d: Date) => {
  return ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][d.getDay()]
}

const localMonths = ['January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December']

const getMonth = (d: Date) => {
  return localMonths[d.getMonth()].slice(0, 3)
}
</script>
<style lang="scss">
@import '@/assets/styles/theme.scss';
.base-date-picker {
  width: 300px;

  &__err {
    border: 1px solid $error;
    border-radius: 10px;
    box-shadow: 0px 0px 3px $error;
  }

  &__header {
    background-color: $app-blue;
    border-radius: 10px 10px 0 0;
    height: 100px;
    padding: 10px;
    width: 298px;
    color: white;

    &__date {
      font-size: 24px;
      margin-left: 17px;
    }
  }

  &__calendar {

    &__day {
      border-radius: 50%;
    }

    .dp__calendar_header {
      margin-top: 6px;

      .dp__calendar_header_item {
        font-size: 12px;
        font-weight: 500;
        color: $gray9 !important;
        padding: 4px 0 0 0;
        width: 40px;
      }
    }
  }

  &__month-year {

    &__prev-btn,
    &__next-btn {
      background-color: transparent !important;
      color: $app-blue !important;
    }

    &__prev-btn:hover,
    &__next-btn:hover {
      background-color: $blueSelected !important;
    }
  }

  &__select {
    height: 321px;
    left: 0;
    overflow: scroll;
    position: absolute;
    top: 0;
    width: 294px;
    z-index: 1;

    &__month {
      background-color: white;
      height: 270px;
      margin-top: 44px;

      &__btn {
        border-color: transparent;
        height: 65px !important;
        text-align: center;
        width: 100%;
      }

      &__btn:hover {
        background-color: $blueSelected;
      }

      &__btn.selected {
        color: $app-blue;
        border-color: $app-blue;
      }
    }

    &__year {

      &__btn {
        padding: 0;
        height: 48px !important;
        width: 100%;
      }

      &__btn:hover {
        background-color: $blueSelected;
      }

      &__btn.selected {
        color: $app-blue;
        font-size: 24px;
        font-weight: 500;
      }

      .v-list-item {
        padding: 0 !important;
      }
    }
  }

  .dp__menu {
    border-radius: 0 0 10px 10px;
    height: 329px;
  }

  .dp__main {
    display: block;
    width: 298px;
  }

  .dp__theme_light {
    --dp-background-color: #ffffff;
    --dp-text-color: #495057;
    --dp-hover-color: #E4EDF7;
    --dp-hover-text-color: #495057;
    --dp-hover-icon-color: #495057;
    --dp-primary-color: #1669bb;
    --dp-primary-text-color: #f8f5f5;
    --dp-secondary-color: #c0c4cc;
    --dp-border-color: #ddd;
    --dp-menu-border-color: #ddd;
    --dp-border-color-hover: #aaaeb7;
    --dp-disabled-color: #f6f6f6;
    --dp-scroll-bar-background: #f3f3f3;
    --dp-scroll-bar-color: #959595;
    --dp-success-color: #76d275;
    --dp-success-color-disabled: #a3d9b1;
    --dp-icon-color: #959595;
    --dp-danger-color: #ff6f60;
    --dp-highlight-color: rgba(25, 118, 210, 0.1);
  }
}
</style>
