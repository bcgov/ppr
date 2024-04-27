<template>
  <v-card
    flat
    class="pt-7"
  >
    <v-row>
      <v-col
        cols="3"
        class="pb-3"
      >
        <label class="generic-label">Transfer Details</label>
      </v-col>
    </v-row>
    <v-row v-if="!isTransferDueToDeath && !isTransferWithoutBillOfSale">
      <v-col cols="3">
        <label class="generic-label">Consideration</label>
      </v-col>
      <v-col
        id="consideration-display"
        cols="9"
        class="gray7"
      >
        {{ getMhrTransferConsideration ? formatCurrency(getMhrTransferConsideration) : '(Not Entered)' }}
      </v-col>
    </v-row>
    <v-row v-if="!isTransferDueToDeath && !isTransferWithoutBillOfSale">
      <v-col cols="3">
        <label class="generic-label">Bill of Sale Date of<br>Execution</label>
      </v-col>
      <v-col
        cols="9"
        class="gray7"
      >
        {{ getMhrTransferDate ? convertDate(getMhrTransferDate, false, false) : '(Not Entered)' }}
      </v-col>
    </v-row>
    <v-row id="lease-land-display">
      <v-col cols="3">
        <label class="generic-label">Lease or Land <br>Ownership</label>
      </v-col>
      <v-col
        cols="9"
        class="gray7"
      >
        <span v-html="landOrLeaseLabel" />
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { convertDate, formatCurrency } from '@/utils'
import { useStore } from '@/store/store'
import { useTransferOwners } from '@/composables'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'TransferDetailsReview',
  components: {},
  props: {
    isMhrTransfer: {
      type: Boolean,
      default: true
    }
  },
  setup () {
    const {
      getMhrTransferConsideration,
      getMhrTransferDate,
      getMhrTransferOwnLand
    } = storeToRefs(useStore())

    const {
      isTransferDueToDeath,
      isTransferBillOfSale,
      isTransferWithoutBillOfSale
    } = useTransferOwners()

    const localState = reactive({
      isNewHomeOwner: computed(() =>
        isTransferBillOfSale.value || isTransferWithoutBillOfSale.value
      ),
      landOrLeaseLabel: computed(() => {
        return `The manufactured home is <b>${!getMhrTransferOwnLand.value ? 'not' : ''}</b> located on land that the
                ${ localState.isNewHomeOwner ? 'new' : ''} homeowners own or on land that they have a registered lease
                of 3 years or more.`
      })
    })

    return {
      isTransferDueToDeath,
      isTransferWithoutBillOfSale,
      getMhrTransferConsideration,
      getMhrTransferDate,
      getMhrTransferOwnLand,
      convertDate,
      formatCurrency,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.col {
  padding-top: 8px !important;
  padding-bottom: 8px;
}
</style>
