<template>
  <v-row
    id="mhr-home-manufacturer-year"
  >
    <v-col cols="3">
      <label
        class="generic-label"
        for="manufacturer-year"
        :class="{ 'error-text': validate && hasError(yearRef) }"
      >
        Year of Manufacture
      </label>
    </v-col>
    <v-col cols="4">
      <v-text-field
        id="manufacturer-year"
        ref="yearRef"
        v-model="yearOfManufacture"
        variant="filled"
        :rules="manufactureYearRules"
        label="Year of Manufacture"
        persistentHint
        hint="YYYY"
        data-test-id="manufacture-year"
      />
    </v-col>
    <v-col cols="5">
      <v-checkbox
        id="circa-year"
        v-model="circa"
        label="This Year of Manufacture is approximate"
        class="float-left"
        data-test-id="circa-year-checkbox"
      />
      <v-tooltip
        location="top"
        contentClass="top-tooltip"
        transition="fade-transition"
        data-test-id="circa-year-tooltip"
      >
        <template #activator="{ props }">
          <v-icon
            class="circa-tooltip-icon pl-3 mt-4"
            color="primary"
            v-bind="props"
          >
            mdi-information-outline
          </v-icon>
        </template>
        When the exact year of manufacture is unknown, enter an estimated
        year and indicate that the year is approximate.
      </v-tooltip>
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
  name: 'ManufacturedYearInput',
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
      getMhrRegistrationYearOfManufacture,
      getMhrRegistrationIsYearApproximate
    } = storeToRefs(useStore())
    const {
      customRules,
      required,
      minLength,
      maxLength,
      startsWith,
      greaterThan,
      isNumber
    } = useInputRules()

    const {
      hasError
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const manufactureYearRules = computed((): Array<Function> =>
      customRules(
        required('Enter a year of manufacture'),
        isNumber(),
        minLength(4, true),
        maxLength(4, true),
        startsWith(['19', '20'], 'Year must begin with 19 or 20'),
        greaterThan(new Date().getFullYear() + 1, 'Year cannot be more than 1 year in the future')
      )
    )

    const localState = reactive({
      yearOfManufacture: getMhrRegistrationYearOfManufacture.value?.toString(),
      circa: getMhrRegistrationIsYearApproximate.value
    })

    watch(() => localState.yearOfManufacture, (val: string) => {
      if (parseInt(val)) {
        setMhrHomeBaseInformation({ key: 'year', value: parseInt(val) })
      }
    })

    watch(() => localState.circa, (val: boolean) => {
      setMhrHomeBaseInformation({ key: 'circa', value: val })
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
</style>
