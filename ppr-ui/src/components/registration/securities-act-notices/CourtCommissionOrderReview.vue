<template>
  <v-row
    id="court-commission-order-review"
    class="pa-4"
    noGuttters
  >
    <v-col
      cols="3"
      class="py-0"
    >
      <h4>{{ courtCommissionLabel }} Order</h4>
    </v-col>
    <v-col
      cols="9"
      class="py-0 px-0 mx-0 mt-n1"
    >
      <slot name="actions" />
    </v-col>
    <template v-if="props.order?.courtOrder">
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
    </template>
    <v-col
      cols="3"
      class="pt-1 pb-0 mb-0"
    >
      <h4>{{ courtCommisionNumberLabel }} Number</h4>
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
      <p class="effect-of-order-text">
        {{ order.effectOfOrder || '(Not Entered)' }}
      </p>
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
const courtCommissionLabel = computed(() => props.order?.courtOrder ? 'Court' : 'Securities Commission')
const courtCommisionNumberLabel = computed(() => props.order?.courtOrder ? 'Court File' : 'Commission Order')


</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
p {
  font-size: .875rem;
  line-height: 2.25rem;
}
.effect-of-order-text {
  line-height: 22px;
}
#court-commission-order-review {
  background-color: #F2F6FB;
}
</style>
