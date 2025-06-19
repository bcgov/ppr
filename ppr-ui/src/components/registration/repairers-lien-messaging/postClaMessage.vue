<script setup lang="ts">
import { useStore } from '@/store/store'
const { rlTransitionDate } = storeToRefs(useStore())
</script>
<template>
  <article id="post-cla-messaging">
    <v-row no-gutters>
      <v-col cols="12">
        <h3>
          Personal Property Registry update: Commercial Lien (CL) registrations are now active.
        </h3>
      </v-col>

      <v-col
        cols="12"
        class="mt-4"
      >
        <p>
          <a
            class="font-weight-regular"
            href="https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/22009"
            target="_blank"
          >
            The Commercial Liens Act (CLA)
          </a>and
          <a
            class="font-weight-regular"
            href="https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/227_2002"
            target="_blank"
          >
            amendments
          </a>
          Personal Property Security Regulation (PPSR) amendments are now active. The
          CLA reforms and consolidates British Columbia’s law for liens that secure payment on repaired, stored, and
          transported goods, replacing the Repairers Lien Act, Warehouse Lien Act, and Livestock Lien Act. PPSR
          amendments define Commercial Lien registration terms and requirements.
        </p>
      </v-col>

<!--      <v-col-->
<!--        cols="12"-->
<!--        class="mt-4"-->
<!--      >-->
<!--        <p>-->
<!--          <b>Need help?</b> For step-by-step instructions, refer to our-->
<!--          <a-->
<!--            class="font-weight-regular"-->
<!--            href="https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/22009"-->
<!--            target="_blank"-->
<!--          >-->
<!--            Commercial Liens User Guide-->
<!--          </a>-->
<!--        </p>-->

<!--        <v-divider class="mt-3" />-->
<!--      </v-col>-->

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
        <p>Commercial Liens differ from Repairers Liens in the following ways:</p>
        <ul class="ml-5 mt-4">
          <li>
            Registration length may be from 1 to 25 years or infinity instead of being a fixed 180 day period
          </li>
          <li>
            A court order is no longer required for renewal
          </li>
          <li>
            Collateral may include serial numbered goods and a general description of collateral
          </li>
          <li>
            Serial numbered goods may include a manufactured home
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
