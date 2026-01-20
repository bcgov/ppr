<template>
  <div class="ma-0 pa-0">
    <v-row no-gutters>
      <v-col class="tombstone-header">
        <h1 class="fs-20 lh-30">
          {{ header }}
        </h1>
      </v-col>
      <v-col
        class="ml-16 tombstone-info"
        style="padding-top: 0.375rem;"
      >
        <v-row
          v-if="!isMhrInformation && !isMhrCorrection && !isMhrReRegistration &&
          !isRouteName(RouteNames.MHR_QUEUE_TRANSFER)"
          justify="end"
          no-gutters
        >
          <v-col
            class="generic-label"
            cols="6"
          >
            <p class="float-right">
              {{ dateTimePrefix }} Registration Date and Time:
            </p>
          </v-col>
          <v-col
            class="pl-3"
            cols="6"
          >
            <p>{{ creationDate }}</p>
          </v-col>
        </v-row>
        <v-row
          v-if="isMhrCorrection"
          class="float-right"
        >
          <MhrStatusCorrection />
        </v-row>
        <v-row
          v-else-if="isMhrInformation || isMhrCorrection || isMhrReRegistration ||
            isRouteName(RouteNames.MHR_QUEUE_TRANSFER)"
          justify="end"
          class="fs-16 pr-5"
          no-gutters
        >
          <v-col>
            <div
              class="float-right"
              data-test-id="mhr-reg-status"
            >
              <dl class="d-flex">
                <dt class="generic-label mr-3">
                  Registration Status:
                </dt>
                <dd>{{ statusType }}</dd>
              </dl>
              <UpdatedBadge
                v-if="showAmendedRegStatusBadge"
                action="AMENDED"
                :baseline="getMhrOriginalTransportPermitRegStatus"
                :current-state="getMhrInformation.statusType"
                style="position: absolute"
              />
              <div v-else-if="showRestoredStatusBadge">
                <InfoChip
                  action="RESTORED"
                  data-test-id="restored-badge"
                  style="position: absolute"
                />
              </div>
            </div>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row
      v-if="!isMhrInformation && !isMhrCorrection && !isMhrReRegistration &&
      !isRouteName(RouteNames.MHR_QUEUE_TRANSFER)"
      class="pt-1 tombstone-sub-header"
      no-gutters
    >
      <v-col>
        <p>{{ isRlTransition ? 'Commercial Lien' : registrationType }}</p>
        <p v-if="isRlTransition || isConvertedCl"><i>(Converted from Repairers Lien {{ getRegistrationNumber }})</i></p>
      </v-col>
      <v-col
        class="ml-16 tombstone-info"
        style="padding-top: 0.125rem;"
      >
        <v-row
          justify="end"
          no-gutters
        >
          <v-col
            class="generic-label"
            cols="6"
          >
            <p class="float-right">
              Current Expiry Date and Time:
            </p>
          </v-col>
          <v-col
            class="pl-3"
            cols="6"
          >
            <p>{{ expiryDate }}</p>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <!-- Mhr Amend/Correct Btns -->
    <v-row
      v-if="isMhrChangesEnabled && isRouteName(RouteNames.MHR_INFORMATION) && !isCancelledMhr"
      no-gutters
      class="mt-2 mb-n4"
    >
      <!-- Public Amendment Btn -->
      <v-btn
        id="public-amend-btn"
        class="pl-0"
        color="primary"
        variant="plain"
        role="link"
        :ripple="false"
        :disabled="actionInProgress || isCancelChangeLocationActive || isExtendChangeLocationActive"
        @click="initMhrCorrection(MhrPublicAmendment)"
      >
        <v-icon
          color="primary"
          class="mr-1"
        >
          mdi-file-document-edit-outline
        </v-icon>
        <span class="fs-14">Public Amendment</span>
      </v-btn>

      <v-menu
        location="bottom right"
      >
        <template #activator="{ props, isActive }">
          <!-- Registry Correction Btn -->
          <v-btn
            id="registry-correction-btn"
            class="pr-0"
            color="primary"
            variant="plain"
            v-bind="props"
            role="link"
            :ripple="false"
            :disabled="actionInProgress || isCancelChangeLocationActive || isExtendChangeLocationActive"
          >
            <v-icon
              color="primary"
              class="mr-1"
            >
              mdi-file-document-edit-outline
            </v-icon>
            <span class="fs-14">Registry Correction</span>
          </v-btn>

          <v-btn
            variant="plain"
            color="primary"
            class="ml-n3 px-0"
            v-bind="props"
            :ripple="false"
            :disabled="actionInProgress || isCancelChangeLocationActive"
          >
            <v-icon v-if="isActive">
              mdi-menu-up
            </v-icon>
            <v-icon v-else>
              mdi-menu-down
            </v-icon>
          </v-btn>
        </template>

        <!-- Correction actions drop down list -->
        <v-list>
          <v-list-item @click="initMhrCorrection(MhrCorrectionStaff)">
            <v-list-item-subtitle class="pa-0">
              <span class="ml-1">Staff Error or Omission</span>
            </v-list-item-subtitle>
          </v-list-item>
          <v-list-item @click="initMhrCorrection(MhrCorrectionClient)">
            <v-list-item-subtitle class="pa-0">
              <span class="ml-1">Client Error or Omission</span>
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-menu>

      <!-- Staff-only: Mhr History Open-in-new Btn -->
      <v-btn
        id="mhr-history-btn"
        class="pl-1"
        color="primary"
        variant="plain"
        role="link"
        :ripple="false"
        @click="openMhrHistory"
      >
        <v-icon
          color="primary"
          class="mr-1"
        >
          mdi-history
        </v-icon>
        <span class="fs-14">Historical Home Information</span>
      </v-btn>
    </v-row>
    <v-row v-else>
      <v-col>
        <v-spacer />
      </v-col>
    </v-row>
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
import { useStore } from '@/store/store'
import { enumToLabel, formatExpiryDate, pacificDate } from '@/utils'
import type { RegistrationTypeIF } from '@/interfaces'
import { MhApiStatusTypes, MhUIStatusTypes, RouteNames } from '@/enums'
import { useMhrCorrections, useMhrInformation, useNavigation, useTransportPermits } from '@/composables'
import { storeToRefs } from 'pinia'
import { useAnalystQueueStore } from '@/store/analystQueue'
import { MhrCorrectionClient, MhrCorrectionStaff, MhrPublicAmendment } from '@/resources'
import MhrStatusCorrection from '@/components/mhrRegistration/MhrStatusCorrection.vue'
import { InfoChip, UpdatedBadge } from '@/components/common'

export default defineComponent({
  name: 'TombstoneDynamic',
  components: { MhrStatusCorrection, UpdatedBadge, InfoChip },
  props: {
    isMhrInformation: {
      type: Boolean,
      default: false
    },
    actionInProgress: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const {
      isRoleStaffReg,
      isConvertedCl,
      isRlTransition,
      getRegistrationCreationDate,
      getRegistrationExpiryDate,
      getRegistrationNumber,
      getRegistrationType,
      getMhrInformation,
      getMhrOriginalTransportPermitRegStatus,
      isMhrReRegistration
    } = storeToRefs(useStore())

    const { queueTransfer } = storeToRefs(useAnalystQueueStore())
    const { isRouteName } = useNavigation()
    const { isFrozenMhr, isCancelledMhr } = useMhrInformation()
    const { initMhrCorrection, isMhrChangesEnabled, isMhrCorrection } = useMhrCorrections()

    const {
      isAmendLocationActive,
      isCancelChangeLocationActive,
      hasMhrStatusChangedToActive,
      isExtendChangeLocationActive
    } = useTransportPermits()

    const localState = reactive({
      creationDate: computed((): string => {
        if (getRegistrationCreationDate.value) {
          const date = new Date(getRegistrationCreationDate.value)
          return pacificDate(date)
        }
        if (getMhrInformation.value?.createDateTime) {
          const date = new Date(getMhrInformation.value.createDateTime)
          return pacificDate(date)
        }
        return ''
      }),
      expiryDate: computed((): string => {
        if (getRegistrationExpiryDate.value) {
          return formatExpiryDate(new Date(new Date(getRegistrationExpiryDate.value)
            .toLocaleString('en-US', { timeZone: 'America/Vancouver' })))
        }
        return 'No Expiry'
      }),
      statusType: computed((): string => {
        // On the analyst queue transfer page, reflect the current review status.
        if (isRouteName(RouteNames.MHR_QUEUE_TRANSFER)) {
          return enumToLabel(queueTransfer.value?.status)
        }

        const regStatus = getMhrInformation.value?.statusType || ''

        if (localState.showRestoredStatusBadge) return MhUIStatusTypes.ACTIVE

        if (isFrozenMhr.value || regStatus === MhApiStatusTypes.DRAFT) return MhUIStatusTypes.ACTIVE

        return enumToLabel(regStatus)
      }),
      header: computed((): string => {
        const numberType = getRegistrationNumber.value ? 'Base' : 'Manufactured Home'
        const regNum = getRegistrationNumber.value || getMhrInformation.value.mhrNumber || ''

        return numberType + ' Registration Number ' + regNum
      }),
      registrationType: computed((): string => {
        const registration = getRegistrationType.value as RegistrationTypeIF
        return registration?.registrationTypeUI || ''
      }),
      dateTimePrefix: computed(() => {
        return getRegistrationNumber.value ? 'Base' : 'MH'
      }),
      showAmendedRegStatusBadge: computed((): boolean => {
        // list all conditions to show the Amended badge
        return isAmendLocationActive.value
      }),
      showRestoredStatusBadge: computed((): boolean => {
        // for Cancelled Transport Permits, show badge (on Review page only) if home is moving back to BC
        return props.actionInProgress && isCancelChangeLocationActive.value && hasMhrStatusChangedToActive.value
      }),
    })

    const openMhrHistory = () => {
      if (getMhrInformation.value?.mhrNumber) {
        window.open(`/mhr-history?mhrNumber=${getMhrInformation.value?.mhrNumber}`, '_blank')
      }
    }

    return {
      isRoleStaffReg,
      openMhrHistory,
      RouteNames,
      isRouteName,
      isConvertedCl,
      isCancelledMhr,
      isMhrCorrection,
      isRlTransition,
      initMhrCorrection,
      isMhrChangesEnabled,
      MhrCorrectionStaff,
      MhrCorrectionClient,
      MhrPublicAmendment,
      getRegistrationNumber,
      getMhrOriginalTransportPermitRegStatus,
      isCancelChangeLocationActive,
      isExtendChangeLocationActive,
      isAmendLocationActive,
      getMhrInformation,
      isMhrReRegistration,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/theme.scss' as *;
</style>
