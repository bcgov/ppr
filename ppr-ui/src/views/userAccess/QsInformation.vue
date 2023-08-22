<template>
  <div id="qs-information">
    <section class="qs-information-intro mt-10">
      <p>
        To request <strong>Qualified Supplier - {{ getMhrSubProduct }}</strong> access to the Manufactured Home
        Registry, complete the information below. BC Registries staff will review your application and if approved,
        will provide access.
      </p>

      <CautionBox
        class="mt-8"
        :setMsg="`This is intended for the exclusive use of B.C. ${getMhrSubProduct && getMhrSubProduct.toLowerCase()}
        only.`"
      />
    </section>

    <div class="increment-sections">
      <section class="qs-service-agreement mt-8">
        <h2>Service Agreement</h2>
        <p class="mt-1">
          Read and accept the terms of the service agreement. You may download and a copy of this agreement to save for
          your records.
        </p>

        <!-- download service agreement button -->
        <v-btn outlined color="primary" class="mt-2" :ripple="false" @click="downloadServiceAgreement">
          <img alt="" src="@/assets/svgs/pdf-icon-blue.svg" />
          <span class="pl-1">Download Qualified Suppliers' Agreement</span>
        </v-btn>

        <!-- service agreement preview container -->
        <v-card flat class="mt-10 scroll-container">
          <!-- TODO: Design Currently reviewing pdf preview options - Placeholder & Example implementation below -->
          <label>Document Preview/html Placeholder</label>
<!--          <vue-pdf-embed v-if="serviceAgreementUrl" :source="serviceAgreementUrl" />-->
<!--          <v-progress-circular v-else class="loading-spinner" color="primary" size="50" indeterminate ce/>-->
        </v-card>

        <!-- service agreement confirmation -->
        <v-card flat class="mt-5 pa-8" :class="{'border-error-left': showQsSaConfirmError}">
          <v-checkbox
              class="align-start ma-0 pa-0"
              color="primary"
              hide-details
              v-model="serviceAgreementConfirm"
          >
            <template v-slot:label>
              <span :class="{ 'error-text': showQsSaConfirmError }">
                I have read, understood and agree to the terms and conditions of the Qualified Suppliers’ Agreement
               for the Manufactured Home Registry.
              </span>
            </template>
          </v-checkbox>
        </v-card>
      </section>

      <section class="qs-information-form mt-8">
        <h2>Qualified Supplier ({{ getMhrSubProduct }}) Information</h2>
        <p class="mt-1">
          Provide the name and contact information for the Qualified Supplier.
        </p>

        <FormCard
          label="Qualified Supplier"
          :showErrors="showQsInfoErrors"
          :class="{'border-error-left': showQsInfoErrors}"
        >
          <template v-slot:formSlot>
            <PartyForm
              ref="qsInformationRef"
              :baseParty="getMhrQsInformation"
              :schema="PartyFormSchema"
              :orgLookupConfig="orgLookupConfig"
              @isValid="updateQsInfoValid"
            >
              <template v-slot:businessNameSlot>
                <label class="generic-label" for="business-name">Qualified Supplier's Legal Business Name</label>
                <p class="mt-2">
                  You can find the full legal name of an active B.C. business by entering the name or incorporation
                  number of the business, or you can type the full legal name of the Qualified Supplier if it is not a
                  registered B.C. business.
                </p>
              </template>
            </PartyForm>
          </template>
        </FormCard>
      </section>
    </div>

  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from 'vue-demi'
import { CautionBox, FormCard, PartyForm } from '@/components/common'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { PartyFormSchema } from '@/schemas'
import { UserAccessOrgLookupConfig } from '@/resources'
import { OrgLookupConfigIF } from '@/interfaces'
import { useUserAccess } from '@/composables'
import { getQsServiceAgreements } from '@/utils'

export default defineComponent({
  name: 'QsInformation',
  components: { CautionBox, FormCard, PartyForm },
  props: { validate: { type: Boolean, default: false } },
  setup (props) {
    const qsInformationRef = ref(null) as any
    const { setMhrQsValidation } = useStore()
    const { getMhrQsInformation, getMhrSubProduct } = storeToRefs(useStore())
    const { downloadServiceAgreement } = useUserAccess()

    const localState = reactive({
      showQsInfoErrors: false,
      showQsSaConfirmError: false,
      serviceAgreementUrl: null,
      serviceAgreementConfirm: false,
      orgLookupConfig: computed((): OrgLookupConfigIF => UserAccessOrgLookupConfig[getMhrSubProduct.value])
    })

    const updateQsInfoValid = (isValid: boolean): void => {
      localState.showQsInfoErrors = !isValid
      setMhrQsValidation({ key: 'qsInformationValid', value: isValid })
    }

    onMounted(async () => {
      // Get the service agreement pdf url for preview
      const serviceAgreementBlob = await getQsServiceAgreements()
      localState.serviceAgreementUrl = URL.createObjectURL(serviceAgreementBlob)
    })

    watch(() => localState.serviceAgreementConfirm, (val: boolean) => {
      localState.showQsSaConfirmError = !val && props.validate
      setMhrQsValidation({ key: 'qsSaConfirmValid', value: val })
    })

    watch(() => props.validate, (val: boolean) => {
      localState.showQsInfoErrors = val
      localState.showQsSaConfirmError = val
      qsInformationRef.value?.validatePartyForm()
    })

    return {
      qsInformationRef,
      PartyFormSchema,
      updateQsInfoValid,
      getMhrQsInformation,
      getMhrSubProduct,
      downloadServiceAgreement,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.loading-spinner {
  position: unset;
}
.scroll-container {
  max-height: 600px;
  overflow-y: auto;

  .content {
    padding: 16px;
  }

  .item {
    padding: 8px;
    border-bottom: 1px solid #ccc;
  }
}
::v-deep {
  .v-input--hide-details > .v-input__control > .v-input__slot {
    display: flex;
    align-items: flex-start;
    .v-label {
      padding-left: 5px;
    }
  }
}
</style>
