<template>
  <v-row
    id="court-commission-order-review"
    class="pa-4"
    :class="{'removed-item': hasRemovedOrders || order.action === ActionTypes.REMOVED}"
    no-guttters
  >
    <v-col
      cols="6"
      class="py-0 dp__flex"
    >
      <h4>
        {{ courtCommissionLabel }} Order
      </h4>
      <span>
        <InfoChip
          v-if="isAmendment && !hasAddedParentNotice"
          class="ml-4 py-1"
          :action="order.action"
        />
      </span>
    </v-col>
    <v-col
      cols="6"
      class="py-0 px-0 mx-0 mt-n1"
    >
      <slot name="actions" />
    </v-col>
    <template v-if="order?.courtOrder">
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
      <h4>{{ courtCommissionNumberLabel }} Number</h4>
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
      <p>{{ yyyyMmDdToPacificDate((order.orderDate.split('T')[0]), true) }}</p>
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
      <p>
        {{ order.effectOfOrder || '(Not Entered)' }}
      </p>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CourtOrderIF } from '@/interfaces'
import { yyyyMmDdToPacificDate } from '@/utils'
import { InfoChip } from '@/components/common'
import { ActionTypes } from '@/enums'

/** Props **/
const props = withDefaults(defineProps<{
  order?: CourtOrderIF,
  isAmendment?: boolean,
  hasRemovedOrders?: boolean,
  hasAddedParentNotice?: boolean
}>(), {
  order: null,
  isAmendment: false,
  hasRemovedOrders: false,
  hasAddedParentNotice: false
})

/** Local Properties **/
const courtCommissionLabel = computed(() => props.order?.courtOrder ? 'Court' : 'Securities Commission')
const courtCommissionNumberLabel = computed(() => props.order?.courtOrder ? 'Court File' : 'Commission Order')


</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme';
h4 {
  white-space: nowrap;
}
p {
  font-size: .875rem;
  line-height: 2.25rem;
}
.removed-item {
  h4, p {
    opacity: .5
  }
}
#court-commission-order-review {
  background-color: #F2F6FB;
}
</style>
