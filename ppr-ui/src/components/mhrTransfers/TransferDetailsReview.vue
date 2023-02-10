<template>
  <v-card flat class="pt-4">
    <v-row>
      <v-col cols="3" class="pb-22px">
        <label class="generic-label">Transfer Details</label>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="3">
        <label class="generic-label">Declared Value of Home</label>
      </v-col>
      <v-col cols="9" class="gray7" id="declared-value-display">${{ getMhrTransferDeclaredValue }}.00</v-col>
    </v-row>
    <v-row>
      <v-col cols="3">
        <label class="generic-label">Consideration</label>
      </v-col>
      <v-col cols="9" class="gray7" id="consideration-display">{{ getMhrTransferConsideration }}</v-col>
    </v-row>
    <v-row>
      <v-col cols="3">
        <label class="generic-label">Bill of Sale Date of<br/>Execution</label>
      </v-col>
      <v-col cols="9" class="gray7">{{ convertDate(getMhrTransferDate, false, false) }}</v-col>
    </v-row>
    <v-row id="lease-land-display">
      <v-col cols="3">
        <label class="generic-label">Lease or Land <br>Ownership</label>
      </v-col>
      <v-col cols="9" class="gray7">
        <span v-if="getMhrTransferOwnLand">The manufactured home is located on land that the new homeowners own, or on
          which they have a registered lease of 3 years or more.</span>
        <span v-else>The manufactured home is <strong>not</strong> located on land that the new homeowners own, or on
          which they have a registered lease of 3 years or more.</span>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'
import TransferDetails from '@/components/mhrTransfers/TransferDetails.vue'
import { convertDate } from '@/utils'
import { useGetters } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'TransferDetailsReview',
  components: {
    TransferDetails
  },
  props: {
    isMhrTransfer: {
      type: Boolean,
      default: true
    }
  },
  setup (props) {
    const {
      getMhrTransferDeclaredValue,
      getMhrTransferConsideration,
      getMhrTransferDate,
      getMhrTransferOwnLand
    } = useGetters<any>([
      'getMhrTransferDeclaredValue',
      'getMhrTransferConsideration',
      'getMhrTransferDate',
      'getMhrTransferOwnLand'
    ])

    return {
      getMhrTransferDeclaredValue,
      getMhrTransferConsideration,
      getMhrTransferDate,
      getMhrTransferOwnLand,
      convertDate
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.pb-22px {
  padding-bottom: 22px !important;
}
.col {
  padding-top: 8px !important;
  padding-bottom: 8px;
}
</style>
