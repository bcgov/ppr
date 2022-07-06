<template>
  <div>
    <v-card flat class="py-6 px-8 rounded">
      <v-row id="mhr-home-manufacturer-name">
        <v-col cols="2">
          <label class="generic-label" for="manufacturer-name"
            >Manufacturer's Name</label
          >
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
          <label class="generic-label" for="manufacturer-year"
            >Year of Manufacture</label
          >
        </v-col>
        <v-col cols="4">
          <v-text-field
            id="manufacturer-year"
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
          >
            <template v-slot:activator="{ on }">
              <v-icon
                class="circa-tooltip-icon ml-2 mt-n1"
                color="primary"
                v-on="on">mdi-information-outline</v-icon>
            </template>
            When the exact year of manufacture is unknown, enter an estimated
            year and indicate that the year is approximate.
          </v-tooltip>
        </v-col>
      </v-row>

      <v-divider class="mt-2 mb-5" />

      <v-row id="mhr-home-manufacturer-make">
        <v-col cols="2">
          <label class="generic-label" for="manufacturer-make">Make</label>
        </v-col>
        <v-col cols="10">
          <v-text-field
            id="manufacturer-make"
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
          <label class="generic-label" for="manufacturer-model">Model</label>
        </v-col>
        <v-col cols="10">
          <v-text-field
            id="manufacturer-model"
            v-model="model"
            filled
            :rules="modelRules"
            label="Model"
            data-test-id="manufacturer-model"
          >
          </v-text-field>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import { useInputRules } from '@/composables/useInputRules'

export default defineComponent({
  setup () {
    const { customRules, required, minLength, maxLength, startsWith, graterThan, isNumber } = useInputRules()

    const {
      getMhrRegistrationManufacturerName,
      getMhrRegistrationYearOfManufacture,
      getMhrRegistrationIsYearApproximate,
      getMhrRegistrationHomeMake,
      getMhrRegistrationHomeModel
    } = useGetters<any>([
      'getMhrRegistrationManufacturerName',
      'getMhrRegistrationYearOfManufacture',
      'getMhrRegistrationIsYearApproximate',
      'getMhrRegistrationHomeMake',
      'getMhrRegistrationHomeModel'
    ])

    const {
      setMhrHomeRegistration
    } = useActions<any>([
      'setMhrHomeRegistration'
    ])

    const manufactureYearRules: Array<Function> =
      customRules(
        required('Enter a year of manufacture'),
        isNumber(),
        minLength(4, true),
        maxLength(4, true),
        startsWith(['19', '20'], 'Year must begin with 19 or 20'),
        graterThan(new Date().getFullYear() + 1, 'Year cannot be more than 1 year in the future')
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
      manufacturerName: getMhrRegistrationManufacturerName.value,
      yearOfManufacture: getMhrRegistrationYearOfManufacture.value,
      circa: getMhrRegistrationIsYearApproximate.value,
      make: getMhrRegistrationHomeMake.value,
      model: getMhrRegistrationHomeModel.value
    })

    watch(
      () => localState.manufacturerName,
      (val: string) => {
        setMhrHomeRegistration({ key: 'description.manufacturer', value: val })
      }
    )

    watch(
      () => localState.yearOfManufacture,
      (val: number) => {
        setMhrHomeRegistration({ key: 'description.baseInformation.year', value: val })
      }
    )

    watch(
      () => localState.circa,
      (val: boolean) => {
        setMhrHomeRegistration({ key: 'description.baseInformation.circa', value: val })
      }
    )

    watch(
      () => localState.make,
      (val: string) => {
        setMhrHomeRegistration({ key: 'description.baseInformation.make', value: val })
      }
    )

    watch(
      () => localState.model,
      (val: string) => {
        setMhrHomeRegistration({ key: 'description.baseInformation.model', value: val })
      }
    )

    return {
      manufactureYearRules,
      makeRules,
      modelRules,
      maxLength,
      graterThan,
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
