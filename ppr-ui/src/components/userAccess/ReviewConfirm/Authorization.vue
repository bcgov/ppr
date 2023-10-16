<template>
  <FormCard
    label="Confirm Authorization"
    :showErrors="showErrors"
    :class="{'border-error-left': showErrors}"
  >
    <template #formSlot>
      <v-form ref="authorizationForm" v-model="authorizationFormValid">
        <v-text-field
          id="authorization-text-field"
          filled
          label="Legal name of authorized person (must be a lawyer or notary)"
          v-model="authorization.authorizationName"
          :rules="authorizationRules"
        />
        <v-checkbox
          id="authorization-checkbox"
          class="mt-1"
          hide-details="true"
          v-model="authorization.isAuthorizationConfirmed"
        >
          <template #label>
            <span
              class="ml-2"
              :class="{ 'error-text': validateReview && !authorization.isAuthorizationConfirmed}"
            >
              <b class=authorization-text>{{ authorization.authorizationName }}</b>
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
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { FormCard } from '@/components/common'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { useInputRules } from '@/composables'
import { UserAccessAuthorizationIF } from '@/interfaces'

export default defineComponent({
  name: 'Authorization',
  components: { FormCard },
  props: { validateReview: { type: Boolean, default: false } },
  setup (props) {
    const { getMhrQsAuthorization } = storeToRefs(useStore())
    const { required, maxLength, customRules } = useInputRules()

    const authorizationForm = ref(null)

    const localState = reactive({
      authorization: getMhrQsAuthorization.value as UserAccessAuthorizationIF,
      authorizationFormValid: false,
      authorizationRules: customRules(required('Enter the legal name of authorized person'), maxLength(150)),
      showErrors: computed((): boolean =>
        props.validateReview &&
        (!authorizationForm.value?.validate() || !localState.authorization.isAuthorizationConfirmed)
      )
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

::v-deep {
  .v-label {
    line-height: 24px;
  }

  .v-input--selection-controls .v-input__slot {
    align-items: flex-start;
  }

  .v-text-field__slot > label {
    height: fit-content;
  }
}
</style>
