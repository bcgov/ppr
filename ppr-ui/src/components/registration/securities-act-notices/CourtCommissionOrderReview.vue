<template>
  <v-row
    id="court-commission-order-review"
    class="pa-4"
    noGuttters
  >
    <v-col
      cols="12"
      class="py-0"
    >
      <h4>{{ courtCommissionLabel }}</h4>
    </v-col>
    <v-col
      cols="3"
      class="pt-1 pb-0 mb-0"
    >
      <h4>Court Name</h4>
    </v-col>
    <v-col
      cols="9"
      class="pt-1 pb-0 mb-0"
    >
      <p>{{ order.courtName }}</p>
    </v-col>
    <v-col
      cols="3"
      class="pt-1 pb-0 mb-0"
    >
      <h4>Court Registry</h4>
    </v-col>
    <v-col
      cols="9"
      class="pt-1 pb-0 mb-0"
    >
      <p>{{ order.courtRegistry }}</p>
    </v-col>
    <v-col
      cols="3"
      class="pt-1 pb-0 mb-0"
    >
      <h4>Court File Number</h4>
    </v-col>
    <v-col
      cols="9"
      class="pt-1 pb-0 mb-0"
    >
      <p>{{ order.fileNumber }}</p>
    </v-col>
    <v-col
      cols="3"
      class="pt-1 pb-0 mb-0"
    >
      <h4>Date of Order</h4>
    </v-col>
    <v-col
      cols="9"
      class="pt-1 pb-0 mb-0"
    >
      <p>{{ yyyyMmDdToPacificDate(order.orderDate, true) }}</p>
    </v-col>
    <v-col
      cols="3"
      class="pt-1 pb-0 mb-0"
    >
      <h4>Effect of Order</h4>
    </v-col>
    <v-col
      cols="9"
      class="pt-1 pb-0 mb-0"
    >
      <p>{{ order.effectOfOrder || '(Not Entered)' }}</p>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CourtOrderIF } from '@/interfaces'
import { yyyyMmDdToPacificDate } from '@/utils'

/** Props **/
const props = withDefaults(defineProps<{
  order: CourtOrderIF
}>(), {
  order: null
})

/** Local Properties **/
const courtCommissionLabel = computed(() => props.order?.courtOrder ? 'Court Order' : 'Commission Order')

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
p {
  font-size: .875rem;
  line-height: 2.25rem;
}
#court-commission-order-review {
  background-color: #F2F6FB;
}
</style>
