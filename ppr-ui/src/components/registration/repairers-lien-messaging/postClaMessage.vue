<script setup lang="ts">
import { useStore } from '@/store/store'
const { rlTransitionDate } = storeToRefs(useStore())
</script>
<template>
  <article id="post-cla-messaging">
    <v-row no-gutters>
      <v-col cols="12">
        <h3>
          Personal Property Registry (PPR) update: The new Commercial Lien (CL) registration type is now active.
        </h3>
      </v-col>

      <v-col
        cols="12"
        class="mt-4"
      >
        <p>
          <a
            class="font-weight-regular"
            href="https://www.bclaws.gov.bc.ca/civix/document/id/bills/billsprevious/3rd42nd:gov11-1"
            target="_blank"
          >
            The Commercial Liens Act (CLA) through Bill 11
            <v-icon size="18">mdi-open-in-new</v-icon>
          </a>
          and amendments to the Personal Property Security
          Regulation (PPSR) came into effect on {{ rlTransitionDate }}. The CLA reforms and consolidates
          British Columbia’s law for liens that secure payment on repaired, stored, and transported goods. The
          CLA repeals and replaces the Repairers Lien Act, Livestock Lien Act, Tugboat Worker Lien Act, Warehouse
          Lien Act, and Woodworker Lien Act. PPSR amendments define Commercial Lien registration terms and
          requirements.
        </p>
      </v-col>

      <v-col
        cols="12"
        class="mt-4"
      >
        <p class="font-weight-bold">CLA impact on Repairers Lien (RL):</p>
        <p>No new Repairers Lien registrations may be added to the PPR. A Repairers Lien registered before
          {{ rlTransitionDate }} remains effective for the unexpired registration period and no further action is
          required. You may renew, amend or discharge a Repairers Lien as a Commercial Lien under the CLA.
        </p>
      </v-col>

      <v-col
        cols="12"
        class="mt-4"
      >
        <p>Commercial Liens differ from Repairers Liens in the following ways::</p>
        <ul class="ml-5">
          <li>
            Registration length may be from 1 to 25 years or infinity instead of being a fixed 180 day period
          </li>
          <li>
            A court order is no longer required for renewal
          </li>
          <li>
            Collateral may include a general description of collateral
          </li>
          <li>
            All debtor, secured party and collateral data may be amended
          </li>
          <li>
            Surrender Date and Lien Amount are not available except as read-only historical information from a
            Repairers Lien
          </li>
        </ul>
      </v-col>
    </v-row>
  </article>
</template>
