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
            label="Business Legal Name (Optional)"
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
            label="Year of Manufacture"
            persistent-hint
            hint="YYYY"
          />
        </v-col>
        <v-col cols="6">
          <v-checkbox>
            <template v-slot:label>
              This Year of Manufacture is approximate
            </template>
          </v-checkbox>
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
            label="Make"
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
            label="Model"
          />
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

export default defineComponent({
  setup () {
    const {
      getMhrRegistrationManufacturerName,
      getMhrRegistrationYearOfManufacture,
      getMhrRegistrationHomeMake,
      getMhrRegistrationHomeModel
    } = useGetters<any>([
      'getMhrRegistrationManufacturerName',
      'getMhrRegistrationYearOfManufacture',
      'getMhrRegistrationHomeMake',
      'getMhrRegistrationHomeModel'
    ])
    const {
      setMhrHomeRegistration
    } = useActions<any>([
      'setMhrHomeRegistration'
    ])

    const localState = reactive({
      manufacturerName: getMhrRegistrationManufacturerName.value,
      yearOfManufacture: getMhrRegistrationYearOfManufacture.value,
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
      ...toRefs(localState)
    }
  }
})
</script>

<style scoped></style>
