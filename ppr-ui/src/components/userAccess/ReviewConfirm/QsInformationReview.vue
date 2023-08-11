<template>
  <PartyReview
    :baseParty="getMhrQsInformation"
    :showIncomplete="!getMhrUserAccessValidation.qsInformationValid"
    :returnToRoutes="[RouteNames.QS_USER_ACCESS, RouteNames.QS_ACCESS_INFORMATION]"
  >
    <!-- Header Override -->
    <template v-slot:headerSlot>
      <header class="review-header">
        <v-icon class="ml-1" color="darkBlue">mdi-account-lock</v-icon>
        <label class="font-weight-bold pl-2">Qualified Supplier ({{ getMhrSubProduct }}) Information</label>
      </header>
    </template>

    <!-- Conditional based on service agreement checkbox -->
    <template v-slot:topInfoSlot>
      <p class="icon-text ml-7 pb-2 mt-8">
        <v-icon color="success" class="pr-2">mdi-check</v-icon>
        I have read, understood and agree to the terms and conditions of the Qualified Suppliers’ Agreement for the
        Manufactured Home Registry.
      </p>
    </template>

  </PartyReview>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'
import { PartyReview } from '@/components/common'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { RouteNames } from '@/enums'

export default defineComponent({
  name: 'QsInformationReview',
  computed: {
    RouteNames () { return RouteNames }
  },
  components: {
    PartyReview
  },
  setup () {
    const {
      getMhrSubProduct,
      getMhrQsInformation,
      getMhrUserAccessValidation
    } = storeToRefs(useStore())

    const localState = reactive({
    })

    return {
      getMhrSubProduct,
      getMhrQsInformation,
      getMhrUserAccessValidation,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.icon-text {
  display: flex;
  align-items: flex-start;
}
</style>
