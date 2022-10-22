<template>
  <div class="mhr-transfer-details">
    <h4 class="header">{{ title }}</h4>
    <v-card flat class="rounded">
      <v-row no-gutters class="px-6 py-4">
        <v-col cols="3">
          <h3 class="table-header">Name</h3>
        </v-col>
        <v-col cols="3" class="pl-1">
          <h3 class="table-header">Mailing Address</h3>
        </v-col>
        <v-col cols="3" class="pl-3">
          <h3 class="table-header">Email Address</h3>
        </v-col>
        <v-col cols="3" class="pl-4">
          <h3 class="table-header">Phone Number</h3>
        </v-col>
      </v-row>
      <v-row no-gutters class="">
        <v-divider />
      </v-row>
      <v-row no-gutters class="px-6 py-7">
        <v-col cols="3">
          <v-row no-gutters>
            <v-col cols="1" class="mr-2">
              <v-icon class="side-header-icon">
                {{ userInfo.businessName ? 'mdi-domain' : 'mdi-account' }}
              </v-icon>
            </v-col>
            <v-col>
              <p class="side-header pt-1 font-weight-bold">
                {{
                  userInfo.businessName
                    ? userInfo.businessName
                    : `${userInfo.personName.first} ${userInfo.personName.middle || ''} ${userInfo.personName.last}`
                }}
              </p>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="3" class="pl-1">
          <BaseAddress id="submitting-party-address" :schema="PartyAddressSchema" :value="address" />
        </v-col>
        <v-col cols="3" class="pl-3">
          <p class="content">{{ userInfo.emailAddress }}</p>
        </v-col>
        <v-col cols="3" class="pl-4">
          {{ toDisplayPhone(userInfo.phoneNumber) }}
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script lang="ts">
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { SubmittingPartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { AddressIF } from '@bcrs-shared-components/interfaces' // eslint-disable-line no-unused-vars
import { defineComponent } from '@vue/composition-api'
import { toDisplayPhone } from '@/utils'

export default defineComponent({
  name: 'CurrentUser',
  components: { BaseAddress },
  props: {
    title: {
      type: String,
      required: true
    },
    userInfo: {
      type: Object as () => SubmittingPartyIF,
      required: true
    },
    address: {
      type: Object as () => AddressIF,
      required: true
    }
  },
  setup () {
    return { PartyAddressSchema, toDisplayPhone }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
