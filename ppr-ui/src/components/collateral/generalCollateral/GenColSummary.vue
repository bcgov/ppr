<template>
  <v-container class="pa-0">
    <h3 style="line-height: 1rem;">General Collateral</h3>
    <div v-if="registrationFlowType !== RegistrationFlowType.NEW" id="general-collateral-history" class="mt-10">
      <v-btn id="gc-show-history-btn" class="ma-0 pa-0" color="primary" text @click="showingHistory = !showingHistory">
        <p class="ma-0">
          <span v-if="showingHistory">Hide </span>
          <span v-else>View </span>
          General Collateral and Ammendments ({{ generalCollateral.length }})
        </p>
      </v-btn>
      <div v-if="showingHistory" class="general-collateral-summary">
        <v-row v-for="(item, index) in generalCollateral" :key="index" no-gutters>
          <v-col :class="[{ 'border-btm': index !== baseGenCollateralIndex }, 'pt-10']">
            <b v-if="item.addedDateTime">{{ asOfDateTime(item.addedDateTime) }}</b>
            <div v-if="item.descriptionDelete" class="gc-description-delete pt-30px">
              <v-chip class="badge-delete" color="primary" label text-color="white" x-small>
                <b>DELETED</b>
              </v-chip>
              <p class="pt-5 ma-0">
                {{ item.descriptionDelete }}
              </p>
            </div>
            <div v-if="item.descriptionAdd" class="gc-description-add pt-30px">
              <v-chip color="primary" label text-color="white" x-small>
                <b>ADDED</b>
              </v-chip>
              <p class="pt-5 ma-0">
                {{ item.descriptionAdd }}
              </p>
            </div>
            <div v-if="item.description && index === baseGenCollateralIndex" class="gc-description">
              <b v-if="registrationFlowType !== RegistrationFlowType.NEW" class="pt-30px">
                Base Registration Collateral:
              </b>
              <p v-if="item.description" class="pt-30px ma-0">
                {{ item.description }}
              </p>
            </div>
          </v-col>
        </v-row>
      </div>
    </div>
    <div v-else class="general-collateral-summary pt-10">
      <p v-if="generalCollateral.length > 0" class="ma-0">
        {{ generalCollateral[0].description }}
      </p>
    </div>
  </v-container>
</template>
<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  computed
} from '@vue/composition-api'
import { useGetters } from 'vuex-composition-helpers'
// local
import { RegistrationFlowType } from '@/enums' // eslint-disable-line no-unused-vars
import { GeneralCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate } from '@/utils'

export default defineComponent({
  name: 'GenColSummary',
  setup () {
    const {
      getGeneralCollateral,
      getRegistrationFlowType
    } = useGetters<any>(['getGeneralCollateral', 'getRegistrationFlowType'])

    const localState = reactive({
      showingHistory: false,
      baseGenCollateralIndex: computed(() => {
        return (localState.generalCollateral?.length || 0) - 1
      }),
      generalCollateral: computed((): GeneralCollateralIF[] => {
        return getGeneralCollateral.value as GeneralCollateralIF[] || []
      }),
      registrationFlowType: computed((): RegistrationFlowType => {
        return getRegistrationFlowType.value
      })
    })

    const asOfDateTime = (dateString: string) => {
      const asOfDate = new Date(dateString)
      return convertDate(asOfDate, true, true)
    }

    return {
      asOfDateTime,
      RegistrationFlowType,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.border-btm {
  border-bottom: 1px solid $gray3;
}
.general-collateral-summary {
  font-size: 0.875rem;
  line-height: 1.375rem;
  color: $gray7;
}
::v-deep .v-btn:not(.v-btn--round).v-size--default {
  font-size: 0.875rem;
  height: 1rem;
  min-width: 0;
  text-decoration: underline;
}
::v-deep .v-btn:not(.v-btn--round).v-size--default::before {
  background-color: transparent;
}
</style>
