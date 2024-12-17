<template>
  <div id="qs-review-confirm">
    <section class="qs-review-intro mt-10">
      <h2>Review and Confirm</h2>
      <p class="mt-2">
        Review the information in your application and complete the additional information below. If you need to change
        anything, return to the previous step to make the necessary change.
      </p>

      <CautionBox
        class="mt-8"
        set-msg="After applying, an email notification will be sent to the Submitting Party once your request has been
          reviewed."
      />
    </section>

    <section
      id="qs-information-review"
      class="mt-15"
    >
      <QsInformationReview />
    </section>

    <section
      id="qs-submitting-party"
      class="mt-15"
    >
      <AccountInfo
        title="Submitting Party for this Application"
        tooltip-content="The default Submitting Party is based on your BC Registries user account information. This
          information can be updated within your account settings."
        :account-info="getMhrQsSubmittingParty"
      />
    </section>

    <div class="increment-sections">
      <section
        id="qs-confirm-requirements"
        class="mt-15"
      >
        <h2>Confirm</h2>
        <p class="mt-1">
          The following requirements must be confirmed.
        </p>
        <ConfirmRequirements
          class="mt-6"
          :validate-review="validateReview"
        />
      </section>

      <section
        id="qs-authorization"
        class="mt-15"
      >
        <h2>Authorization</h2>
        <p class="mt-1">
          Enter the legal name of the person authorized to complete and submit this application.
          <span v-if="getMhrSubProduct === MhrSubTypes.LAWYERS_NOTARIES">
            <b>Note:</b> The authorized person must be an active B.C. lawyer or notary in good standing.
          </span>
        </p>
        <QsAuthorization
          class="mt-6"
          :is-lawyer-notary="getMhrSubProduct === MhrSubTypes.LAWYERS_NOTARIES"
          :validate-review="validateReview"
        />
      </section>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from 'vue'
import { AccountInfo, CautionBox } from '@/components/common'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { ConfirmRequirements, QsAuthorization, QsInformationReview } from '@/components/userAccess/ReviewConfirm'
import { useUserAccess } from '@/composables'
import { MhrSubTypes } from '@/enums'

export default defineComponent({
  name: 'QsReviewConfirm',
  components: { CautionBox, AccountInfo, QsAuthorization, ConfirmRequirements, QsInformationReview },
  props: { validateReview: { type: Boolean, default: false } },
  setup () {
    const { setMhrQsValidation } = useStore()
    const { getMhrQsSubmittingParty, getMhrSubProduct } = storeToRefs(useStore())
    const { isValid } = useUserAccess()
    const localState = reactive({})

    watch(() => isValid.value, (val: boolean) => {
      setMhrQsValidation({ key: 'qsReviewConfirmValid', value: val })
    })

    return {
      MhrSubTypes,
      getMhrSubProduct,
      getMhrQsSubmittingParty,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
