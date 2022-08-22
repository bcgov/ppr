<template>
  <div>
    <v-card flat class="py-6 px-8 rounded">
      <v-form ref="makeModelComboForm" v-model="makeModelValid">
        <v-row id="mhr-home-manufacturer-name">
          <v-col cols="2">
            <label class="generic-label" for="manufacturer-name">Manufacturer's Name</label>
          </v-col>
          <v-col cols="10">
            <v-text-field
              id="manufacturer-name"
              v-model="manufacturerName"
              filled
              :rules="maxLength(65)"
              label="Business Legal Name (Optional)"
              data-test-id="manufacturer-name"
            />
          </v-col>
        </v-row>

        <v-row id="mhr-home-manufacturer-year">
          <v-col cols="2">
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
              filled
              :rules="manufactureYearRules"
              label="Year of Manufacture"
              persistent-hint
              hint="YYYY"
              data-test-id="manufacture-year"
            />
          </v-col>
          <v-col cols="6">
            <v-checkbox
              id="circa-year"
              label="This Year of Manufacture is approximate"
              v-model="circa"
              class="float-left"
              data-test-id="circa-year-checkbox"
            />
            <v-tooltip
              top
              content-class="top-tooltip pa-5"
              transition="fade-transition"
              data-test-id="circa-year-tooltip"
              nudge-right="3"
              nudge-bottom="22"
            >
              <template v-slot:activator="{ on }">
                <v-icon
                  class="circa-tooltip-icon ml-2 mt-n1"
                  color="primary"
                  v-on="on"
                  >mdi-information-outline</v-icon
                >
              </template>
              When the exact year of manufacture is unknown, enter an estimated
              year and indicate that the year is approximate.
            </v-tooltip>
          </v-col>
        </v-row>

        <v-divider class="mt-2 mb-5 mx-0 w-100" />

        <v-row id="mhr-home-manufacturer-make">
          <v-col cols="2">
            <label
              class="generic-label"
              for="manufacturer-make"
              :class="{ 'error-text': validate && hasError(makeRef) }"
            >Make</label>
          </v-col>
          <v-col cols="10">
            <v-text-field
              id="manufacturer-make"
              ref="makeRef"
              v-model="make"
              filled
              :rules="makeRules"
              label="Make"
              data-test-id="manufacturer-make"
            />
          </v-col>
        </v-row>

        <v-row id="mhr-home-manufacturer-model">
          <v-col cols="2">
            <label
              class="generic-label"
              for="manufacturer-model"
              :class="{ 'error-text': validate && hasError(modelRef) }"
            >Model</label>
          </v-col>
          <v-col cols="10">
            <v-text-field
              id="manufacturer-model"
              ref="modelRef"
              v-model="model"
              filled
              :rules="modelRules"
              label="Model"
              data-test-id="manufacturer-model"
            >
            </v-text-field>
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  ref,
  toRefs,
  watch
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { useInputRules, useMhrValidations } from '@/composables/'

export default defineComponent({
  props: {
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    // Form Refs
    const makeModelComboForm = ref(null)
    const yearRef = ref(null)
    const makeRef = ref(null)
    const modelRef = ref(null)

    const {
      getMhrRegistrationValidationModel,
      getMhrRegistrationManufacturerName,
      getMhrRegistrationYearOfManufacture,
      getMhrRegistrationIsYearApproximate,
      getMhrRegistrationHomeMake,
      getMhrRegistrationHomeModel
    } = useGetters<any>([
      'getMhrRegistrationValidationModel',
      'getMhrRegistrationManufacturerName',
      'getMhrRegistrationYearOfManufacture',
      'getMhrRegistrationIsYearApproximate',
      'getMhrRegistrationHomeMake',
      'getMhrRegistrationHomeModel'
    ])

    const {
      setMhrHomeDescription,
      setMhrHomeBaseInformation
    } = useActions<any>([
      'setMhrHomeDescription',
      'setMhrHomeBaseInformation'
    ])

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
      MhrCompVal,
      MhrSectVal,
      hasError,
      setValidation
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

    const combinedMakeModelLengthRule = (localState): Array<Function> => {
      return [
        () => (0 || localState.model.length) + (0 || localState.make.length) <= 65 ||
          'Make and Model combined cannot exceed 65 characters'
      ]
    }

    const makeRules = computed((): Array<Function> =>
      customRules(
        required('Enter a make'),
        combinedMakeModelLengthRule(localState)
      )
    )

    const modelRules = computed((): Array<Function> =>
      customRules(
        required('Enter a model'),
        combinedMakeModelLengthRule(localState)
      )
    )

    const localState = reactive({
      makeModelValid: false,
      manufacturerName: getMhrRegistrationManufacturerName.value,
      yearOfManufacture: getMhrRegistrationYearOfManufacture.value,
      circa: getMhrRegistrationIsYearApproximate.value,
      make: getMhrRegistrationHomeMake.value,
      model: getMhrRegistrationHomeModel.value
    })

    watch(() => localState.manufacturerName, (val: string) => {
      setMhrHomeDescription({ key: 'manufacturer', value: val })
    })

    watch(() => localState.yearOfManufacture, (val: number) => {
      setMhrHomeBaseInformation({ key: 'year', value: +val })
    })

    watch(() => localState.circa, (val: boolean) => {
      setMhrHomeBaseInformation({ key: 'circa', value: val })
    })

    watch(() => localState.make, (val: string) => {
      setMhrHomeBaseInformation({ key: 'make', value: val })
    })

    watch(() => localState.model, (val: string) => {
      setMhrHomeBaseInformation({ key: 'model', value: val })
    })

    watch(() => localState.makeModelValid, (val: boolean) => {
      setValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.MAKE_MODEL_VALID, val)
    })

    watch(() => props.validate, async () => {
      // @ts-ignore - function exists
      await context.refs.makeModelComboForm.validate()
    })

    return {
      hasError,
      yearRef,
      makeRef,
      modelRef,
      makeModelComboForm,
      manufactureYearRules,
      makeRules,
      modelRules,
      maxLength,
      greaterThan,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
::v-deep .circa-tooltip-icon {
  line-height: 3em;
}
</style>
