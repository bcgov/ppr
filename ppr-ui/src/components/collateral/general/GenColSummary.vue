<template>
  <v-container class="px-2">
    <v-row
      v-if="showConfirm"
      no-gutters
      class="pb-4"
    >
      <v-col cols="10">
        <h3 style="line-height: 1rem;">
          General Collateral
        </h3>
      </v-col>
    </v-row>
    <v-row
      v-if="showAmendLink"
      no-gutters
      class="px-0"
    >
      <v-col cols="10">
        <h3 style="line-height: 1rem;">
          General Collateral
        </h3>
      </v-col>
      <v-col class="pl-3">
        <div class="float-right">
          <span
            v-if="registrationFlowType === RegistrationFlowType.AMENDMENT &&
              generalCollateral.length > 0 &&
              generalCollateral[generalCollateral.length - 1].addedDateTime === undefined"
          >
            <v-btn
              id="gen-col-undo-btn"
              variant="plain"
              color="primary"
              class="smaller-button edit-btn"
              @click="undo()"
            >
              <v-icon size="small">mdi-undo</v-icon>
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
              id="gen-col-amend-btn"
              variant="plain"
              color="primary"
              class="smaller-button edit-btn"
              @click="initGenColAmend()"
            >
              <v-icon size="small">mdi-pencil</v-icon>
              <span>Amend</span>
            </v-btn>
          </span>
          <span
            v-if="registrationFlowType === RegistrationFlowType.AMENDMENT &&
              generalCollateral.length > 0 &&
              generalCollateral[generalCollateral.length - 1].addedDateTime === undefined"
            class="actions-border actions__more"
          >
            <v-menu
              location="bottom right"
            >
              <template #activator="{ props }">
                <v-btn
                  variant="plain"
                  size="small"
                  color="primary"
                  class="smaller-actions actions__more-actions__btn"
                  v-bind="props"
                >
                  <v-icon>mdi-menu-down</v-icon>
                </v-btn>
              </template>
              <v-list class="actions__more-actions">
                <v-list-item @click="initGenColAmend()">
                  <v-list-item-subtitle>
                    <v-icon size="small">mdi-pencil</v-icon>
                    <span class="ml-1">Amend</span>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-menu>
          </span>
        </div>
      </v-col>
    </v-row>
    <div
      v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
        && lastGeneralCollateral
        && (showAmendLink || showConfirm)
        && !lastGeneralCollateral.addedDateTime"
      class="pa-0 general-collateral-summary"
      :class="{'ps-6': !showViewLink}"
    >
      <div
        v-if="lastGeneralCollateral.descriptionDelete"
        class="gc-description-delete pt-2"
      >
        <v-chip
          class="badge-delete"
          variant="elevated"
          color="greyLighten"
          x-small
        >
          <b>DELETED</b>
        </v-chip>
        <p class="ProseMirror pt-3 ma-0">
          <span
            style="white-space: pre-wrap;"
            v-html="lastGeneralCollateral.descriptionDelete"
          />
        </p>
      </div>
      <div
        v-if="lastGeneralCollateral.descriptionAdd"
        class="gc-description-add pt-5"
      >
        <v-chip
          color="primary"
          variant="elevated"
          x-small
        >
          <b>ADDED</b>
        </v-chip>
        <p class="ProseMirror pt-3 ma-0">
          <span
            style="white-space: pre-wrap;"
            v-html="lastGeneralCollateral.descriptionAdd"
          />
        </p>
      </div>
    </div>
    <div
      v-if="registrationFlowType !== RegistrationFlowType.NEW"
      id="general-collateral-history"
    >
      <v-btn
        v-if="showViewLink"
        id="gc-show-history-btn"
        class="ma-0 pa-0"
        color="primary"
        variant="plain"
        @click="showingHistory = !showingHistory"
      >
        <p class="ma-0">
          <span v-if="showingHistory">Hide </span>
          <span v-else>View </span>
          General Collateral Changes and Amendments ({{ generalCollateralLength }})
        </p>
      </v-btn>
      <div
        v-if="showingHistory"
        class="general-collateral-summary"
      >
        <v-row
          v-for="(item, index) in generalCollateral"
          :key="index"
          no-gutters
        >
          <v-col
            v-if="item.addedDateTime"
            :class="[{ 'border-btm': index !== baseGenCollateralIndex, 'pb-30px':
              index !== baseGenCollateralIndex }, 'pt-30px']"
          >
            <div v-if="!item.description || registrationFlowType === RegistrationFlowType.NEW">
              <b>{{ asOfDateTime(item.addedDateTime) }}</b>
            </div>
            <div
              v-if="item.descriptionDelete"
              class="gc-description-delete pt-5"
            >
              <v-chip
                class="badge-delete"
                color="greyLighten"
                variant="elevated"
                x-small
              >
                <b>DELETED</b>
              </v-chip>
              <p class="pt-3 ma-0 pr-6">
                <span
                  style="white-space: pre-wrap;"
                  v-html="item.descriptionDelete"
                />
              </p>
            </div>
            <div
              v-if="item.descriptionAdd"
              class="gc-description-add pt-5"
            >
              <v-chip
                color="primary"
                variant="elevated"
                x-small
              >
                <b>ADDED</b>
              </v-chip>
              <p class="pt-3 ma-0 pr-6">
                <span
                  style="white-space: pre-wrap;"
                  v-html="item.descriptionAdd"
                />
              </p>
            </div>
            <div
              v-if="item.description"
              class="gc-description"
            >
              <div
                v-if="registrationFlowType !== RegistrationFlowType.NEW && index === firstBaseGenCollateralIndex"
                class="pb-5"
              >
                <b>{{ asOfDateTime(item.addedDateTime) }}</b>
              </div>
              <div
                v-if="registrationFlowType !== RegistrationFlowType.NEW && index === firstBaseGenCollateralIndex"
                class="pb-5"
              >
                <b>Base Registration General Collateral:</b>
              </div>
              <p
                v-if="item.description"
                class="ProseMirror ma-0"
              >
                <span
                  style="white-space: pre-wrap;"
                  v-html="item.description"
                />
              </p>
            </div>
          </v-col>
        </v-row>
      </div>
    </div>
    <div
      v-else
      class="ProseMirror general-collateral-summary pt-5 px-6"
    >
      <p
        v-if="generalCollateral.length > 0"
        class="ma-0 fs-14"
      >
        <span v-html="generalCollateral[0].description" />
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
} from 'vue'
import { useStore } from '@/store/store'
import { RegistrationFlowType } from '@/enums'
import type { GeneralCollateralIF } from '@/interfaces'
import { pacificDate } from '@/utils'
import { cloneDeep } from 'lodash'
import { storeToRefs } from 'pinia'

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
  emits: [
    'initGenColAmend'
  ],
  setup (props, { emit }) {
    const { setGeneralCollateral } = useStore()
    const { getGeneralCollateral, getOriginalAddCollateral, getRegistrationFlowType } = storeToRefs(useStore())
    const localState = reactive({
      showingHistory: props.setShowHistory,
      baseGenCollateralIndex: computed(() => {
        let curIndex = 0
        // find the entry with the lowest added date time
        for (let i = 0; i < localState.generalCollateral.length; i++) {
          if (localState.generalCollateral[i].description) {
            curIndex = i
          }
        }
        return curIndex
      }),
      firstBaseGenCollateralIndex: computed(() => {
        // find the index of the first base registration general collateral record to display label once.
        for (let i = 0; i < localState.generalCollateral.length; i++) {
          if (localState.generalCollateral[i].description && localState.generalCollateral[i].collateralId) {
            return i
          }
        }
        return -1
      }),
      generalCollateral: computed((): GeneralCollateralIF[] => {
        const generalCollateral = getGeneralCollateral.value as GeneralCollateralIF[] || []
        const cleanedGeneralCollateral = [] as GeneralCollateralIF[]
        for (let i = 0; i < generalCollateral.length; i++) {
          if (!generalCollateral[i].addedDateTime) {
            cleanedGeneralCollateral.push(generalCollateral[i])
            continue
          }
          let alreadyAdded = false
          if (generalCollateral[i].description) {
            const existsIndex = cleanedGeneralCollateral.findIndex(collateral =>
              collateral.description &&
              collateral.addedDateTime === generalCollateral[i].addedDateTime
            )
            if (existsIndex !== -1) {
              cleanedGeneralCollateral[existsIndex].description += generalCollateral[i].description
            } else {
              cleanedGeneralCollateral.push(generalCollateral[i])
              alreadyAdded = true
            }
          }
          if (generalCollateral[i].descriptionAdd) {
            const existsIndex = cleanedGeneralCollateral.findIndex(collateral =>
              collateral.descriptionAdd &&
              collateral.addedDateTime === generalCollateral[i].addedDateTime
            )
            if (existsIndex !== -1) {
              cleanedGeneralCollateral[existsIndex].descriptionAdd += generalCollateral[i].descriptionAdd
            } else {
              if (!alreadyAdded) {
                cleanedGeneralCollateral.push(generalCollateral[i])
                alreadyAdded = true
              }
            }
          }
          if (generalCollateral[i].descriptionDelete) {
            const existsIndex = cleanedGeneralCollateral.findIndex(collateral =>
              collateral.descriptionDelete &&
              collateral.addedDateTime === generalCollateral[i].addedDateTime
            )
            if (existsIndex !== -1) {
              if (!alreadyAdded) {
                cleanedGeneralCollateral[existsIndex].descriptionDelete += generalCollateral[i].descriptionDelete
              }
            } else {
              if (!alreadyAdded) {
                cleanedGeneralCollateral.push(generalCollateral[i])
              }
            }
          }
        }
        return cleanedGeneralCollateral
      }),
      lastGeneralCollateral: computed((): GeneralCollateralIF => {
        if (localState.generalCollateral.length) {
          return localState.generalCollateral[localState.generalCollateral.length - 1]
        }
        return null
      }),
      generalCollateralLength: computed((): number => {
        if (!localState.lastGeneralCollateral) { return 0 }
        if (localState.lastGeneralCollateral?.addedDateTime) {
          return localState.generalCollateral.length
        }
        return localState.generalCollateral.length - 1
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
      return pacificDate(asOfDate)
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

:deep(.general-collateral-summary table td) {
  white-space: normal;
}

#gc-show-history-btn {
  font-size: 0.875rem;
  height: 1rem;
  min-width: 0;
  text-decoration: underline;
}
.edit-button {
  padding-right: 15px;
}
:deep(.v-btn:not(.v-btn--round).v-size--default::before) {
  background-color: transparent;
}
table {
  border-collapse: collapse;
}
td {
  vertical-align: baseline;
  border: 1px solid $gray3;
  padding: 3px 5px;
}

</style>
