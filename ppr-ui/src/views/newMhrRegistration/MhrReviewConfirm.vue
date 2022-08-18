<template>
  <div id="mhr-review-confirm">
    <!-- Review and Confirm -->
    <div class="mt-10">
      <h2>Review and Confirm</h2>
      <p class="mt-4">
        Review the information in your registration and complete the additional information below. If you need to
        change anything, return to the previous step to make the necessary change.
      </p>

      <!-- Your Home Summary -->
      <YourHomeReview />

      <!-- Submitting Party Review -->
      <SubmittingPartyReview />

      <!-- Home Location Review -->
      <HomeLocationReview />
    </div>

    <!-- Authorization -->
    <section id="mh-certify-section" class="mt-10 pt-4">
      <CertifyInformation
        isMhr
        :setShowErrors="validateReview"
        @certifyValid="authorizationValid = $event"
      />
    </section>

    <!-- Staff Payment -->
    <section id="mhr-staff-payment-section" class="mt-10" v-if="true">
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
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { HomeLocationReview, SubmittingPartyReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
import { CertifyInformation } from '@/components/common'
import { useMhrValidations } from '@/composables'
import { RouteNames } from '@/enums'
import { useGetters } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'MhrReviewConfirm',
  components: {
    YourHomeReview,
    SubmittingPartyReview,
    HomeLocationReview,
    CertifyInformation
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
      scrollToInvalid,
      getValidation,
      getStepValidation,
      getSectionValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      authorizationValid: false,
      validateReview: computed(() => {
        return getSectionValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.AUTHORIZATION_VALID) &&
          getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP)
      })
    })

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
          scrollToInvalid(MhrSectVal.REVIEW_CONFIRM_VALID, 'mhr-review-confirm',
            [
              getStepValidation(MhrSectVal.YOUR_HOME_VALID),
              getStepValidation(MhrSectVal.SUBMITTING_PARTY_VALID),
              getStepValidation(MhrSectVal.HOME_OWNERS_VALID),
              getStepValidation(MhrSectVal.LOCATION_VALID)
            ])
          setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_STEPS, true)
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
