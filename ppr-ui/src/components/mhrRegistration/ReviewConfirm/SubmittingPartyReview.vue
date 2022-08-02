<template>
  <v-card flat id="submitting-party-summary" class="mt-6 pb-6">
    <header class="review-header">
      <v-icon class="ml-2" color="darkBlue">mdi-account</v-icon>
      <label class="font-weight-bold pl-2">Submitting Party</label>
    </header>

    <div :class="{ 'invalid-section': false }">
      <section class="mx-6 pt-8" v-if="true">
        <span>
          <v-icon color="error">mdi-information-outline</v-icon>
          <span class="error-text mx-1">This step is unfinished.</span>
          <router-link
            :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.SUBMITTING_PARTY}` }"
          >Return to this step to complete it.</router-link>
        </span>
      </section>

      <!-- -->
      <template>
        <section class="pt-6" id="review-submitting-party-section">
          <!-- Insert Review mode of component here -->
          <v-row no-gutters class="px-6 pb-7">
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

          <div class="px-4">
            <v-divider />
          </div>

          <v-row no-gutters class="px-6 py-7">
            <v-col cols="3">
              <v-row no-gutters>
                <v-col cols="1" class="mr-2">
                  <v-icon class="side-header-icon">
                    {{getMhrRegistrationSubmittingParty.businessName ? 'mdi-domain' : 'mdi-account'}}
                  </v-icon>
                </v-col>
                <v-col>
                  <p class="side-header pt-1 font-weight-bold">
                    {{ getSubmittingPartyName() }}
                  </p>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="3" class="pl-1">
              <base-address
                v-if="hasAddress"
                class="content"
                :schema="addressSchema"
                :value="address"
              >
              </base-address>
              <p v-else class="content"> (Not Entered) </p>
            </v-col>
            <v-col cols="3" class="pl-3">
              <p class="content">{{getMhrRegistrationSubmittingParty.emailAddress || '(Not Entered)'}}</p>
            </v-col>
            <v-col cols="3" class="pl-4">
              <p class="content" v-html="parsePhoneNumber()"></p>
            </v-col>
          </v-row>

          <div class="px-4">
            <v-divider />
          </div>

          <v-row no-gutters class="px-6 py-7">
            <v-col cols="3">
              <p class="side-header">Attention or<br>Reference Number</p>
            </v-col>
            <v-col cols="9">
              <p class="content ref-text">{{getMhrAttentionReferenceNum || '(Not Entered)'}}</p>
            </v-col>
          </v-row>
        </section>
      </template>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { RouteNames } from '@/enums'
import { useGetters } from 'vuex-composition-helpers'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { toDisplayPhone } from '@/utils'

export default defineComponent({
  name: 'SubmittingPartyReview',
  components: {
    BaseAddress
  },
  props: {},
  setup () {
    const {
      getMhrRegistrationSubmittingParty,
      getMhrAttentionReferenceNum
    } = useGetters<any>([
      'getMhrRegistrationSubmittingParty',
      'getMhrAttentionReferenceNum'
    ])

    const localState = reactive({
      address: computed(() => getMhrRegistrationSubmittingParty.value.address),
      businessName: computed(() => getMhrRegistrationSubmittingParty.value.businessName),
      personName: computed(() => getMhrRegistrationSubmittingParty.value.personName),
      hasAddress: computed(() => !Object.values(localState.address).every(val => !val))
    })

    const addressSchema = PartyAddressSchema

    const parsePhoneNumber = () => {
      const phone = getMhrRegistrationSubmittingParty.value
      const phoneNum = phone.phoneNumber
      const ext = phone.phoneExtension ? ' &nbsp;Ext ' + phone.phoneExtension : ''
      return phoneNum ? `${toDisplayPhone(phoneNum)}${ext}` : '(Not Entered)'
    }

    const getSubmittingPartyName = () => {
      if (!localState.businessName && Object.values(localState.personName).every(val => !val)) {
        return '(Not Entered)'
      } else {
        if (localState.businessName) {
          return localState.businessName
        } else {
          return localState.personName.middle
            ? localState.personName.first + ' ' + localState.personName.middle + ' ' + localState.personName.last
            : localState.personName.first + ' ' + localState.personName.last
        }
      }
    }

    return {
      RouteNames,
      addressSchema,
      getMhrRegistrationSubmittingParty,
      getMhrAttentionReferenceNum,
      getSubmittingPartyName,
      parsePhoneNumber,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.review-header {
  display: flex; // to align icons
  background-color: $BCgovBlue5O;
  padding: 1.25rem;
  color: $gray9;
}

.error-text {
  font-size: 16px;
}

.ref-text {
  font-size: 16px !important;
}

.table-header {
  font-size: 14px;
  color: $gray9;
}

.side-header {
  font-weight: bold;
  font-size: 16px;
  color: $gray9;
}

.side-header-icon {
  color: $gray9;
}

.content {
  margin-bottom: unset;
  line-height: 24px;
  font-size: 14px;
  color: $gray7;
}
</style>
