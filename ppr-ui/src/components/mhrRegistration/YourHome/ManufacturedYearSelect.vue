<template>
  <v-row id="mhr-home-manufacturer-year">
    <v-col cols="3">
      <label
        class="generic-label"
        :class="{ 'error-text': validate && hasError(yearRef) }"
      >
        Year of Manufacture
      </label>
    </v-col>
    <v-col cols="4">
      <v-select
        id="manufacturer-year-select"
        ref="yearRef"
        v-model="yearOfManufacture"
        :items="[currentYear + 1, currentYear, currentYear - 1]"
        variant="filled"
        color="primary"
        :rules="manufactureYearRules"
        label="Year of Manufacture"
        data-test-id="manufacture-year-select"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  ref,
  toRefs,
  watch
} from 'vue'
import { useStore } from '@/store/store'
import { useInputRules, useMhrValidations } from '@/composables/'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'ManufacturedYearSelect',
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const yearRef = ref(null)

    const { setMhrHomeBaseInformation } = useStore()
    const {
      // Getters
      getMhrRegistrationValidationModel,
      getMhrRegistrationYearOfManufacture
    } = storeToRefs(useStore())
    const {
      customRules,
      required,
      greaterThan,
      isNumber
    } = useInputRules()

    const {
      hasError
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const manufactureYearRules = computed((): Array<()=>string|boolean> =>
      customRules(
        required('Select year of manufacture'),
        isNumber(),
        greaterThan(new Date().getFullYear() + 1, 'Year cannot be more than 1 year in the future')
      )
    )

    const localState = reactive({
      currentYear: new Date().getFullYear(),
      yearOfManufacture: getMhrRegistrationYearOfManufacture?.value
    })

    watch(() => localState.yearOfManufacture, (val: number) => {
      setMhrHomeBaseInformation({ key: 'year', value: val })
    })

    return {
      hasError,
      yearRef,
      manufactureYearRules,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
:deep(.theme--light.v-select .v-select__selection--comma) {
  color: $gray7;
}
:deep(.v-list-item .v-list-item__title, .v-list-item .v-list-item__subtitle) {
  color: $gray7;
}
.v-list-item--link[aria-selected='true'] {
  background-color: $blueSelected !important;
  .v-list-item__title, .v-list-item .v-list-item__subtitle {
    color: $app-blue !important;
  }
}
:deep(.v-list-item--link:hover) {
  background-color: $gray1 !important;
  .v-list-item__title, .v-list-item .v-list-item__subtitle {
    color: $app-blue !important;
  }
}
</style>
