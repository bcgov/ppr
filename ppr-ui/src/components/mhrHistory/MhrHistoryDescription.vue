<template>
  <section
    id="mhr-history-description"
    class="pr-4"
  >
    <v-row class="ma-0">
      <v-col
        cols="3"
        class="pl-0"
      >
        <h4>Year of Manufacture</h4>
      </v-col>
      <v-col>
        <p>{{ content?.baseInformation?.year || '(Not Entered)' }}</p>
      </v-col>
    </v-row>

    <v-row
      v-if="content?.csaNumber"
      noGutters
      class="py-3"
    >
      <v-col cols="3">
        <h4>CSA Number</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ content?.csaNumber || '(Not Entered)' }}</p>
      </v-col>
      <v-col cols="3">
        <h4>CSA Standard</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ content?.csaStandard || '(Not Entered)' }}</p>
      </v-col>
    </v-row>

    <v-row
      v-else-if="content?.engineerName"
      noGutters
      class="py-3"
    >
      <v-col cols="3">
        <h4>Engineer's Name</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ content?.engineerName || '(Not Entered)' }}</p>
      </v-col>
      <v-col cols="3">
        <h4>Date of Engineer's Report</h4>
      </v-col>
      <v-col
        cols="6"
        class="pl-3"
      >
        <p>{{ shortPacificDate(content?.engineerDate) || '(Not Entered)' }}</p>
      </v-col>
    </v-row>

    <v-row
      v-else
      noGutters
      class="py-3"
    >
      <v-col cols="3">
        <h4>Home Certification</h4>
      </v-col>
      <v-col class="pl-3">
        <p>{{ 'There is no certification available for this home.' }}</p>
      </v-col>
    </v-row>

    <v-row class="ma-0">
      <v-col
        cols="12"
        class="pl-0"
      >
        <h4>Home Sections</h4>
        <HomeSectionsTable
          class="mt-n3"
          :homeSections="content?.sections"
          :isReviewMode="true"
        />
      </v-col>
    </v-row>

    <v-row class="ma-0">
      <v-col
        cols="3"
        class="pl-0"
      >
        <h4>Rebuilt Status</h4>
      </v-col>
      <v-col>
        <p>{{ content?.rebuiltRemarks || '(Not Entered)' }}</p>
      </v-col>
    </v-row>

    <v-row class="ma-0">
      <v-col
        cols="3"
        class="pl-0"
      >
        <h4>Other Information</h4>
      </v-col>
      <v-col>
        <p>{{ content?.otherRemarks || '(Not Entered)' }}</p>
      </v-col>
    </v-row>

    <v-row
      noGutters
      class="py-6 condensed-row"
    >
      <v-col cols="3">
        <h4>Registration Date</h4>
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
    </v-row>
  </section>
</template>

<script setup lang="ts">
import { HomeSectionsTable } from '@/components/tables/mhr'
import { DescriptionIF } from '@/interfaces'
import { shortPacificDate } from '@/utils'

/** Props **/
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(defineProps<{
  content: DescriptionIF
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
p {
  line-height: 2.25rem;
}
.condensed-row {
  p, h4 {
    line-height: 1.5rem;
  }
}
:deep(.v-col-3) {
  flex: 0 0 26.25%;
  max-width: 26.25%;
}
:deep(#mh-home-sections-table) {
  .column-mdl {
    width: 26.25%
  }
}
</style>
