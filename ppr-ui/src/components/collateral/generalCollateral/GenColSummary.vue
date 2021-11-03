<template>
  <v-container class="pa-0">
    <v-row no-gutters v-if="showConfirm">
      <v-col cols="10">
        <h3 style="line-height: 1rem;">General Collateral</h3>
      </v-col>
    </v-row>
    <v-row no-gutters v-if="showAmendLink">
      <v-col cols="10">
        <h3 style="line-height: 1rem;">General Collateral</h3>
      </v-col>
      <v-col>
        <div class="float-right">
        <span
          v-if="registrationFlowType === RegistrationFlowType.AMENDMENT &&
              generalCollateral.length > 0 &&
              generalCollateral[generalCollateral.length - 1].addedDateTime === undefined"
          class="edit-button"
        >
          <v-btn
            text
            color="primary"
            class="smaller-button edit-btn"
            id="gen-col-undo-btn"
            @click="undo()"
          >
            <v-icon small>mdi-undo</v-icon>
            <span>Undo</span>
          </v-btn>
        </span>
        <span
          v-else-if="registrationFlowType === RegistrationFlowType.AMENDMENT &&
              (generalCollateral.length === 0 ||
                generalCollateral[generalCollateral.length - 1].addedDateTime !== undefined)"
          class="edit-button"
        >
          <v-btn
            text
            color="primary"
            class="smaller-button edit-btn"
            id="gen-col-amend-btn"
            @click="initGenColAmend()"
          >
            <v-icon small>mdi-pencil</v-icon>
            <span>Amend</span>
          </v-btn>
        </span>
        <span
          class="actions-border actions__more"
          v-if="registrationFlowType === RegistrationFlowType.AMENDMENT &&
              generalCollateral.length > 0 &&
              generalCollateral[generalCollateral.length - 1].addedDateTime === undefined"
        >
          <v-menu offset-y left nudge-bottom="4">
            <template v-slot:activator="{ on }">
              <v-btn
                text
                small
                v-on="on"
                color="primary"
                class="smaller-actions actions__more-actions__btn"
              >
                <v-icon>mdi-menu-down</v-icon>
              </v-btn>
            </template>
            <v-list class="actions__more-actions">
              <v-list-item @click="initGenColAmend()">
                <v-list-item-subtitle>
                  <v-icon small>mdi-pencil</v-icon>
                  <span class="ml-1">Amend</span>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-menu>
        </span>
        </div>
      </v-col>
    </v-row>
    <div v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
              && lastGeneralCollateral
              && (showAmendLink || showConfirm)
              && !lastGeneralCollateral.addedDateTime"
              class="pa-0"
              :class="{'ps-6': !showViewLink}">
      <div v-if="lastGeneralCollateral.descriptionDelete" class="gc-description-delete pt-2">
        <v-chip class="badge-delete" color="primary" label text-color="white" x-small>
          <b>DELETED</b>
        </v-chip>
        <p class="pt-3 ma-0">
          {{ lastGeneralCollateral.descriptionDelete }}
        </p>
      </div>
      <div v-if="lastGeneralCollateral.descriptionAdd" class="gc-description-add pt-5">
        <v-chip color="primary" label text-color="white" x-small>
          <b>ADDED</b>
        </v-chip>
        <p class="pt-3 ma-0">
          {{ lastGeneralCollateral.descriptionAdd }}
        </p>
      </div>
    </div>
    <div
      v-if="registrationFlowType !== RegistrationFlowType.NEW"
      id="general-collateral-history"
      class="mt-7"
    >
      <v-btn
        v-if="showViewLink"
        id="gc-show-history-btn"
        class="ma-0 pa-0"
        color="primary"
        text
        @click="showingHistory = !showingHistory"
      >
        <p class="ma-0">
          <span v-if="showingHistory">Hide </span>
          <span v-else>View </span>
          General Collateral Changes and Amendments ({{ generalCollateralLength }})
        </p>
      </v-btn>
      <div v-if="showingHistory" class="general-collateral-summary">
        <v-row v-for="(item, index) in generalCollateral" :key="index" no-gutters>
          <v-col v-if="item.addedDateTime" :class="[{ 'border-btm': index !== baseGenCollateralIndex,
            'pb-30px': index !== baseGenCollateralIndex }, 'pt-30px']">
            <b>{{ asOfDateTime(item.addedDateTime) }}</b>
            <div v-if="item.descriptionDelete" class="gc-description-delete pt-5">
              <v-chip class="badge-delete" color="primary" label text-color="white" x-small>
                <b>DELETED</b>
              </v-chip>
              <p class="pt-3 ma-0">
                {{ item.descriptionDelete }}
              </p>
            </div>
            <div v-if="item.descriptionAdd" class="gc-description-add pt-5">
              <v-chip color="primary" label text-color="white" x-small>
                <b>ADDED</b>
              </v-chip>
              <p class="pt-3 ma-0">
                {{ item.descriptionAdd }}
              </p>
            </div>
            <div v-if="item.description && index === baseGenCollateralIndex" class="gc-description pt-5">
              <b v-if="registrationFlowType !== RegistrationFlowType.NEW">
                Base Registration General Collateral:
              </b>
              <p v-if="item.description" class="pt-5 ma-0">
                {{ item.description }}
              </p>
            </div>
          </v-col>
        </v-row>
      </div>
    </div>
    <div v-else class="general-collateral-summary pt-5">
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
import { useActions, useGetters } from 'vuex-composition-helpers'
// local
import { RegistrationFlowType } from '@/enums' // eslint-disable-line no-unused-vars
import { GeneralCollateralIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate } from '@/utils'
import { cloneDeep } from 'lodash'

export default defineComponent({
  name: 'GenColSummary',
  props: {
    setShowHistory: {
      type: Boolean,
      default: false
    },
    setShowAmendLink: {
      type: Boolean,
      default: true
    },
    setShowViewLink: {
      type: Boolean,
      default: true
    },
    setShowConfirm: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const {
      getGeneralCollateral,
      getOriginalAddCollateral,
      getRegistrationFlowType
    } = useGetters<any>([
      'getGeneralCollateral',
      'getOriginalAddCollateral',
      'getRegistrationFlowType'
    ])
    const { setGeneralCollateral } = useActions<any>(['setGeneralCollateral'])

    const localState = reactive({
      showingHistory: props.setShowHistory,
      baseGenCollateralIndex: computed(() => {
        let curIndex = 0
        // find the entry with the lowest added date time
        for (var i = 0; i < localState.generalCollateral.length; i++) {
          if (localState.generalCollateral[i].description) {
            curIndex = i
          }
        }
        return curIndex
      }),
      generalCollateral: computed((): GeneralCollateralIF[] => {
        return (getGeneralCollateral.value as GeneralCollateralIF[]) || []
      }),
      lastGeneralCollateral: computed((): GeneralCollateralIF => {
        if (localState.generalCollateral.length) {
          return localState.generalCollateral[localState.generalCollateral.length - 1]
        }
        return null
      }),
      generalCollateralLength: computed((): number => {
        if (getGeneralCollateral.value && getGeneralCollateral.value.length > 0) {
          if (localState.lastGeneralCollateral.addedDateTime) {
            return getGeneralCollateral.value.length
          } else {
            return getGeneralCollateral.value.length - 1
          }
        }
        return 0
      }),
      registrationFlowType: computed((): RegistrationFlowType => {
        return getRegistrationFlowType.value
      }),
      showAmendLink: computed((): boolean => {
        return props.setShowAmendLink
      }),
      showViewLink: computed((): boolean => {
        return props.setShowViewLink
      }),
      showConfirm: computed((): boolean => {
        return props.setShowConfirm
      })
    })

    const initGenColAmend = () => {
      emit('initGenColAmend', true)
    }

    const undo = () => {
      const originalGeneralCollateral =
        cloneDeep(getOriginalAddCollateral.value.generalCollateral)
      setGeneralCollateral(originalGeneralCollateral)
    }

    const asOfDateTime = (dateString: string) => {
      const asOfDate = new Date(dateString)
      return convertDate(asOfDate, true, true)
    }

    return {
      asOfDateTime,
      RegistrationFlowType,
      initGenColAmend,
      undo,
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
#gc-show-history-btn {
  font-size: 0.875rem;
  height: 1rem;
  min-width: 0;
  text-decoration: underline;
}
::v-deep .v-btn:not(.v-btn--round).v-size--default::before {
  background-color: transparent;
}
</style>
