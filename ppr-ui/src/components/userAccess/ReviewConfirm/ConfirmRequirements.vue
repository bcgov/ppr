<template>
  <FormCard
    label="Confirm Requirements"
    :show-errors="validateReview && !isRequirementsConfirmed"
    :class="{'border-error-left': validateReview && !isRequirementsConfirmed}"
  >
    <template #formSlot>
      <v-form>
        <ListRequirements
          class="pl-1"
          :requirements="requirements"
        />
        <v-checkbox
          v-model="isRequirementsConfirmed"
          class="confirmation-checkbox mt-7 ml-n4"
          hide-details
          label="I confirm and agree to all of the above requirements."
        >
          <template #label>
            <span :class="{ 'error-text' : validateReview && !isRequirementsConfirmed}">
              I confirm and agree to all of the above requirements.
            </span>
          </template>
        </v-checkbox>
      </v-form>
    </template>
  </FormCard>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { FormCard } from '@/components/common'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import ListRequirements from './ListRequirements.vue'
import { userAccessRequirements } from '@/resources'
import type { RequirementsConfigIF } from '@/interfaces'

export default defineComponent({
  name: 'ConfirmRequirements',
  components: { FormCard, ListRequirements },
  props: { validateReview: { type: Boolean, default: false } },
  setup () {
    const { setMhrQsIsRequirementsConfirmed } = useStore()
    const { getMhrQsIsRequirementsConfirmed, getMhrSubProduct } = storeToRefs(useStore())

    const localState = reactive({
      isRequirementsConfirmed: !!getMhrQsIsRequirementsConfirmed.value,
      requirements: computed((): RequirementsConfigIF[] => userAccessRequirements[getMhrSubProduct.value])
    })

    watch(() => localState.isRequirementsConfirmed, (val) => {
      setMhrQsIsRequirementsConfirmed(val)
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.confirmation-checkbox {
  background-color: $gray1;
  padding: .75rem 1rem;
}
</style>
