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
              <h3 class="headers">Name</h3>
            </v-col>
            <v-col cols="3">
              <h3 class="headers">Mailing Address</h3>
            </v-col>
            <v-col cols="3">
              <h3 class="headers">Email Address</h3>
            </v-col>
            <v-col cols="3">
              <h3 class="headers">Phone Number</h3>
            </v-col>
          </v-row>

          <div class="px-4">
            <v-divider />
          </div>

          <v-row no-gutters class="px-6 py-7">
            <v-col cols="3">
              <v-row no-gutters>
                <v-col cols="1" class="mr-2">
                  <v-icon color="black">
                    mdi-domain
                  </v-icon>
                </v-col>
                <v-col>
                  <p class="first-col pt-1 font-weight-bold">
                    {{ getMhrRegistrationSubmittingParty.businessName || '(Not Entered)' }}
                  </p>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="3">
              <p class="content" v-html="parseAddress()"></p>
            </v-col>
            <v-col cols="3">
              <p class="content">{{getMhrRegistrationSubmittingParty.emailAddress || '(Not Entered)'}}</p>
            </v-col>
            <v-col cols="3">
              <p class="content" v-html="parsePhoneNumber()"></p>
            </v-col>
          </v-row>

          <div class="px-4">
            <v-divider />
          </div>

          <v-row no-gutters class="px-6 py-7">
            <v-col cols="3">
              <p class="first-col">Attention or<br>Reference Number</p>
            </v-col>
            <v-col cols="9">
              <p class="content">{{getMhrAttentionReferenceNum || '(Not Entered)'}}</p>
            </v-col>
          </v-row>
        </section>
      </template>
    </div>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'
import { RouteNames } from '@/enums'
import { useGetters } from 'vuex-composition-helpers'
import { useCountriesProvinces, formatAddress } from '@/composables/address/factories'

export default defineComponent({
  name: 'SubmittingPartyReview',
  components: {},
  props: {},
  setup () {
    const {
      getMhrRegistrationSubmittingParty,
      getMhrAttentionReferenceNum
    } = useGetters<any>([
      'getMhrRegistrationSubmittingParty',
      'getMhrAttentionReferenceNum'
    ])

    const localState = reactive({})

    const parseAddress = () => {
      let address = getMhrRegistrationSubmittingParty.value.address
      if (Object.values(address).every((val) => { return !val })) {
        return '(Not Entered)'
      }
      address = formatAddress(address)
      const street = address.street ? address.street + '<br>' : ''
      const city = address.city ? address.city + ' ' : ''
      const region = address.region ? address.region + ' &nbsp;' : ''
      const postalCode = address.postalCode ? address.postalCode + '<br>' : ''
      const country = address.country ? useCountriesProvinces().getCountryName(address.country) + '<br>' : ''
      const details = address.deliveryInstructions ? '<br><i>' + address.deliveryInstructions + '</i>' : ''
      return `${street}${city}${region}${postalCode}${country}${details}`
    }

    const parsePhoneNumber = () => {
      const phone = getMhrRegistrationSubmittingParty.value
      const phoneNum = phone.phoneNumber
      const ext = phone.phoneExtension ? ' &nbsp;Ext ' + phone.phoneExtension : ''
      if (!phoneNum && !ext) {
        return '(Not Entered)'
      }
      return `${phoneNum}${ext}`
    }

    return {
      RouteNames,
      getMhrRegistrationSubmittingParty,
      getMhrAttentionReferenceNum,
      parseAddress,
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

.headers{
  font-size: 14px;
  color: $gray9;
}
.first-col{
  font-weight: bold;
  font-size: 16px;
  color: $gray9;
}
.content{
  margin-bottom: unset;
  line-height: 24px;
  font-size: 14px;
  color: $gray7;
}
</style>
