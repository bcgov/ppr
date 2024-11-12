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
        <v-icon
          class="ml-1"
          color="darkBlue"
        >
          mdi-account-lock
        </v-icon>
        <label class="font-weight-bold pl-2">Qualified Supplier ({{ getMhrSubProduct }}) Information</label>
      </header>
    </template>

    <!-- Conditional based on service agreement checkbox -->
    <template
      v-if="getMhrUserAccessValidation.qsSaConfirmValid"
      #topInfoSlot
    >
      <FormCard
        label="Qualified Suppliers’ Agreement"
        class="pb-2"
      >
        <template #infoSlot>
          <p class="icon-text mb-n1">
            <v-icon
              color="success"
              class="pr-2"
            >
              mdi-check
            </v-icon>
            I have read, understood and agree to the terms and conditions of the Qualified Suppliers’ Agreement for the
            Manufactured Home Registry.
          </p>
        </template>
      </FormCard>
    </template>

    <template #partyInfoLabelSlot>
      <v-row
        noGutters
        class="px-8 pt-6 mb-n2"
      >
        <v-col>
          <label class="generic-label">Qualified Supplier</label>
        </v-col>
      </v-row>
    </template>

    <template
      v-if="[MhrSubTypes.MANUFACTURER, MhrSubTypes.DEALERS].includes(getMhrSubProduct)"
      #bottomInfoSlot
    >
      <article class="px-8">
        <v-card
          v-if="getMhrSubProduct === MhrSubTypes.MANUFACTURER"
          class="read-only-container"
          flat
        >
          <p>
            <span class="font-weight-bold">Note:</span> Your manufacturer name(s) will appear in registration documents
            as the following:
          </p>
          <p class="font-weight-bold mt-3">
            Registered Owner
          </p>
          <p>
            {{ getMhrQsInformation.businessName || '(Not Entered)' }}
          </p>
          <p class="font-weight-bold mt-3">
            Registered Location and Description of Manufactured Home
          </p>
          <p>
            {{ getMhrQsInformation.businessName || '(Not Entered)' }}
            {{ getMhrQsInformation.dbaName ? ` / ${getMhrQsInformation.dbaName} ` : '' }}
          </p>
        </v-card>

        <v-divider
          v-if="getMhrSubProduct === MhrSubTypes.DEALERS"
          class="mx-0"
        />

        <h3 class="mt-4">
          Location of Manufactured Home(s)
        </h3>
      </article>


      <FormCard
        label="Civic Address"
        class="pt-3"
      >
        <template #formSlot>
          <BaseAddress
            v-if="hasTruthyValue(getMhrQsHomeLocation)"
            :value="getMhrQsHomeLocation"
          />
          <p v-else>
            (Not Entered)
          </p>
        </template>
      </FormCard>
    </template>
  </PartyReview>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { FormCard, PartyReview } from '@/components/common'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { MhrSubTypes, RouteNames } from '@/enums'
import { hasTruthyValue } from '@/utils'
import BaseAddress from '@/composables/address/BaseAddress.vue'

export default defineComponent({
  name: 'QsInformationReview',
  components: {
    BaseAddress,
    FormCard,
    PartyReview
  },
  setup () {
    const {
      getMhrSubProduct,
      getMhrQsInformation,
      getMhrQsHomeLocation,
      getMhrUserAccessValidation
    } = storeToRefs(useStore())

    return {
      RouteNames,
      MhrSubTypes,
      hasTruthyValue,
      getMhrSubProduct,
      getMhrQsInformation,
      getMhrQsHomeLocation,
      getMhrUserAccessValidation
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
