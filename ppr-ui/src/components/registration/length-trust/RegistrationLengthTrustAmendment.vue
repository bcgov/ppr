<template>
  <div id="length-trust-amendment">
    <header
      class="summary-header"
    >
      <v-icon color="darkBlue">
        mdi-calendar-clock
      </v-icon>
      <label class="pl-3">
        <strong>Current Expiry<span v-if="showTrustIndenture"> and Trust Indenture</span></strong>
      </label>
    </header>
    <v-card
      v-if="!summaryView"
      flat
      class="bg-white pb-6 px-6 rounded-bottom"
      :class="{ 'border-error-left': showErrorBar && editInProgress }"
    >
      <v-row
        noGutters
        class="pt-6"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Current Expiry
        </v-col>
        <v-col
          id="current-expiry"
          cols="9"
        >
          {{ computedExpiryDateFormatted }}
        </v-col>
      </v-row>
      <v-row
        v-if="showTrustIndenture && !showEditTrustIndenture"
        noGutters
        class="pt-6"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Trust Indenture
          <div v-if="trustIndentureModified">
            <v-chip
              xSmall
              variant="elevated"
              color="primary"
            >
              AMENDED
            </v-chip>
          </div>
        </v-col>
        <v-col
          cols="7"
          class="summary-text"
        >
          {{ trustIndentureSummary }}
        </v-col>
        <v-col
          cols="2"
          class="text-right"
        >
          <span
            v-if="trustIndentureModified"
            class="edit-action"
          >
            <v-btn
              id="trust-indenture-undo-btn"
              variant="text"
              color="primary"
              class="smaller-button edit-btn pb-4"
              :disabled="editInProgress"
              @click="undoTrustIndenture()"
            >
              <v-icon size="small">mdi-undo</v-icon>
              <span>Undo</span>
            </v-btn>
          </span>
          <span
            v-else
            class="edit-action"
          >
            <v-btn
              id="trust-indenture-amend-btn"
              variant="text"
              color="primary"
              class="smaller-button edit-btn pb-4"
              :disabled="editInProgress"
              @click="initEdit()"
            >
              <v-icon size="small">mdi-pencil</v-icon>
              <span>Amend</span>
            </v-btn>
          </span>
        </v-col>
      </v-row>
      <!-- Edit -->
      <v-row
        v-if="showEditTrustIndenture"
        noGutters
      >
        <v-col
          cols="12"
          class="edit-debtor-container pa-0"
        >
          <edit-trust-indenture
            :currentTrustIndenture="trustIndenture"
            @editTrustIndenture="resetEdit"
            @resetEvent="resetEdit"
          />
        </v-col>
      </v-row>
    </v-card>
    <v-container
      v-else
      class="bg-white pa-0 noGutters"
      fluid
    >
      <v-row
        noGutters
        class="py-8"
      >
        <v-col
          cols="3"
          class="generic-label pl-3"
        >
          Trust Indenture
          <div v-if="trustIndentureModified">
            <v-chip
              xSmall
              variant="elevated"
              color="primary"
            >
              AMENDED
            </v-chip>
          </div>
        </v-col>
        <v-col
          cols="9"
          class="summary-text"
        >
          {{ trustIndentureSummary }}
        </v-col>
      </v-row>
    </v-container>
  </div>
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
} from 'vue'
import { useStore } from '@/store/store'
import EditTrustIndenture from './EditTrustIndenture.vue'
import { LengthTrustIF } from '@/interfaces'
import { formatExpiryDate } from '@/utils'
import { APIRegistrationTypes } from '@/enums'
import { storeToRefs } from 'pinia'

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
  emits: ['lengthTrustOpen'],
  setup (props, context) {
    const { setLengthTrust } = useStore()
    const {
      // Getters
      getLengthTrust,
      getOriginalLengthTrust,
      getRegistrationType,
      getRegistrationExpiryDate
    } = storeToRefs(useStore())
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
          return formatExpiryDate(new Date(new Date(getRegistrationExpiryDate.value)
            .toLocaleString('en-US', { timeZone: 'America/Vancouver' })))
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

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
