<template>
  <section
    id="mhr-history-location"
    class="pr-4"
  >
    <v-row
      noGutters
      class="pt-4 pb-5"
    >
      <v-col cols="3">
        <h4>Location Type</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ content?.locationType || '(Not Entered)' }}</p>
      </v-col>

      <template v-if="content.locationType === HomeLocationTypes.LOT">
        <v-col
          cols="3"
        >
          <h4>Dealer / Manufacturer Name</h4>
        </v-col>
        <v-col
          cols="6"
          class="pl-3"
        >
          <p>{{ content.dealerName || '(Not Entered)' }}</p>
        </v-col>
      </template>

      <!-- Park Type -->
      <template v-if="content.locationType === HomeLocationTypes.HOME_PARK">
        <v-col cols="3">
          <h4>Park Name</h4>
        </v-col>
        <v-col cols="9">
          <p>{{ content.parkName || '(Not Entered)' }}</p>
        </v-col>
        <v-col cols="3">
          <h4>Pad</h4>
        </v-col>
        <v-col cols="9">
          <p>{{ content.pad || '(Not Entered)' }}</p>
        </v-col>
      </template>

      <template
        v-if="
          [HomeLocationTypes.OTHER_RESERVE,
           HomeLocationTypes.OTHER_STRATA,
           HomeLocationTypes.OTHER_LAND].includes(content.locationType)"
      >
        <v-row
          noGutters
          class="condensed-row other-land-content"
        >
          <template v-if="content.pidNumber">
            <v-col
              cols="12"
              class="pb-2"
            >
              <h4>Legal Land Description</h4>
            </v-col>

            <v-col cols="3">
              <h4>Pid Number</h4>
            </v-col>
            <v-col
              cols="7"
              class="pl-3"
            >
              <p>{{ content.pidNumber || '(Not Entered)' }}</p>
            </v-col>
            <v-col
              v-if="content.legalDescription"
              cols="3"
            >
              <h4>Legal Description</h4>
            </v-col>
            <v-col
              cols="7"
              class="pl-3"
            >
              <p>{{ content.legalDescription }}</p>
            </v-col>
          </template>

          <v-col
            v-else
            cols="3"
            class="pb-2"
          >
            <h4>Legal Land Description</h4>
          </v-col>

          <v-col
            cols="7"
            class="pl-3"
          >
            <p v-if="content.bandName">
              Band Name: {{ content.bandName || '(Not Entered)' }}
            </p>
            <p v-if="content.reserveNumber">
              Reserve Number: {{ content.reserveNumber || '(Not Entered)' }}
            </p>
            <p v-if="content.lot">
              Lot: {{ content.lot }}
            </p>
            <p v-if="content.parcel">
              Parcel: {{ content.parcel }}
            </p>
            <p v-if="content.block">
              Block: {{ content.block }}
            </p>
            <p v-if="content.districtLot">
              District Lot: {{ content.districtLot }}
            </p>
            <p v-if="content.partOf">
              Part of: {{ content.partOf }}
            </p>
            <p v-if="content.section">
              Section: {{ content.section }}
            </p>
            <p v-if="content.township">
              Township: {{ content.township }}
            </p>
            <p v-if="content.range">
              Range: {{ content.range }}
            </p>
            <p v-if="content.meridian">
              Meridian: {{ content.meridian }}
            </p>
            <p v-if="content.landDistrict">
              Land District: {{ content.landDistrict }}
            </p>
            <p v-if="content.plan">
              Plan: {{ content.plan }}
            </p>
            <p v-if="content.exceptionPlan">
              Exception Plan: {{ content.exceptionPlan }}
            </p>
          </v-col>

          <v-col
            v-if="content.additionalDescription"
            cols="3"
          >
            <h4>Additional Description</h4>
          </v-col>
          <v-col
            cols="7"
            class="pl-3"
          >
            <p>{{ content.additionalDescription }}</p>
          </v-col>
        </v-row>
      </template>
    </v-row>

    <!-- Civic Address -->
    <v-row
      noGutters
      class="condensed-row py-5"
    >
      <v-col cols="3">
        <h4>Civic Address</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>
          <span v-if="!!content.address.street">
            {{ content.address.street }}<br>
          </span>
          <span v-if="!!content.address.streetAdditional">
            {{ content.address.streetAdditional }}<br>
          </span>
          {{ content.address.city }}
          {{ content.address.region }}
          <br>{{ getCountryName(content.address.country) }}
        </p>
      </v-col>
    </v-row>

    <!-- Land Details -->
    <v-row
      noGutters
      class="condensed-row py-5"
    >
      <v-col cols="12">
        <h4>Land Details</h4>
      </v-col>
      <v-col
        cols="3"
        class="mt-3"
      >
        <h4>Lease or Land <br>Ownership</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3 mt-3"
      >
        <p>
          The manufactured home is<b>{{ !!isOwnLand ? '' : ' not' }}</b> located on land that the
          homeowners own or on land that they have a registered lease of 3 years or more.
        </p>
      </v-col>
    </v-row>

    <!-- To From Details -->
    <v-row
      noGutters
      class="py-6 condensed-row"
    >
      <v-col cols="3">
        <h4>From</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ shortPacificDate(content?.createDateTime) || '(Not Entered)' }}</p>
      </v-col>
      <v-col cols="3">
        <h4>Document Type</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ content?.registrationDescription || '(Not Entered)' }}</p>
      </v-col>
      <v-col cols="3">
        <h4>Registration Number</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ content?.documentRegistrationNumber || '(Not Entered)' }}</p>
      </v-col>
      <v-col cols="3">
        <h4>Document ID</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ content?.documentId || '(Not Entered)' }}</p>
      </v-col>

      <template v-if="content?.endDateTime">
        <v-col
          cols="3"
          class="mt-4"
        >
          <h4>To</h4>
        </v-col>
        <v-col
          cols="6"
          class="pl-3 mt-4"
        >
          <p>{{ shortPacificDate(content?.endDateTime) || '(Not Entered)' }}</p>
        </v-col>
        <v-col cols="3">
          <h4>Document Type</h4>
        </v-col>
        <v-col
          cols="6"
          class="pl-3"
        >
          <p>{{ content?.registrationDescription || '(Not Entered)' }}</p>
        </v-col>
        <v-col cols="3">
          <h4>Registration Number</h4>
        </v-col>
        <v-col
          cols="6"
          class="pl-3"
        >
          <p>{{ content?.documentRegistrationNumber || '(Not Entered)' }}</p>
        </v-col>
        <v-col cols="3">
          <h4>Document ID</h4>
        </v-col>
        <v-col
          cols="6"
          class="pl-3"
        >
          <p>{{ content?.documentId || '(Not Entered)' }}</p>
        </v-col>
      </template>
      <template v-else>
        <v-col
          cols="3"
          class="mt-4"
        >
          <h4>To</h4>
        </v-col>
        <v-col
          cols="6"
          class="pl-3 mt-4"
        >
          <p>Current</p>
        </v-col>
      </template>
    </v-row>
  </section>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { LocationIF, RegistrationIF } from '@/interfaces'
import { HomeLocationTypes } from '@/enums'
import { useCountriesProvinces } from '@/composables/address/factories'
import { shortPacificDate } from '@/utils'

/** Props **/
const props = withDefaults(defineProps<{
  content: LocationIF,
  registrations?: Array<RegistrationIF>
}>(), {
  content: null,
  registrations: null
})

const { getCountryName } = useCountriesProvinces()
const isOwnLand = ref(props.registrations?.find(reg => reg.documentId === props.content.documentId)?.ownLand)

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
.v-row {
  min-height: 65px;
  border-top: 1px solid $gray3;
}
p {
  line-height: 2.25rem;
}
.condensed-row {
  p, h4 {
    line-height: 1.25rem;
  }
}
.other-land-content {
  border-top: none;
}
:deep(.v-col-3) {
  flex: 0 0 26.25%;
  max-width: 26.25%;
}
</style>
