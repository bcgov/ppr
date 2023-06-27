<template>
  <v-card flat id="submitting-party-summary" class="mt-6">
    <header class="review-header">
      <v-icon class="ml-1" color="darkBlue">mdi-account</v-icon>
      <label class="font-weight-bold pl-2">Submitting Party</label>
    </header>

    <div :class="{ 'border-error-left': showStepError }">
      <section class="mx-6 pt-8" v-if="showStepError">
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

          <v-divider class="mx-4"/>

          <v-row no-gutters class="px-6 py-7">
            <v-col cols="3">
              <v-row no-gutters>
                <v-col cols="1" class="mr-2">
                  <v-icon class="side-header-icon">
                    {{getMhrRegistrationSubmittingParty.businessName ? 'mdi-domain' : 'mdi-account'}}
                  </v-icon>
                </v-col>
                <v-col>
                  <p class="submitting-name">
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
              <p class="content">{{getMhrRegistrationSubmittingParty.emailAddress || emptyText }}</p>
            </v-col>
            <v-col cols="3" class="pl-4">
              <p class="content" v-html="parsePhoneNumber()"></p>
            </v-col>
          </v-row>

          <template v-if="!isMhrManufacturerRegistration">
            <v-divider class="mx-4"/>

            <v-row no-gutters class="px-6 py-7">
              <v-col cols="3">
                <h3>Document ID</h3>
              </v-col>
              <v-col cols="9">
                <p class="content ref-text">{{getMhrRegistrationDocumentId || emptyText }}</p>
              </v-col>
            </v-row>

            <v-divider class="mx-4"/>

            <v-row no-gutters class="px-6 py-7">
              <v-col cols="3">
                <p class="side-header">{{ attnOrRefConfig.title }}</p>
              </v-col>
              <v-col cols="9">
                <p class="content ref-text">{{getMhrAttentionReference || emptyText }}</p>
              </v-col>
            </v-row>

          </template>
        </section>
      </template>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { RouteNames } from '@/enums'
import { useStore } from '@/store/store'
import { BaseAddress } from '@/composables/address'
import { PartyAddressSchema } from '@/schemas'
import { toDisplayPhone } from '@/utils'
import { useMhrValidations } from '@/composables'
import { AttnRefConfigIF } from '@/interfaces'
import { attentionConfig, folioOrRefConfig } from '@/resources/attnRefConfigs'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'SubmittingPartyReview',
  components: {
    BaseAddress
  },
  props: {},
  setup () {
    const {
      isRoleStaffReg,
      getMhrRegistrationSubmittingParty,
      getMhrRegistrationDocumentId,
      getMhrAttentionReference,
      getMhrRegistrationValidationModel,
      isMhrManufacturerRegistration
    } = storeToRefs(useStore())

    const {
      MhrSectVal,
      getStepValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      address: computed(() => getMhrRegistrationSubmittingParty.value.address),
      businessName: computed(() => getMhrRegistrationSubmittingParty.value.businessName),
      personName: computed(() => getMhrRegistrationSubmittingParty.value.personName),
      hasAddress: computed(() => !Object.values(localState.address).every(val => !val)),
      attnOrRefConfig: computed((): AttnRefConfigIF => isRoleStaffReg.value ? attentionConfig : folioOrRefConfig),
      emptyText: computed(() => isMhrManufacturerRegistration.value ? '' : '(Not Entered)'),
      showStepError: computed(() => {
        return !isMhrManufacturerRegistration.value && !getStepValidation(MhrSectVal.SUBMITTING_PARTY_VALID)
      })
    })

    const addressSchema = PartyAddressSchema

    const parsePhoneNumber = () => {
      const phone = getMhrRegistrationSubmittingParty.value
      const phoneNum = phone.phoneNumber
      const ext = phone.phoneExtension ? ' &nbsp;Ext ' + phone.phoneExtension : ''
      return phoneNum ? `${toDisplayPhone(phoneNum)}${ext}` : localState.emptyText
    }

    const getSubmittingPartyName = () => {
      if (!localState.businessName && Object.values(localState.personName).every(val => !val)) {
        return localState.emptyText
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
      MhrSectVal,
      isRoleStaffReg,
      isMhrManufacturerRegistration,
      getMhrRegistrationSubmittingParty,
      getMhrRegistrationDocumentId,
      getMhrAttentionReference,
      getStepValidation,
      getSubmittingPartyName,
      parsePhoneNumber,
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
  line-height: 24px;
  font-size: 14px;
  color: $gray7;
}

#review-submitting-party-section {
  h3 {
    line-height: unset;
  }
}
</style>
