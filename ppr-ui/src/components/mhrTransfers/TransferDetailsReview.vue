<template>
  <v-card flat class="py-6 pt-4 px-8 rounded">
    <v-row>
      <v-col cols="3">
        <label class="generic-label">Home Owners</label>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="3">
        <label class="generic-label">Home Tenancy Type</label>
      </v-col>
      <v-col cols="9">{{getHomeTenancyType()}}</v-col>
    </v-row>

    <HomeOwnersTable
      isMhrTransfer
      isReadonlyTable
      class="mt-n2"
      :homeOwners="reviewOwners"
      :currentHomeOwners="getMhrTransferCurrentHomeOwners"
    />
    <v-row>
      <v-col cols="3">
        <label class="generic-label">Transfer Details</label>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="3">
        <label class="generic-label">Declared Value of Home</label>
      </v-col>
      <v-col cols="9">{{ getTransferDetails().declaredValue }}</v-col>
    </v-row>
    <v-row>
      <v-col cols="3">
        <label class="generic-label">Consideration</label>
      </v-col>
      <v-col cols="9">{{ getTransferDetails().consideration }}</v-col>
    </v-row>
    <v-row>
      <v-col cols="3">
        <label class="generic-label">Bill of Sale Date of <br> Execution</label>
      </v-col>
      <v-col cols="9">{{ getTransferDetails().transferDate }}</v-col>
    </v-row>
    <v-row v-if="getTransferDetails().transferOwnLand">
      <v-col cols="3">
        <label class="generic-label">Lease or Land<br> Ownership</label>
      </v-col>
      <v-col cols="9" class="mt-0 pt-0">The manufactured home is located on land the new homeowners own, or on
        which they have a registered lease of 3 years or more.
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, toRefs, reactive, computed } from '@vue/composition-api'
import { useMhrInformation, useHomeOwners } from '@/composables'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import TransferDetails from '@/components/mhrTransfers/TransferDetails.vue'
import { HomeOwners } from '@/views'
import { useGetters } from 'vuex-composition-helpers'
import { ActionTypes } from '@/enums'

export default defineComponent({
  name: 'TransferDetailsReview',
  components: {
    HomeOwners,
    TransferDetails,
    HomeOwnersTable
  },
  props: {
    isMhrTransfer: {
      type: Boolean,
      default: true
    }
  },
  setup (props, context) {
    const { getTransferDetails } = useMhrInformation()
    const {
      getHomeTenancyType
    } = useHomeOwners(props.isMhrTransfer)
    const { getMhrTransferHomeOwners, getMhrTransferCurrentHomeOwners } = useGetters<any>([
      'getMhrTransferHomeOwners',
      'getMhrTransferCurrentHomeOwners'
    ])
    const localState = reactive({
      reviewOwners: computed(() => {
        return getMhrTransferHomeOwners.value.filter(owner => owner.action !== ActionTypes.REMOVED)
      })
    })

    return {
      getMhrTransferHomeOwners,
      getMhrTransferCurrentHomeOwners,
      getTransferDetails,
      getHomeTenancyType,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.pb-60px {
  padding-bottom: 60px;
}
</style>
