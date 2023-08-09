<template>
   <div id="qs-review-confirm">
    <section id="qs-submitting-party">
      <AccountInfo
        title="Submitting Party for this Application"
        tooltipContent="The default Submitting Party is based on your BC Registries user account information. This
          information can be updated within your account settings."
        :accountInfo="getMhrQsSubmittingParty"
      />
    </section>

    <section id="qs-confirm-requirements" class="mt-15">
      <h2>Confirm</h2>
      <p class="mt-1">
        The following requirements must be confirmed
      </p>
      <ConfirmRequirements :validateReview="validateReview" />
    </section>

    <section id="qs-authorization" class="mt-15">
      <h2>Authorization</h2>
      <p class="mt-1">
        Enter the legal name of the person authorized to complete and submit this application.
        <b>Note:</b> The authorized person must be an active B.C. lawyer or notary in good standing.
      </p>
      <Authorization :validateReview="validateReview" />
    </section>

  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { AccountInfo } from '@/components/common'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { ConfirmRequirements, Authorization } from '@/components/userAccess/ReviewConfirm'

export default defineComponent({
  name: 'QsReviewConfirm',
  components: { AccountInfo, Authorization, ConfirmRequirements },
  props: { validateReview: { type: Boolean, default: false } },
  setup () {
    const { setMhrQsValidation } = useStore()
    const { getMhrQSReviewConfirm, getMhrQsSubmittingParty, getMhrUserAccessValidation } = storeToRefs(useStore())

    const authorizationForm = ref(null)

    const localState = reactive({
      isValid: computed((): boolean => {
        return (
          getMhrUserAccessValidation.value.qsInformationValid &&
          getMhrQSReviewConfirm.value.isRequirementsConfirmed &&
          getMhrQSReviewConfirm.value.authorization.isAuthorizationConfirmed &&
          getMhrQSReviewConfirm.value.authorization.legalName.trim() !== ''
        )
      })
    })

    watch(() => localState.isValid, (val: boolean) => {
      setMhrQsValidation({ key: 'qsReviewConfirmValid', value: val })
    })

    return {
      authorizationForm,
      getMhrQsSubmittingParty,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
