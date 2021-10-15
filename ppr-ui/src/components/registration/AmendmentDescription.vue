<template>
  <v-container v-if="!summaryView" fluid no-gutters class="pb-6  px-0 rounded">
    <v-row no-gutters class="summary-header pa-2 mb-8">
      <v-col cols="auto" class="pa-2">
        <v-icon color="darkBlue">mdi-message-text</v-icon>
        <label class="pl-3">
          <strong>Details Description</strong>
        </label>
      </v-col>
    </v-row>
    <v-row no-gutters class="pb-6">
        <v-col>
            If this registration is related to a Subordination, Transfer of Security, or Transfer of Collateral,
            you MUST enter a description of the registration below, otherwise the Details Description is optional.
        </v-col>
    </v-row>
    <v-card
      id="amendment-detail-description"
      :class="{ 'invalid-message': showErrorComponent }"
      flat
    >
      <v-row no-gutters class="py-6">
        <v-col cols="3" class="generic-label pa-4">
          Details Description
        </v-col>
        <v-col cols="9" class="pr-4">
          <v-textarea
            v-model="detailDescription"
            id="amendment-description"
            auto-grow
            counter="4000"
            filled
            label="Details Description (Optional)"
            class="white pt-2 text-input-field"
            :error-messages="valid ? '' : 'Maximum 4000 characters'"
          />
        </v-col>
      </v-row>
    </v-card>
  </v-container>
  <v-container v-else class="white pa-0" fluid no-gutters>
    <h2 class="pl-3">Details Description</h2>
    <v-row no-gutters class="py-8">
      <v-col cols="3" class="generic-label pl-5">
        Details Description
      </v-col>
      <v-col cols="9" class="summary-text pr-4">
        {{ detailDescription }}
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch, computed, onMounted } from '@vue/composition-api'
import { useGetters, useActions } from 'vuex-composition-helpers'

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
    const { getAmendmentDescription } = useGetters<any>(['getAmendmentDescription'])
    const { setAmendmentDescription } = useActions<any>(['setAmendmentDescription'])

    const localState = reactive({
      detailDescription: '',
      summaryView: computed((): boolean => {
        return props.isSummary
      }),
      amendmentDescription: computed((): string => {
        return getAmendmentDescription.value || ''
      }),
      showErrorComponent: computed((): boolean => {
        return (props.setShowErrors && localState.detailDescription.length > 4000)
      }),
      valid: computed((): boolean => {
        return (localState.detailDescription?.length || 0) <= 4000
      })
    })

    onMounted(() => {
      localState.detailDescription = localState.amendmentDescription
    })

    watch(() => localState.detailDescription, (val: string) => {
      emit('valid', localState.valid)
      if (val) {
        setAmendmentDescription(val)
      }
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
