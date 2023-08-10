<template>
  <v-card flat id="" class="mt-10">
    <header class="review-header">
      <v-icon class="ml-1" color="darkBlue">mdi-account</v-icon>
      <label class="font-weight-bold pl-2">{{ headerLabel }}</label>
    </header>

    <div :class="{ 'border-error-left': false }">
      <section  v-if="false" class="mx-6 pt-8" :class="{ 'pb-8': !hasData }">
        <span>
          <v-icon color="error">mdi-information-outline</v-icon>
          <span class="error-text mx-1">This step is unfinished.</span>
          <router-link
              :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.SUBMITTING_PARTY}` }"
          >Return to this step to complete it.</router-link>
        </span>
      </section>

      <!-- -->
      <template v-if="hasData">
        <section id="">
          <!-- Insert Review mode of component here -->
          <v-row no-gutters class="px-6 pb-5 pt-6">
            <v-col v-if="hasPropData('businessName')" cols="3">
              <h3 class="table-header">Name</h3>
            </v-col>
            <v-col v-if="hasPropData('address')" cols="3" class="pl-1">
              <h3 class="table-header">Mailing Address</h3>
            </v-col>
            <v-col v-if="hasPropData('emailAddress')" cols="3" class="pl-3">
              <h3 class="table-header">Email Address</h3>
            </v-col>
            <v-col v-if="hasPropData('phoneNumber')" cols="3" class="pl-4">
              <h3 class="table-header">Phone Number</h3>
            </v-col>
          </v-row>

          <v-divider class="mx-4"/>

          <v-row no-gutters class="px-6 py-7">
            <v-col cols="3">
              <v-row no-gutters>
                <v-col cols="1" class="mr-2">
                  <v-icon class="side-header-icon">
<!--                    {{getMhrRegistrationSubmittingParty.businessName ? 'mdi-domain' : 'mdi-account'}}-->
                  </v-icon>
                </v-col>
                <v-col>
                  <p class="submitting-name">
<!--                    {{ getSubmittingPartyName() }}-->
                  </p>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="3" class="pl-1">
              <base-address
                  v-if="false"
                  class="content"
                  :schema="addressSchema"
                  :value="null"
              >
              </base-address>
              <p v-else class="content"> (Not Entered) </p>
            </v-col>
            <v-col cols="3" class="pl-3">
              <p class="content">
<!--                {{getMhrRegistrationSubmittingParty.emailAddress || emptyText }}-->
              </p>
            </v-col>
            <v-col cols="3" class="pl-4">
<!--              <p class="content" v-html="parsePhoneNumber()"></p>-->
            </v-col>
          </v-row>

<!--          <template v-if="!isMhrManufacturerRegistration">-->
<!--            <v-divider class="mx-4"/>-->

<!--            <v-row no-gutters class="px-6 py-7">-->
<!--              <v-col cols="3">-->
<!--                <h3>Document ID</h3>-->
<!--              </v-col>-->
<!--              <v-col cols="9">-->
<!--                <p class="content ref-text">{{getMhrRegistrationDocumentId || emptyText }}</p>-->
<!--              </v-col>-->
<!--            </v-row>-->

<!--            <v-divider class="mx-4"/>-->

<!--            <v-row no-gutters class="px-6 py-7">-->
<!--              <v-col cols="3">-->
<!--                <p class="side-header">{{ attnOrRefConfig.title }}</p>-->
<!--              </v-col>-->
<!--              <v-col cols="9">-->
<!--                <p class="content ref-text">{{getMhrAttentionReference || emptyText }}</p>-->
<!--              </v-col>-->
<!--            </v-row>-->

<!--          </template>-->
        </section>
      </template>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { RouteNames } from '@/enums'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { PartyIF } from '@/interfaces'

export default defineComponent({
  name: 'PartyReview',
  components: {
    BaseAddress
  },
  props: {
    baseParty: {
      type: Object as () => PartyIF,
      required: true
    },
    headerLabel: {
      type: String,
      default: 'Party Review'
    }
  },
  setup (props) {
    const localState = reactive({
      partyModel: props.baseParty as PartyIF,
      // address: computed(() => getMhrRegistrationSubmittingParty.value.address),
      // businessName: computed(() => getMhrRegistrationSubmittingParty.value.businessName),
      // personName: computed(() => getMhrRegistrationSubmittingParty.value.personName),
      // hasAddress: computed(() => hasTruthyValue(localState.address)),
      // attnOrRefConfig: computed((): AttnRefConfigIF => isRoleStaffReg.value ? attentionConfig : folioOrRefConfig),
      // emptyText: computed(() => isMhrManufacturerRegistration.value ? '' : '(Not Entered)'),
      // showStepError: computed(() => {
      //   return !isMhrManufacturerRegistration.value && !getStepValidation(MhrSectVal.SUBMITTING_PARTY_VALID)
      // }),
      hasData: computed(() : boolean => {
        return true
      })
    })

    const hasPropData = (propertyName: string): boolean => {
      return localState.partyModel?.hasOwnProperty(propertyName)
    }

    const addressSchema = PartyAddressSchema

    return {
      RouteNames,
      hasPropData,
      addressSchema,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
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
.submitting-name {
  font-weight: bold;
  font-size: 14px;
  color: $gray9;
  padding-top: 1px;
}

.side-header-icon {
  margin-top: -8px;
  color: $gray9;
}

.content {
  margin-bottom: unset;
  line-height: 22px;
  font-size: 14px;
  color: $gray7;
}

#review-submitting-party-section {
  h3 {
    line-height: unset;
  }
}
</style>
