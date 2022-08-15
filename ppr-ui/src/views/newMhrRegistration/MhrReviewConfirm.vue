<template>
  <div id="mhr-review-confirm">
    <!-- Review and Confirm -->
    <section class="mt-10">
      <article>
        <h2>Review and Confirm</h2>
        <p class="mt-4">
          Review the information in your registration and complete the additional information below. If you need to
          change anything, return to the previous step to make the necessary change.
        </p>
      </article>

      <!-- Your Home Summary -->
      <YourHomeReview />

      <!-- Submitting Party Review -->
      <SubmittingPartyReview />

      <!-- Home Location Review -->
      <HomeLocationReview />
    </section>

    <!-- Transactional Folio Number -->
    <section id="folio-number-section" class="mt-10" v-if="false">
      <article>
        <h2>Folio or Reference Number</h2>
        <p class="mt-4">
          Enter the folio or reference number you want to use for this filing for your own tracking
          purposes. The Business Folio or Reference Number is displayed below (if available).
          Entering a different value below will not change the Business Folio or Reference Number.
          Only the number below will appear on the transaction report and receipt for this filing.
        </p>
      </article>

      <v-card flat class="mt-6">
       <!-- Folio Number Placeholder -->
      </v-card>
    </section>

    <!-- Certify -->
    <section id="certify-section" class="mt-10" v-if="false">
      <article>
        <h2>Certify</h2>
        <p class="mt-4">
          Confirm the legal name of the person authorized to complete and submit this dissolution.
        </p>
      </article>

      <v-card flat class="mt-6">
        <!-- Certify Placeholder -->
      </v-card>
    </section>

    <!-- Staff Payment -->
    <section id="staff-payment-section" class="mt-10" v-if="false">
      <article>
        <h2>Staff Payment</h2>
        <p class="mt-4"></p>
      </article>

      <v-card flat class="mt-6">
        <!-- Staff Payment Piece -->
      </v-card>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { HomeLocationReview, SubmittingPartyReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
import { useMhrValidations } from '@/composables'
import { RouteNames } from '@/enums'
import { useGetters } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'MhrReviewConfirm',
  components: {
    YourHomeReview,
    SubmittingPartyReview,
    HomeLocationReview
  },
  props: {},
  setup (props, context) {
    const {
      getMhrRegistrationValidationModel
    } = useGetters<any>([
      'getMhrRegistrationValidationModel'
    ])

    const {
      MhrCompVal,
      MhrSectVal,
      setValidation,
      scrollToInvalid
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({})

    watch(() => context.root.$route.name, (route: string) => {
      switch (route) {
        case RouteNames.YOUR_HOME:
          scrollToInvalid(MhrSectVal.YOUR_HOME_VALID, 'mhr-describe-your-home')
          break
        case RouteNames.SUBMITTING_PARTY:
          scrollToInvalid(MhrSectVal.SUBMITTING_PARTY_VALID, 'mhr-submitting-party')
          break
        case RouteNames.HOME_OWNERS:
          scrollToInvalid(MhrSectVal.HOME_OWNERS_VALID, 'mhr-home-owners-list')
          break
        case RouteNames.HOME_LOCATION:
          scrollToInvalid(MhrSectVal.LOCATION_VALID, 'mhr-home-location')
          break
        case RouteNames.MHR_REVIEW_CONFIRM:
          setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP, true)
          break
      }
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
