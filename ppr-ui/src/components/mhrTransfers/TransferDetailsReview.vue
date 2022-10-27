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
      <v-col cols="9" class="gray7" id="declared-value-display">${{ declaredValue }}.00</v-col>
    </v-row>
    <v-row>
      <v-col cols="3">
        <label class="generic-label">Consideration</label>
      </v-col>
      <v-col cols="9" class="gray7" id="consideration-display">{{ consideration }}</v-col>
    </v-row>
    <v-row>
      <v-col cols="3">
        <label class="generic-label"
          >Bill of Sale Date of <br />
          Execution</label
        >
      </v-col>
      <v-col cols="9" class="gray7">{{ transferDate }}</v-col>
    </v-row>
    <v-row v-if="isOwnLand" id="lease-land-display">
      <v-col cols="3">
        <label class="generic-label"
          >Lease or Land<br />
          Ownership</label
        >
      </v-col>
      <v-col cols="9" class="gray7"
        >The manufactured home is located on land the new homeowners own, or on which they have a registered lease of 3
        years or more.
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'
import { useMhrInformation } from '@/composables'
import TransferDetails from '@/components/mhrTransfers/TransferDetails.vue'
import moment from 'moment'

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
    const { getTransferDetails } = useMhrInformation()

    const formatDate = (inputDate: string) => {
      return moment(inputDate).format('MMMM D, YYYY')
    }

    const localState = reactive({
      declaredValue: getTransferDetails().declaredValue,
      consideration: getTransferDetails().consideration,
      transferDate: formatDate(getTransferDetails().transferDate),
      isOwnLand: getTransferDetails().transferOwnLand
    })

    return {
      getTransferDetails,
      formatDate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.gray7 {
  color: $gray7;
}
.pb-22px {
  padding-bottom: 22px !important;
}
.col {
  padding-top: 8px !important;
  padding-bottom: 8px;
}
</style>
