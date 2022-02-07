<template>
  <v-container
    v-if="!summaryView"
    fluid
    id="length-trust-amendment"
    no-gutters
    class="white pb-6 pr-10 pl-8 rounded-bottom"
    :class="{ 'border-error-left': showErrorBar && editInProgress }"
  >
    <v-row no-gutters class="summary-header pa-2 mb-8 mt-n3 ml-n8 mr-n10 rounded-top">
      <v-col cols="auto" class="pa-2">
        <v-icon color="darkBlue">mdi-calendar-clock</v-icon>
        <label class="pl-3">
          <strong>Current Expiry<span v-if="showTrustIndenture"> and Trust Indenture</span></strong>
        </label>
      </v-col>
    </v-row>
    <div>
      <v-row no-gutters class="pt-2 pb-3">
        <v-col cols="3" class="generic-label">Current Expiry</v-col>
        <v-col cols="9" id="current-expiry">{{ computedExpiryDateFormatted }}</v-col>
      </v-row>
      <v-row no-gutters class="pt-6" v-if="showTrustIndenture && !showEditTrustIndenture">
        <v-col cols="3" class="generic-label">
          Trust Indenture
          <div v-if="trustIndentureModified">
            <v-chip x-small label color="primary" text-color="white">
                AMENDED
            </v-chip>
          </div>
        </v-col>
        <v-col cols="7" class="summary-text">
            {{ trustIndentureSummary }}
        </v-col>
        <v-col cols="2" class="text-right">
          <span v-if="trustIndentureModified" class="edit-action">
            <v-btn
              text
              color="primary"
              :class="[$style['smaller-button'], 'edit-btn', 'pb-4']"
              id="trust-indenture-undo-btn"
              @click="undoTrustIndenture()"
              :disabled="editInProgress"
            >
              <v-icon small>mdi-undo</v-icon>
              <span>Undo</span>
            </v-btn>
          </span>
          <span v-else class="edit-action">
            <v-btn
              text
              color="primary"
              :class="[$style['smaller-button'], 'edit-btn', 'pb-4']"
              id="trust-indenture-amend-btn"
              @click="initEdit()"
              :disabled="editInProgress"
            >
              <v-icon small>mdi-pencil</v-icon>
              <span>Amend</span>
            </v-btn>
          </span>
        </v-col>
      </v-row>
      <!-- Edit -->
      <v-row no-gutters v-if="showEditTrustIndenture">
          <v-col cols="12" class="edit-debtor-container pa-0">
            <edit-trust-indenture
              :currentTrustIndenture="trustIndenture"
              @editTrustIndenture="resetEdit"
              @resetEvent="resetEdit"
            />
          </v-col>
      </v-row>
    </div>
  </v-container>
  <v-container v-else class="white pa-0" fluid no-gutters>
    <h2 class="pl-3">Trust Indenture</h2>
    <v-row no-gutters class="py-8">
      <v-col cols="3" class="generic-label pl-5">
        Trust Indenture
        <div v-if="trustIndentureModified">
          <v-chip x-small label color="primary" text-color="white">
              AMENDED
          </v-chip>
        </div>
      </v-col>
      <v-col cols="9" class="summary-text">
          {{ trustIndentureSummary }}
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch,
  onMounted
} from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'
import EditTrustIndenture from './EditTrustIndenture.vue'

// local
import { LengthTrustIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { convertDate } from '@/utils'
import { APIRegistrationTypes } from '@/enums'

export default defineComponent({
  components: {
    EditTrustIndenture
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { setLengthTrust } = useActions<any>(['setLengthTrust'])
    const { getLengthTrust } = useGetters<any>(['getLengthTrust'])
    const { getOriginalLengthTrust } = useGetters<any>(['getOriginalLengthTrust'])

    const { getRegistrationType, getRegistrationExpiryDate } = useGetters<any>([
      'getRegistrationType', 'getRegistrationExpiryDate'
    ])
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const modal = false

    const localState = reactive({
      showEditTrustIndenture: false,
      editInProgress: false,
      originalTrustIndenture: getOriginalLengthTrust.value.trustIndenture,
      lifeInfinite: getLengthTrust.value.valid ? getLengthTrust.value.lifeInfinite.toString() : '',
      trustIndentureHint: '',
      showTrustIndenture: computed((): boolean => {
        return registrationType === APIRegistrationTypes.SECURITY_AGREEMENT
      }),
      summaryView: computed((): boolean => {
        return props.isSummary
      }),
      computedExpiryDateFormatted: computed((): string => {
        if (getLengthTrust.value.lifeInfinite) {
          return 'No Expiry'
        }
        if ((getRegistrationExpiryDate.value)) {
          return convertDate(new Date(getRegistrationExpiryDate.value), true, true)
        }
        return ''
      }),
      lengthTrust: computed((): LengthTrustIF => {
        return getLengthTrust.value as LengthTrustIF || null
      }),
      trustIndenture: computed((): boolean => {
        return localState.lengthTrust.trustIndenture
      }),
      trustIndentureSummary: computed((): string => {
        return localState.lengthTrust.trustIndenture ? 'Yes' : 'No'
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      }),
      trustIndentureModified: computed((): boolean => {
        return localState.lengthTrust.trustIndenture !== localState.originalTrustIndenture
      })
    })

    const undoTrustIndenture = (): void => {
      const lt = getLengthTrust.value
      lt.trustIndenture = localState.originalTrustIndenture
      delete lt.action
      setLengthTrust(lt)
    }

    const initEdit = () => {
      localState.editInProgress = true
      localState.showEditTrustIndenture = true
      context.emit('lengthTrustOpen', true)
    }

    const resetEdit = () => {
      localState.editInProgress = false
      localState.showEditTrustIndenture = false
      context.emit('lengthTrustOpen', false)
    }

    onMounted(() => {
      const lt = localState.lengthTrust
      lt.valid = true
      setLengthTrust(lt)
    })

    watch(
      () => localState.trustIndenture,
      (val: boolean) => {
        const lt = localState.lengthTrust
        lt.trustIndenture = val
        setLengthTrust(lt)
      }
    )

    return {
      APIRegistrationTypes,
      resetEdit,
      initEdit,
      registrationType,
      undoTrustIndenture,
      modal,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
/* Need scoped for date picker v-deep style overrides to work */
@import '@/assets/styles/theme.scss';
.v-list-item {
  min-height: 0;
}

::v-deep
  .theme--light.v-btn:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
  background-color: $primary-blue !important;
  border-color: $primary-blue !important;
  color: white !important;
}
::v-deep .v-btn:not(.v-btn--text):not(.v-btn--outlined).v-btn--active:before {
  opacity: 0;
}
::v-deep .v-icon.v-icon.v-icon--link {
  cursor: text;
}
::v-deep .theme--light.v-icon.v-icon.v-icon--disabled {
  color: $primary-blue !important;
}
::v-deep .v-input--is-disabled {
  opacity: 0.4;
}

.smaller-actions {
  min-width: 34px !important;
  padding: 0 8px !important;
}

.smaller-button {
  padding: 0 12px !important;
}

</style>
