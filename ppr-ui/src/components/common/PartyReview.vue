<template>
  <v-card flat id="party-review" class="mt-10">

    <!-- Header Slot -->
    <slot name="headerSlot">
      <header class="review-header">
        <v-icon class="ml-1" color="darkBlue">mdi-account</v-icon>
        <label class="font-weight-bold pl-2">Submitting Party</label>
      </header>
    </slot>

    <div :class="{ 'border-error-left': showIncomplete }">
      <!-- Incomplete Section Msg -->
      <section v-if="showIncomplete" class="mx-7 pt-9" :class="{ 'pb-9' : !hasData }">
        <v-icon color="error">mdi-information-outline</v-icon>
        <span class="error-text mx-1">This step is unfinished.</span>
        <router-link :to="{ path: returnRoute }">Return to this step to complete it.</router-link>
      </section>

      <!-- Party Info -->
      <template v-if="hasData || showNotEntered">

        <section class="party-info">
          <!-- Upper party info slot -->
          <slot name="topInfoSlot" />

          <!--- Party Info Headers -->
          <v-divider class="mx-8 mt-6"/>

          <!-- Party info label slot -->
          <slot name="partyInfoLabelSlot" />

          <v-row no-gutters class="px-8 pt-6 pb-2">
            <!-- Future: Handle person name -->
            <v-col v-if="hasPropData('businessName')">
              <h4>Name</h4>
            </v-col>
            <v-col v-if="hasPropData('address')">
              <h4>Mailing Address</h4>
            </v-col>
            <v-col v-if="hasPropData('emailAddress')">
              <h4>Email Address</h4>
            </v-col>
            <v-col v-if="hasPropData('phoneNumber')">
              <h4>Phone Number</h4 >
            </v-col>
          </v-row>
          <v-divider class="mx-8"/>

          <!-- Party Info Data -->
          <v-row no-gutters class="px-8 py-7">
            <v-col v-if="hasPropData('businessName')" class="pr-4">
              <!-- Future: Handle person name -->
              <label class="generic-label fs-14 icon-text">
                <v-icon class="mt-n1 mr-1">mdi-domain</v-icon>
                {{ partyModel.businessName || '(Not Entered)' }}
              </label>
            </v-col>

            <v-col v-if="hasPropData('address')">
              <base-address
                v-if="hasTruthyValue(partyModel.address)"
                :value="partyModel.address"
              />

              <p v-else> (Not Entered) </p>
            </v-col>

            <v-col v-if="hasPropData('emailAddress')">
              <p>{{ partyModel.emailAddress || '(Not Entered)'}}</p>
            </v-col>

            <v-col v-if="hasPropData('phoneNumber')">
              <p>
                {{ partyModel.phoneNumber || '(Not Entered)'}}
                {{ partyModel.phoneExtension ? `Ext ${partyModel.phoneExtension}` : '' }}
              </p>
            </v-col>
          </v-row>

          <!-- Bottom party info slot -->
          <slot name="bottomInfoSlot" />
        </section>
      </template>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { RouteNames } from '@/enums'
import { BaseAddress } from '@/composables/address'
import { PartyIF } from '@/interfaces'
import { hasTruthyValue } from '@/utils'

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
    showIncomplete: {
      type: Boolean,
      default: true
    },
    showNotEntered: {
      type: Boolean,
      default: false
    },
    returnToRoutes: {
      type: Array as () => Array<RouteNames>,
      default: () => []
    }
  },
  setup (props) {
    const localState = reactive({
      partyModel: props.baseParty as PartyIF,
      hasData: computed(() : boolean => {
        return hasTruthyValue(props.baseParty)
      }),
      returnRoute: computed(() : string => {
        let returnRoute = ''
        for (const route of props.returnToRoutes) {
          returnRoute += `/${route}`
        }
        return returnRoute
      })
    })

    const hasPropData = (propertyName: string): boolean => {
      return localState.partyModel?.hasOwnProperty(propertyName)
    }

    return {
      RouteNames,
      hasPropData,
      hasTruthyValue,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
