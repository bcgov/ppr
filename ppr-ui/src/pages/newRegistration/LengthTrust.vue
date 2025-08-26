<template>
  <v-container
    v-if="dataLoaded"
    class="pa-0 footer-view-container"
  >
    <div class="py-0">
      <div class="pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row
              id="registration-header"
              no-gutters
              class="length-trust-header pt-3 pb-3 soft-corners-top"
            >
              <v-col cols="auto">
                <h2 class="fs-32 lh-36">
                  {{ registrationTypeUI }}
                </h2>
              </v-col>
            </v-row>
            <Stepper
              class="mt-4"
              :step-config="getPprSteps"
              :show-step-errors="showStepErrors"
            />
            <v-row
              no-gutters
              class="pt-10"
            >
              <v-col
                cols="auto"
                class="sub-header"
              >
                <h3 class="lh-22">
                  {{ registrationTitle }}
                </h3>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col class="pt-2 pb-6 sub-header-info">
                {{ registrationLengthMessage }}
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <RegistrationLengthTrust v-if="registrationType !== registrationTypeRL" />
                <RegistrationRepairersLien v-else />
              </v-col>
            </v-row>

            <!-- Security Act Notice Components -->
            <template v-if="isSecurityActNotice">
              <SecuritiesActNotices />
            </template>
          </v-col>
          <v-col
            class="pl-6 pt-5"
            cols="3"
          >
            <aside>
              <StickyContainer
                :show-connect-fees="true"
                :set-right-offset="true"
                :set-show-fee-summary="true"
                :set-fee-type="feeType"
                :set-registration-length="registrationLength"
                :set-registration-type="registrationTypeUI"
              />
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
    <ButtonFooter
      :nav-config="getFooterButtonConfig"
      :current-step-name="stepName"
      @error="emitError($event)"
    />
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { Stepper, StickyContainer } from '@/components/common'
import ButtonFooter from '@/components/common/ButtonFooter.vue'
import { RegistrationLengthTrust, RegistrationRepairersLien, SecuritiesActNotices } from '@/components/registration'
import type { UIRegistrationTypes } from '@/enums';
import { APIRegistrationTypes, RegistrationFlowType, RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import type { ErrorIF } from '@/interfaces'
import type { RegistrationLengthI } from '@/composables/fees/interfaces'
import { storeToRefs } from 'pinia'
import { useAuth, useNavigation, usePprRegistration } from '@/composables'
import { useConnectFeeStore } from '@/store/connectFee'
import { RegistrationFees } from '@/resources'
import { hasNoCharge } from '@/composables/fees/factories'

export default defineComponent({
  name: 'LengthTrust',
  components: {
    ButtonFooter,
    RegistrationLengthTrust,
    RegistrationRepairersLien,
    Stepper,
    SecuritiesActNotices,
    StickyContainer
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    }
  },
  emits: ['error', 'haveData'],
  setup (props, context) {
    const { goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const { isSecurityActNotice } = usePprRegistration()
    const { setFees } = useConnectFeeStore()
    const { fees, feeOptions } = storeToRefs(useConnectFeeStore())
    const { setLengthTrustStepValidity } = useStore()
    const {
      isRoleStaffReg,
      getPprSteps,
      showStepErrors,
      getLengthTrust,
      getRegistrationType,
      getRegistrationOther,
      getRegistrationFlowType,
      getFooterButtonConfig,
      getSecuritiesActNotices
    } = storeToRefs(useStore())

    const localState = reactive({
      dataLoaded: false,
      feeType: FeeSummaryTypes.NEW,
      stepName: RouteNames.LENGTH_TRUST,
      registrationLength: computed((): RegistrationLengthI => {
        return {
          lifeInfinite: getLengthTrust.value?.lifeInfinite || false,
          lifeYears: getLengthTrust.value?.lifeYears || 0
        }
      }),
      registrationTypeUI: computed((): UIRegistrationTypes => {
        if (getRegistrationType.value?.registrationTypeAPI === APIRegistrationTypes.OTHER) {
          return getRegistrationOther.value || ''
        }
        return getRegistrationType.value?.registrationTypeUI || ''
      }),
      registrationType: computed((): APIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeAPI || ''
      }),
      registrationTypeRL: computed((): APIRegistrationTypes => {
        return APIRegistrationTypes.REPAIRERS_LIEN
      }),
      registrationTitle: computed((): string => {
        switch (localState.registrationType) {
          case APIRegistrationTypes.SECURITY_AGREEMENT:
            return 'Registration Length and Trust Indenture'
          case APIRegistrationTypes.SECURITY_ACT_NOTICE:
            return 'Registration Details'
          case APIRegistrationTypes.REPAIRERS_LIEN:
            return 'Terms of Repairers Lien'
          default:
            return 'Registration Length'
        }
      }),
      registrationLengthMessage: computed((): string => {
        switch (localState.registrationType) {
          case APIRegistrationTypes.REPAIRERS_LIEN:
            return 'Enter the amount of the Lien and the date the vehicle was (or will be) surrendered. ' +
              'Please note that this cannot be more than 21 days in the past. The length of the Lien is ' +
              'automatically set to 180 days.'

          case APIRegistrationTypes.MARRIAGE_MH:
            return (
              'The registration length for this registration is automatically set to infinite. ' +
              'There is a $10.00 fee for this registration.'
            )
          case APIRegistrationTypes.LAND_TAX_LIEN:
          case APIRegistrationTypes.MANUFACTURED_HOME_LIEN:
          case APIRegistrationTypes.INSURANCE_PREMIUM_TAX:
          case APIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX:
          case APIRegistrationTypes.FOREST:
          case APIRegistrationTypes.LOGGING_TAX:
          case APIRegistrationTypes.CARBON_TAX:
          case APIRegistrationTypes.RURAL_PROPERTY_TAX:
          case APIRegistrationTypes.PROVINCIAL_SALES_TAX:
          case APIRegistrationTypes.INCOME_TAX:
          case APIRegistrationTypes.MOTOR_FUEL_TAX:
          case APIRegistrationTypes.EXCISE_TAX:
          case APIRegistrationTypes.LIEN_UNPAID_WAGES:
          case APIRegistrationTypes.PROCEEDS_CRIME_NOTICE:
          case APIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE:
          case APIRegistrationTypes.MANUFACTURED_HOME_NOTICE:
          case APIRegistrationTypes.MAINTENANCE_LIEN:
          case APIRegistrationTypes.OTHER:
          case APIRegistrationTypes.SCHOOL_ACT:
          case APIRegistrationTypes.PROPERTY_TRANSFER_TAX:
          case APIRegistrationTypes.MINERAL_LAND_TAX:
          case APIRegistrationTypes.TOBACCO_TAX:
          case APIRegistrationTypes.SPECULATION_VACANCY_TAX:
          case APIRegistrationTypes.SECURITY_ACT_NOTICE:
            return (
              'The registration length for this registration is automatically set to infinite. ' +
              'There is no fee for this registration.'
            )
          default:
            return (
              'Enter the length of time you want the ' +
              getRegistrationType.value?.registrationTypeUI +
              ' registration to be in effect. You can renew the registration in the future (for a fee).'
            )
        }
      })
    })

    onMounted(() => {
      onAppReady(props.appReady)
      // set the registration type for the fees
      if (!fees.value[FeeSummaryTypes.NEW]) {
        setFees({[FeeSummaryTypes.NEW]: {
            ...RegistrationFees[FeeSummaryTypes.NEW],
            filingFees: localState.registrationType === APIRegistrationTypes.MARRIAGE_MH ? 10 : 0,
            serviceFees: (isRoleStaffReg.value || hasNoCharge(localState.registrationTypeUI)) ? 0 : 1.50,
            processingFees: (isRoleStaffReg.value && !hasNoCharge(localState.registrationTypeUI)) ? 10 : 0,
            filingTypeCode: localState.registrationType,
            waived: hasNoCharge(localState.registrationTypeUI)
          }})
      }
      feeOptions.value.showProcessingFees = isRoleStaffReg.value
      feeOptions.value.showServiceFees = !isRoleStaffReg.value
    })

    /** Called when App is ready and this component can load its data. */
    const onAppReady = (val: boolean): void => {
      // do not proceed if app is not ready
      if (!val) return
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!isAuthenticated.value) {
        goToDash()
        return
      }

      // redirect if store doesn't contain all needed data (happens on page reload, etc.)
      if (!getRegistrationType.value || getRegistrationFlowType.value !== RegistrationFlowType.NEW) {
        goToDash()
        return
      }

      // page is ready to view
      emitHaveData(true)
      localState.dataLoaded = true
    }

    /** Emits error to app.vue for handling */
    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
      console.error(error)
    }

    /** Emits Have Data event. */
    const emitHaveData = (haveData: boolean = true): void => {
      context.emit('haveData', haveData)
    }

    watch(() => props.appReady, (val: boolean) => {
      onAppReady(val)
    })

    watch(() => localState.registrationLength, (val: RegistrationLengthI) => {
      // if (localState.registrationType === APIRegistrationTypes.MARRIAGE_MH) return
      if (val.lifeInfinite && val.lifeYears < 1) {
        setFees({[FeeSummaryTypes.NEW]: {
            ...fees.value[FeeSummaryTypes.NEW],
            filingFees: 500,
            quantity: 1,
            feeDescOverride: 'Infinite Registration',
            waived: hasNoCharge(localState.registrationTypeUI)
          }})
      } else if (!val.lifeInfinite && val.lifeYears >= 1 && val.lifeYears <= 25) {
        setFees({[FeeSummaryTypes.NEW]: {
            ...fees.value[FeeSummaryTypes.NEW],
            filingFees: 5,
            quantity: val.lifeYears,
            feeDescOverride: `${val.lifeYears} years @ $5.00/year`,
            waived: hasNoCharge(localState.registrationTypeUI)
          }})
      } else {
        setFees({[FeeSummaryTypes.NEW]: {
            ...fees.value[FeeSummaryTypes.NEW],
            filingFees: 0,
            quantity: 1,
            filingTypeCode: localState.registrationType,
            feeDescOverride: 'Select a valid registration length',
            waived: hasNoCharge(localState.registrationTypeUI)
          }})
      }
    })

    watch(() => !!getSecuritiesActNotices.value.length, (val: boolean) => {
      if (isSecurityActNotice.value) setLengthTrustStepValidity(val)
    }, { immediate: true  })

    return {
      emitError,
      getPprSteps,
      showStepErrors,
      isSecurityActNotice,
      getFooterButtonConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme';

.step-container {
  margin-top: 1rem;
  padding: 1.25rem;
}

.meta-container {
  display: flex;
  flex-flow: column nowrap;
  position: relative;

  > label:first-child {
    font-weight: 700;
  }
}

@media (min-width: 768px) {
  .meta-container {
    flex-flow: row nowrap;

    > label:first-child {
      flex: 0 0 auto;
      padding-right: 2rem;
      width: 12rem;
    }
  }
}

.reg-default-btn {
  background-color: $gray3 !important;
}

.reg-default-btn::before {
  background-color: transparent !important;
}
</style>
