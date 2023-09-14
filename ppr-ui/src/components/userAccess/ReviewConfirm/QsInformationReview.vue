<template>
  <PartyReview
    :baseParty="getMhrQsInformation"
    :showNotEntered="getMhrUserAccessValidation.qsSaConfirmValid"
    :showIncomplete="!getMhrUserAccessValidation.qsInformationValid || !getMhrUserAccessValidation.qsSaConfirmValid"
    :returnToRoutes="[RouteNames.QS_USER_ACCESS, RouteNames.QS_ACCESS_INFORMATION]"
  >
    <!-- Header Override -->
    <template #headerSlot>
      <header class="review-header">
        <v-icon class="ml-1" color="darkBlue">mdi-account-lock</v-icon>
        <label class="font-weight-bold pl-2">Qualified Supplier ({{ getMhrSubProduct }}) Information</label>
      </header>
    </template>

    <template #partyInfoLabelSlot>
      <v-row no-gutters class="px-8 pt-6 mb-n2">
        <v-col>
          <label class="generic-label">Qualified Supplier</label>
        </v-col>
      </v-row>
    </template>

    <!-- Conditional based on service agreement checkbox -->
    <template v-if="getMhrUserAccessValidation.qsSaConfirmValid" #topInfoSlot>
      <FormCard label="Service Agreement" class="pb-2">
        <template #infoSlot>
          <p class="icon-text ml-10 mb-n1">
            <v-icon color="success" class="pr-2">mdi-check</v-icon>
            I have read, understood and agree to the terms and conditions of the Qualified Suppliers’ Agreement for the
            Manufactured Home Registry.
          </p>
        </template>
      </FormCard>
    </template>

  </PartyReview>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue-demi'
import { FormCard, PartyReview } from '@/components/common'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { RouteNames } from '@/enums'

export default defineComponent({
  name: 'QsInformationReview',
  components: {
    FormCard,
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
      RouteNames,
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
</style>
