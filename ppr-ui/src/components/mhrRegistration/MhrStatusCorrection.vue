<template>
  <div id="mhr-status-correction">
    <v-row
      noGutters
      class="fs-16 align-center mr-1"
    >
      <v-col
        cols="5"
        class="text-no-wrap mx-6 px-6"
      >
        <v-tooltip
          contentClass="bottom-tooltip"
          location="bottom"
          transition="fade-transition"
        >
          <template #activator="{ props }">
            <v-icon
              v-if="displayStatusOptions"
              color="primary"
              v-bind="props"
              class="mr-1"
              tabindex="0"
            >
              mdi-information-outline
            </v-icon>
          </template>
          {{ mhrStatusToolTip }}
        </v-tooltip>
        <span class="generic-label">Registration Status:</span>
      </v-col>
      <v-col v-if="displayStatusOptions">
        <v-radio-group
          id="mhr-status-correction-options"
          v-model="mhrStatus"
          inline
          hideDetails="true"
        >
          <v-tooltip
            contentClass="bottom-tooltip"
            location="bottom"
            transition="fade-transition"
          >
            <template #activator="{ props }">
              <v-radio
                id="active-option"
                class="pr-2"
                :value="MhApiStatusTypes.ACTIVE"
              >
                <template #label>
                  <span v-bind="props">Active</span>
                </template>
              </v-radio>
            </template>
            {{ mhrStatusToolTip }}
          </v-tooltip>
          <v-tooltip
            contentClass="bottom-tooltip"
            location="bottom"
            transition="fade-transition"
          >
            <template #activator="{ props }">
              <v-radio
                id="business-option"
                :value="MhApiStatusTypes.EXEMPT"
              >
                <template #label>
                  <span v-bind="props">Exempt</span>
                </template>
              </v-radio>
            </template>
            {{ mhrStatusToolTip }}
          </v-tooltip>
        </v-radio-group>
      </v-col>
      <v-col
        v-else
        class="ml-1 py-2 text-center"
      >
        <p>{{ mhrStatus === MhApiStatusTypes.ACTIVE ? MhUIStatusTypes.ACTIVE : MhUIStatusTypes.EXEMPT }}</p>
      </v-col>
    </v-row>
    <v-row
      noGutter
      class="mt-0"
    >
      <v-col cols="2" />
      <v-col class="py-0 mt-n1">
        <UpdatedBadge
          class="ml-n2"
          :action="correctionState.action"
          :baseline="correctionState.status.baseline"
          :currentState="correctionState.status.currentState"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { MhApiStatusTypes, MhUIStatusTypes, RouteNames } from '@/enums'
import { UpdatedBadge } from '@/components/common'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useMhrCorrections, useNavigation } from '@/composables'

const { containsCurrentRoute } = useNavigation()
const { setMhrCorrectStatusType } = useStore()
const { getMhrInformation } = storeToRefs(useStore())
const { correctionState } = useMhrCorrections()

const mhrStatus = ref(getMhrInformation.value?.statusType)
const displayStatusOptions = computed((): boolean => {
  return !containsCurrentRoute([RouteNames.MHR_REVIEW_CONFIRM])
})
const mhrStatusToolTip = 'Changing the Registration Status from Exempt to Active on a home with a Residential or ' +
  'Non-Residential Exemption will cancel the Exemption Order(s) and remove the Exemption Unit Note(s) from search' +
  ' results.'

/** Called on mount and when mhrStatus updates. */
watch(() => mhrStatus, async (status: MhApiStatusTypes) => {
  await setMhrCorrectStatusType(status)
}, { immediate: true })

</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.v-icon {
  margin-top: -2px;
}
</style>
