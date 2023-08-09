<template>
  <FormCard
    label="Confirm Requirements"
    :showErrors="validateReview && !getMhrQSReviewConfirm.isRequirementsConfirmed"
    :class="{'border-error-left': validateReview && !getMhrQSReviewConfirm.isRequirementsConfirmed}"
  >
    <template v-slot:formSlot>
      <v-form class="pl-2">
        <ListRequirements />
        <v-checkbox
          class="confirmation-checkbox mt-7"
          hide-details="true"
          v-model="getMhrQSReviewConfirm.isRequirementsConfirmed"
          label="I confirm and agree to all of the above requirements."
        >
          <template #label>
            <span :class="{ 'error-text' : validateReview && !getMhrQSReviewConfirm.isRequirementsConfirmed}">
              I confirm and agree to all of the above requirements.
            </span>
          </template>
        </v-checkbox>
      </v-form>
    </template>
  </FormCard>
</template>

<script lang="ts">
import { defineComponent } from 'vue-demi'
import { FormCard } from '@/components/common'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import ListRequirements from './ListRequirements.vue'

export default defineComponent({
  name: 'ConfirmRequirements',
  components: { FormCard, ListRequirements },
  props: { validateReview: { type: Boolean, default: false } },
  setup () {
    const { getMhrQSReviewConfirm } = storeToRefs(useStore())

    return {
      getMhrQSReviewConfirm
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.confirmation-checkbox {
  background-color: $gray1;
  padding: 2rem;
}
</style>
