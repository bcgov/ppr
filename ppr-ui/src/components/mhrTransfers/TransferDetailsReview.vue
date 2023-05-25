<template>
  <v-card flat class="pt-4">
    <v-row>
      <v-col cols="3" class="pb-3">
        <label class="generic-label">Transfer Details</label>
      </v-col>
    </v-row>
    <v-row v-if="!isTransferDueToDeath">
      <v-col cols="3">
        <label class="generic-label">Consideration</label>
      </v-col>
      <v-col cols="9" class="gray7" id="consideration-display">{{ getMhrTransferConsideration }}</v-col>
    </v-row>
    <v-row v-if="!isTransferDueToDeath">
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
        <span v-html="landOrLeaseLabel"></span>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { convertDate } from '@/utils'
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
      isTransferToExecutorProbateWill
    } = useTransferOwners()

    const localState = reactive({
      landOrLeaseLabel: computed(() => {
        return `The manufactured home is <b>${!getMhrTransferOwnLand.value ? 'not' : ''}</b> located on land that the
            ${!isTransferDueToDeath.value || isTransferToExecutorProbateWill.value ? 'new' : ''} homeowners own, or
            on which they have a registered lease of 3 years or more.`
      })
    })

    return {
      isTransferDueToDeath,
      getMhrTransferConsideration,
      getMhrTransferDate,
      getMhrTransferOwnLand,
      convertDate,
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
