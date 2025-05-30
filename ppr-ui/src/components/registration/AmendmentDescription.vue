<template>
  <v-container
    v-if="!summaryView"
    fluid
    class="pb-6 px-0 rounded noGutters"
  >
    <v-row
      no-gutters
      class="summary-header pa-2 rounded-top"
    >
      <v-col
        cols="auto"
        class="py-2 px-4"
      >
        <v-icon color="darkBlue">
          mdi-message-text
        </v-icon>
        <label class="pl-3">
          <strong>Details Description</strong>
        </label>
      </v-col>
    </v-row>
    <v-card
      id="amendment-detail-description"
      class="px-4"
      :class="{ 'border-error-left': showErrorComponent }"
      flat
    >
      <v-row class="pt-6">
        <v-col class="pa-4 pl-5 summary-text">
          <p v-if="isSecurityActNotice">
            If this registration is related to a partial transfer of collateral to a new debtor, then enter the
            prescribed information below, otherwise the Details Description is optional.
          </p>
          <p v-else>
            If this registration is related to a Subordination, Partial secured party transfer, or
            Partial transfer of collateral to a new debtor, you MUST enter the prescribed information below,
            otherwise the Details Description is optional.
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col
          cols="3"
          class="generic-label py-4 px-2"
        >
          Details Description
        </v-col>
        <v-col
          cols="9"
          class="pr-4"
        >
          <v-textarea
            id="amendment-description"
            v-model="detailDescription"
            auto-grow
            counter="4000"
            variant="filled"
            color="primary"
            label="Details Description (Optional)"
            class="bg-white pt-2 text-input-field"
            :error-messages="valid ? '' : 'Maximum 4000 characters'"
          />
        </v-col>
      </v-row>
    </v-card>
  </v-container>
  <v-container
    v-else
    class="bg-white pa-0 noGutters"
    fluid
  >
    <v-row
      no-gutters
      class="py-8"
    >
      <v-col class="generic-label pl-3">
        Details Description
      </v-col>
      <v-col
        cols="9"
        class="summary-text pr-4 pl-5"
      >
        <span style="white-space: pre-wrap">{{ detailDescription }}</span>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch, computed } from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { usePprRegistration } from '@/composables'

export default defineComponent({
  props: {
    isSummary: {
      type: Boolean,
      default: false
    },
    setShowErrors: {
      type: Boolean,
      default: false
    }
  },
  emits: ['valid'],
  setup (props, { emit }) {
    const { setAmendmentDescription } = useStore()
    const { getAmendmentDescription } = storeToRefs(useStore())
    const { isSecurityActNotice } = usePprRegistration()
    const localState = reactive({
      detailDescription: getAmendmentDescription.value || '',
      summaryView: computed((): boolean => {
        return props.isSummary
      }),
      amendmentDescription: computed((): string => {
        return getAmendmentDescription.value || ''
      }),
      showErrorComponent: computed((): boolean => {
        return (props.setShowErrors && !localState.valid)
      }),
      valid: computed((): boolean => {
        return (localState.detailDescription?.length || 0) <= 4000
      })
    })

    watch(() => localState.detailDescription, (val: string) => {
      emit('valid', localState.valid)
      setAmendmentDescription(val)
    })

    return {
      isSecurityActNotice,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
