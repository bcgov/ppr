<template>
  <div id="account-info">
    <h4 class="header mb-5">
      {{ title }}
      <v-tooltip
        if="tooltipContent"
        location="top"
        nudge-right="3"
        content-class="top-tooltip pa-5"
        transition="fade-transition"
        data-test-id="submitting-party-tooltip"
      >
        <template #activator="{ on }">
          <v-icon
            class="mt-n1"
            color="primary"
            v-on="on"
          >
            mdi-information-outline
          </v-icon>
        </template>
        {{ tooltipContent }}
      </v-tooltip>
      <p class="fs-16">
        {{ desc }}
      </p>
    </h4>
    <v-card
      flat
      class="rounded"
    >
      <v-table
        v-if="accountInfo"
        data-test-id="account-info-table"
      >
        <template #default>
          <thead>
            <tr>
              <th class="pl-8 py-4">
                Name
              </th>
              <th class="py-4">
                Mailing Address
              </th>
              <th class="py-4">
                Email Address
              </th>
              <th class="py-4">
                Phone Number
              </th>
            </tr>
          </thead>
          <tbody>
            <tr class="table-info">
              <td class="account-name pl-8 py-6">
                <v-icon class="mt-n2">
                  {{ accountInfo.isBusinessAccount ? 'mdi-domain' : 'mdi-account' }}
                </v-icon>
                <span class="pt-1 font-weight-bold">
                  {{ accountInfo.name }}
                </span>
              </td>
              <td class="py-6">
                <BaseAddress
                  id="submitting-party-address"
                  :schema="PartyAddressSchema"
                  :value="accountInfo.mailingAddress"
                />
              </td>
              <td class="py-6">
                {{ accountInfo.accountAdmin.email }}
              </td>
              <td class="py-6">
                {{ toDisplayPhone(accountInfo.accountAdmin.phone) }}
                <span v-if="accountInfo.accountAdmin.phoneExtension">
                  Ext {{ accountInfo.accountAdmin.phoneExtension }}
                </span>
              </td>
            </tr>
          </tbody>
        </template>
      </v-table>
    </v-card>
  </div>
</template>

<script lang="ts">
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { defineComponent } from 'vue'
import { toDisplayPhone } from '@/utils'
import { AccountInfoIF, PartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars

export default defineComponent({
  name: 'AccountInfo',
  components: { BaseAddress },
  props: {
    title: {
      type: String,
      required: true
    },
    tooltipContent: {
      type: String,
      default: null
    },
    accountInfo: {
      type: Object as () => AccountInfoIF,
      required: true
    },
    desc: {
      type: String,
      default: null
    }
  },
  setup () {
    return { PartyAddressSchema, toDisplayPhone }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.table-info {
  vertical-align: top;
  .account-name,
  i {
    color: $gray9 !important;
    span {
      padding-left: 2px;
    }
  }
}
</style>
