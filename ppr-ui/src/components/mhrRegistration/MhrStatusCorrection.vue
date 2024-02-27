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
              class="mt-n1 mr-1"
            >
              mdi-information-outline
            </v-icon>
          </template>
          Changing the Registration Status from Exempt to Active on a home with a Residential or Non-Residential
          Exemption will cancel the Exemption Order(s) and remove the Exemption Unit Note(s) from search results.
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
          <v-radio
            id="active-option"
            class="pr-2"
            label="Active"
            :value="MhApiStatusTypes.ACTIVE"
          />
          <v-radio
            id="business-option"
            label="Exempt"
            :value="MhApiStatusTypes.EXEMPT"
          />
        </v-radio-group>
      </v-col>
      <v-col
        v-else
        class="ml-4 py-2 text-center"
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
          :baseline="getMhrBaseline?.statusType"
          :currentState="getMhrStatusType"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { MhApiStatusTypes, MhUIStatusTypes, RouteNames } from '@/enums'
import { UpdatedBadge } from '@/components/common'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { useNavigation } from '@/composables'

export default defineComponent({
  name: 'MhrStatusCorrection',
  components: { UpdatedBadge },
  setup () {
    const { containsCurrentRoute } = useNavigation()
    const { setMhrCorrectStatusType } = useStore()
    const {
      getMhrBaseline,
      getMhrStatusType,
      getMhrInformation
    } = storeToRefs(useStore())

    const localState = reactive({
      mhrStatus: getMhrInformation.value?.statusType,
      displayStatusOptions: computed((): boolean => {
        return !containsCurrentRoute([RouteNames.MHR_REVIEW_CONFIRM])
      })
    })

    /** Called on mount and when mhrStatus updates. */
    watch(() => localState.mhrStatus, async (status: MhApiStatusTypes) => {
      await setMhrCorrectStatusType(status)
    }, { immediate: true })

    return {
      getMhrBaseline,
      getMhrStatusType,
      getMhrInformation,
      MhUIStatusTypes,
      MhApiStatusTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
