<template>
  <FormCard
    label="Confirm Authorization"
    :show-errors="showErrors"
    :class="{'border-error-left': showErrors}"
  >
    <template #formSlot>
      <v-form
        ref="authorizationForm"
        v-model="authorizationFormValid"
      >
        <v-text-field
          id="authorization-text-field"
          v-model="authorization.authorizationName"
          variant="filled"
          color="primary"
          class="ml-2"
          :label="`Legal name of authorized person ${isLawyerNotary ? '(must be a lawyer or notary)' : ''}`"
          :rules="authorizationRules"
        />
        <v-checkbox
          id="authorization-checkbox"
          v-model="authorization.isAuthorizationConfirmed"
          class="mt-1"
          hide-details
        >
          <template #label>
            <span
              class="ml-2"
              :class="{ 'error-text': validateReview && !authorization.isAuthorizationConfirmed}"
            >
              <b class="authorization-text">{{ authorization.authorizationName }}</b>
              certifies that they have relevant knowledge of the Qualified Supplier
              and is authorized to submit this application.
            </span>
          </template>
        </v-checkbox>
        <div class="mt-5 ml-10">
          <span id="authorization-date"><b>Date:</b> {{ authorization.date }}</span>
          <p class="mt-4 mb-n1 offence-note">
            Note: It is an offence to make or assist in making a false or misleading statement
            in a record filed under the Manufactured Home Act.
            A person who commits this offence is subject to fine of up to $2,000.
          </p>
        </div>
      </v-form>
    </template>
  </FormCard>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from 'vue'
import { FormCard } from '@/components/common'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { useInputRules } from '@/composables'
import type { UserAccessAuthorizationIF } from '@/interfaces'

export default defineComponent({
  name: 'QsAuthorization',
  components: { FormCard },
  props: { validateReview: { type: Boolean, default: false }, isLawyerNotary: { type: Boolean, default: false } },
  setup (props) {
    const { getMhrQsAuthorization } = storeToRefs(useStore())
    const { required, maxLength, customRules } = useInputRules()

    const authorizationForm = ref(null)

    const localState = reactive({
      authorization: getMhrQsAuthorization.value as UserAccessAuthorizationIF,
      authorizationFormValid: false,
      authorizationRules: customRules(
        required('Enter the legal name of authorized person'),
        maxLength(150)
      ),
      showErrors: computed((): boolean =>
        props.validateReview &&
        (!authorizationForm.value?.validate() || !localState.authorization.isAuthorizationConfirmed)
      )
    })

    onMounted(() => {
      // Clear authorization name from model for Lawyers and Notaries to prevent pre-population
      localState.authorization.authorizationName = !props.isLawyerNotary
        ? getMhrQsAuthorization.value.authorizationName
        : ''
    })

    watch(() => props.validateReview, () => {
      authorizationForm.value?.validate()
    })

    return {
      getMhrQsAuthorization,
      authorizationForm,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.offence-note {
  line-height: 22px;
  font-size: 14px;
}

.authorization-text {
  word-break: break-all;
}

span {
  color: $gray7;
}

:deep(.v-label) {
  line-height: 24px;
}

:deep(.v-checkbox .v-selection-control) {
  align-items: baseline;
}

:deep(.v-text-field__slot > label) {
  height: fit-content;
}
</style>
