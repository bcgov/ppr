<template>
  <v-card flat id="home-location-summary" class="mt-6">
    <header class="review-header">
      <v-icon class="ml-2" color="darkBlue">mdi-home</v-icon>
      <label class="font-weight-bold pl-2">Location of Home</label>
    </header>

    <div :class="{ 'border-error-left': !getStepValidation(MhrSectVal.LOCATION_VALID)}">
      <section class="mx-6 pt-8" v-if="!getStepValidation(MhrSectVal.LOCATION_VALID)">
        <span>
          <v-icon color="error">mdi-information-outline</v-icon>
          <span class="error-text mx-1">This step is unfinished.</span>
          <router-link
            :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.HOME_LOCATION}` }"
          >Return to this step to complete it.</router-link>
        </span>
      </section>

      <section class="py-6" id="review-home-location-section">
        <v-row no-gutters class="px-6">
          <v-col cols="3" class="pt-1">
            <h3>Location Type</h3>
          </v-col>
          <v-col cols="9" class="pt-1">
            <p>{{ locationType }}</p>
          </v-col>
        </v-row>

          <!-- Lot Type -->
          <template v-if="getMhrRegistrationLocation.locationType === HomeLocationTypes.LOT">
            <v-row no-gutters class="px-6 pt-1">
              <v-col cols="3" class="pt-1 pr-2">
                <h3>Dealer / Manufacturer Name</h3>
              </v-col>
              <v-col cols="9" class="pt-1">
                <p>{{ getMhrRegistrationLocation.dealerName || '(Not Entered)' }}</p>
              </v-col>
            </v-row>
          </template>

          <!-- Park Type -->
          <template v-if="getMhrRegistrationLocation.locationType === HomeLocationTypes.HOME_PARK">
            <v-row no-gutters class="px-6 pt-1">
              <v-col cols="3" class="pt-1">
                <h3>Park Name</h3>
              </v-col>
              <v-col cols="9" class="pt-1">
                <p>{{ getMhrRegistrationLocation.parkName || '(Not Entered)' }}</p>
              </v-col>
            </v-row>
            <v-row no-gutters class="px-6 pt-1">
              <v-col cols="3" class="pt-1">
                <h3>Pad</h3>
              </v-col>
              <v-col cols="9" class="pt-1">
                <p>{{ getMhrRegistrationLocation.pad || 'N/A' }}</p>
              </v-col>
            </v-row>
          </template>

          <!-- Other PID Type -->
          <template v-if="includesPid">
            <v-row no-gutters class="px-6 pt-1">
              <v-col cols="3" class="pt-1">
                <h3>PID Number</h3>
              </v-col>
              <v-col cols="9" class="pt-1">
                <p>{{ getMhrRegistrationLocation.pidNumber || '(Not Entered)' }}</p>
              </v-col>
            </v-row>
          </template>

          <!-- Civic Address -->
          <v-row no-gutters class="px-6 pt-2">
            <v-col cols="3" class="pt-1">
              <h3>Civic Address</h3>
            </v-col>
            <v-col cols="9" class="pt-1">
              <p v-if="getMhrRegistrationLocation.address.street &&
                       getMhrRegistrationLocation.address.city">
                {{ getMhrRegistrationLocation.address.street }}<br/>
                <span v-if="!!getMhrRegistrationLocation.address.streetAdditional">
                  {{getMhrRegistrationLocation.address.streetAdditional}}<br/>
                </span>
                {{ getMhrRegistrationLocation.address.city }} {{ getMhrRegistrationLocation.address.region }}
              </p>
              <p v-else>
                {{ '(Not Entered)' }}
              </p>
            </v-col>
          </v-row>
      </section>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { HomeLocationTypes, RouteNames } from '@/enums'
import { useGetters } from 'vuex-composition-helpers'
import { useMhrValidations } from '@/composables'

export default defineComponent({
  name: 'HomeLocationReview',
  components: {},
  props: {},
  setup () {
    const {
      getMhrRegistrationLocation,
      getMhrRegistrationValidationModel
    } = useGetters<any>([
      'getMhrRegistrationLocation',
      'getMhrRegistrationValidationModel'
    ])

    const {
      MhrSectVal,
      getStepValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      includesPid: computed((): boolean => {
        return [HomeLocationTypes.OTHER_STRATA, HomeLocationTypes.OTHER_TYPE]
          .includes(getMhrRegistrationLocation.value.otherType)
      }),
      locationType: computed((): string => {
        switch (getMhrRegistrationLocation.value.locationType) {
          case HomeLocationTypes.LOT:
            return 'Dealer\'s / Manufacturer\'s lot'
          case HomeLocationTypes.HOME_PARK:
            return 'Manufactured home park (other than a strata park)'
          case HomeLocationTypes.OTHER_LAND:
            switch (getMhrRegistrationLocation.value.otherType) {
              case HomeLocationTypes.OTHER_RESERVE:
                return 'Indian Reserve'
              case HomeLocationTypes.OTHER_STRATA:
                return 'Strata'
              case HomeLocationTypes.OTHER_TYPE:
                return 'Other'
              default:
                return '(Not Entered)'
            }
          default:
            return '(Not Entered)'
        }
      })
    })

    return {
      HomeLocationTypes,
      RouteNames,
      MhrSectVal,
      getStepValidation,
      getMhrRegistrationLocation,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#home-location-summary {
  h3 {
    line-height: unset;
  }

  p {
    margin-bottom: unset;
    line-height: 24px;
    color: $gray7;
  }
}

.review-header {
  display: flex; // to align icons
  background-color: $BCgovBlue5O;
  padding: 1.25rem;
  color: $gray9;
}

.error-text {
  font-size: 16px;
}
</style>
