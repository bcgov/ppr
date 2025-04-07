<template>
  <section
    id="mhr-history-owners"
    class="pr-4"
  >
    <v-row
      no-gutters
      class="condensed-row pt-5"
    >
      <p>
        <span class="generic-label-14">Tenancy Type:</span>
        {{ content.type }}
        <v-divider
          v-if="content.type === HomeTenancyTypes.COMMON"
          vertical
        />
      </p>
      <template v-if="content.type === HomeTenancyTypes.COMMON">
        <p>
          <span class="generic-label-14">Group:</span>
          {{ content.groupId }} of {{ content.groupCount }} <v-divider vertical />
        </p>
        <p>
          <span class="generic-label-14">Owner:</span>
          {{ content.ownerId }} of {{ content.groupOwnerCount }} <v-divider vertical />
        </p>
        <p>
          <span class="generic-label-14">Group Tenancy Type:</span>
          {{ content.groupTenancyType }}
          <v-divider vertical />
        </p>
        <p>
          <span class="generic-label-14">Interest:</span>
          {{ content.interest }} {{ content.interestNumerator }}/{{ content.interestDenominator }}
        </p>
      </template>
    </v-row>

    <v-row
      no-gutters
      class="condensed-row py-3"
    >
      <v-col cols="3">
        <h4>Mailing Address</h4>
        <BaseAddress :value="content.address" />
      </v-col>
      <v-col
        cols="3"
        class="pl-3"
      >
        <h4>Phone Number</h4>
        <p>
          {{ content.phoneNumber || '(Not Entered)' }}
          {{ content.phoneExtension ? `Ext ${content.phoneExtension}` : '' }}
        </p>
      </v-col>
      <v-col cols="3">
        <h4>Email Address</h4>
        <p>{{ content.emailAddress || '(Not Entered)' }}</p>
      </v-col>
    </v-row>

    <!-- Owner From/Until Details -->
    <v-row
      no-gutters
      class="py-6 condensed-row"
    >
      <v-col cols="3">
        <h4>Owned From</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ pacificDate(content?.createDateTime, true) || '(Not Entered)' }}</p>
      </v-col>
      <v-col cols="3">
        <h4>Document Type</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ multipleWordsToTitleCase(content?.registrationDescription, false) }}</p>
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
          <h4>Owned Until</h4>
        </v-col>
        <v-col
          cols="6"
          class="pl-3 mt-4"
        >
          <p>{{ pacificDate(content?.endDateTime, true) || '(Not Entered)' }}</p>
        </v-col>
        <v-col cols="3">
          <h4>Document Type</h4>
        </v-col>
        <v-col
          cols="6"
          class="pl-3"
        >
          <p>{{ multipleWordsToTitleCase(content?.registrationDescription, false) }}</p>
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
          <h4>Owned Until</h4>
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
import type { OwnerIF } from '@/interfaces'
import { BaseAddress } from '@/composables/address'
import { multipleWordsToTitleCase, pacificDate } from '@/utils'
import { HomeTenancyTypes } from '@/enums'

/** Props **/

const props = withDefaults(defineProps<{
  content?: OwnerIF
}>(), {
  content: null
})

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
.v-row {
  min-height: 65px;
  border-top: 1px solid $gray3;
}
.condensed-row {
  p, h4 {
    line-height: 1.5rem;
  }
}
:deep(.v-divider) {
  height: 14px;
  color: $gray3;
  margin: 0 20px;
  opacity: 1;
}
:deep(.v-col-3) {
  flex: 0 0 26.25%;
  max-width: 26.25%;
}
</style>
