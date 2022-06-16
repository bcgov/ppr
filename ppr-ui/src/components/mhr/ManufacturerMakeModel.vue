<template>
  <div>
    <section id="mhr-make-model" no-gutters class="pt-10">
      <v-col cols="auto" class="sub-header">
        1. Manufacturer, Make, and Model
      </v-col>
    </section>
    <section no-gutters>
      <v-col class="pt-2 pb-6 sub-header-info">
        Enter the Year of Manufacture (not the model year), Make, and Model of
        the home.
      </v-col>
    </section>

    <v-card flat class="white pb-6 pt-6 pr-10 pl-8 rounded">
      <v-row>
        <v-col cols="2">
          <label class="generic-label ml" for="">Manufacturer's Name</label>
        </v-col>
        <v-col cols="10">
          <v-text-field
            v-model="manufacturerName"
            filled
            label="Business Legal Name (Optional)"
          />
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="2">
          <label class="generic-label ml" for="">Year of Manufacture</label>
        </v-col>
        <v-col cols="4">
          <v-text-field
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

      <v-divider class="ma-0 pa-0 mt-2 mb-5" />

      <v-row>
        <v-col cols="2">
          <label class="generic-label ml" for="">Make</label>
        </v-col>
        <v-col cols="10">
          <v-text-field v-model="make" filled label="Make" />
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="2">
          <label class="generic-label ml" for="">Model</label>
        </v-col>
        <v-col cols="10">
          <v-text-field v-model="model" filled label="Model" />
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
      setMhrRegistrationManufacturerName,
      setMhrRegistrationYearOfManufacture,
      setMhrRegistrationHomeMake,
      setMhrRegistrationHomeModel
    } = useActions<any>([
      'setMhrRegistrationManufacturerName',
      'setMhrRegistrationYearOfManufacture',
      'setMhrRegistrationHomeMake',
      'setMhrRegistrationHomeModel'
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
        setMhrRegistrationManufacturerName(val)
      }
    )

    watch(
      () => localState.yearOfManufacture,
      (val: string) => {
        setMhrRegistrationYearOfManufacture(val)
      }
    )

    watch(
      () => localState.make,
      (val: string) => {
        setMhrRegistrationHomeMake(val)
      }
    )

    watch(
      () => localState.model,
      (val: string) => {
        setMhrRegistrationHomeModel(val)
      }
    )

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style scoped></style>
