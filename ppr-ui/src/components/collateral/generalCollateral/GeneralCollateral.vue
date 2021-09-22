<template>
  <v-container v-if="summaryView" style="padding: 16px 12px 0 30px;">
    <h3 style="line-height: 1rem;">General Collateral</h3>
    <v-btn text color="primary" class="ma-0 pa-0 mt-10" @click="showingHistory = !showingHistory">
      <p class="ma-0">
        <span v-if="showingHistory">Hide </span>
        <span v-else>View </span>
        General Collateral and Ammendments ({{ generalCollateral.length }})
      </p>
    </v-btn>
    <div v-if="showingHistory" class="general-collateral-summary">
      <v-row v-for="(item, index) in generalCollateral" :key="index" no-gutters>
        <v-col :class="[{ 'border-btm': index !== baseGenCollateralIndex }, 'py-10']">
          <b v-if="item.addDateTime">{{ asOfDateTime(item.addDateTime) }}</b>
          <div v-if="item.descriptionDelete" class="pt-30px">
            <v-chip x-small label color="primary" text-color="white">
              <b>DELETED</b>
            </v-chip>
            <p class="pt-5 ma-0">
              {{ item.descriptionDelete }}
            </p>
          </div>
          <div v-if="item.descriptionAdd" class="pt-30px">
            <v-chip x-small label color="primary" text-color="white">
              <b>ADDED</b>
            </v-chip>
            <p class="pt-5 ma-0">
              {{ item.descriptionAdd }}
            </p>
          </div>
          <div v-if="item.description && index === baseGenCollateralIndex" class="pt-30px">
            <b>
              Base Registration Collateral:
            </b>
            <p v-if="item.description" class="pt-30px ma-0">
              {{ item.description }}
            </p>
          </div>
        </v-col>
      </v-row>
    </div>
  </v-container>
  <v-container v-else class="pa-0">
    <v-card
      id="general-collateral"
      :class="{ 'invalid-message': showErrorComponent }"
      flat
    >
      <v-row no-gutters class="py-6">
        <v-col cols="3" class="generic-label pa-4">
          General Collateral
        </v-col>
        <v-col cols="9" class="pr-4">
          <v-textarea
            v-model="newDesc"
            id="generalCollateral"
            auto-grow
            counter="4000"
            filled
            label="Description of General Collateral"
            class="white pt-2 text-input-field"
            :error-messages="valid ? '' : 'Maximum 4000 characters'"
          />
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  onMounted,
  computed
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
// bcregistry shared components
import { ActionChip } from '@bcrs-shared-components/action-chip'
// local
import { APIRegistrationTypes } from '@/enums'
import { GeneralCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate } from '@/utils'
import { useGeneralCollateral } from './factories'

export default defineComponent({
  name: 'GeneralCollateral',
  components: {
    ActionChip
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    },
    setRegistrationType: String as () => APIRegistrationTypes,
    showInvalid: {
      type: Boolean,
      default: false
    }
  },
  emits: ['valid'],
  setup (props, { emit }) {
    const { getGeneralCollateral } = useGetters<any>(['getGeneralCollateral'])
    const { setGeneralCollateral } = useActions<any>(['setGeneralCollateral'])

    const { hasGeneralCollateral, hasGeneralCollateralText } = useGeneralCollateral()

    const localState = reactive({
      newDesc: '',
      registrationType: props.setRegistrationType,
      showingHistory: false,
      summaryView: props.isSummary,
      baseGenCollateralIndex: computed(() => {
        return (localState.generalCollateral?.length || 0) - 1
      }),
      generalCollateral: computed((): GeneralCollateralIF[] => {
        return getGeneralCollateral.value as GeneralCollateralIF[] || []
      }),
      showErrorComponent: computed((): boolean => {
        return props.showInvalid
      }),
      valid: computed((): boolean => {
        return (localState.newDesc?.length || 0) <= 4000
      })
    })

    onMounted(() => {
      // setGeneralCollateral([
      //   {
      //     addDateTime: '2021-09-20T18:56:20Z',
      //     descriptionDelete: 'test delete 2'
      //   },
      //   {
      //     addDateTime: '2021-09-19T18:56:20Z',
      //     descriptionAdd: 'test add 2',
      //     descriptionDelete: 'test delete 1'
      //   },
      //   {
      //     addDateTime: '2021-09-18T18:56:20Z',
      //     descriptionAdd: 'test add 1'
      //   },
      //   {
      //     addDateTime: '2021-09-17T18:56:20Z',
      //     description: 'test description'
      //   }
      // ])
      // if (localState.generalCollateral?.length > 0) {
      //   localState.newDesc = localState.generalCollateral[0].description
      // }
      // if (hasGeneralCollateral(localState.registrationType) && !localState.newDesc) {
      //   if (localState.registrationType === APIRegistrationTypes.LIEN_UNPAID_WAGES) {
      //     localState.newDesc =
      //       'All the personal property of the debtor'
      //   }
      //   if (hasGeneralCollateralText(localState.registrationType)) {
      //     localState.newDesc =
      //       'All the debtor’s present and after acquired personal property, including ' +
      //       'but not restricted to machinery, equipment, furniture, fixtures and receivables.'
      //   }
      // }
    })

    const asOfDateTime = (dateString: string) => {
      const asOfDate = new Date(dateString)
      return convertDate(asOfDate, true, true)
    }

    watch(() => localState.newDesc, (val: string) => {
      emit('valid', localState.valid)
      // if (val) {
      //   setGeneralCollateral([{ description: val }])
      // } else {
      //   setGeneralCollateral([])
      // }
    })

    return {
      asOfDateTime,
      hasGeneralCollateral,
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
