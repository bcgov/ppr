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

    <section class="qs-service-agreement mt-8">
      <h2>Service Agreement</h2>
      <p class="mt-1">
        Read and accept the terms of the service agreement. You may download and a copy of this agreement to save for
        your records.
      </p>
      <v-btn outlined color="primary" class="mt-2" :ripple="false">
        <img alt="" src="@/assets/svgs/pdf-icon-blue.svg" />
        <span class="pl-1">Download Qualified Suppliers Agreement</span>
      </v-btn>
    </section>

    <section class="qs-information-form mt-8">
      <h2>Qualified Supplier ({{ getMhrSubProduct }}) Information</h2>
      <p class="mt-1">
        Provide the name and contact information for the Qualified Supplier.
      </p>

      <FormCard label="Qualified Supplier" :showErrors="showErrors" :class="{'border-error-left': showErrors}">
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
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from 'vue-demi'
import { CautionBox, FormCard, PartyForm } from '@/components/common'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'
import { PartyFormSchema } from '@/schemas'
import { UserAccessOrgLookupConfig } from '@/resources'
import { OrgLookupConfigIF } from '@/interfaces'

export default defineComponent({
  name: 'QsInformation',
  components: { CautionBox, FormCard, PartyForm },
  props: { validate: { type: Boolean, default: false } },
  setup (props) {
    const qsInformationRef = ref(null) as any
    const { setMhrQsValidation } = useStore()
    const { getMhrQsInformation, getMhrSubProduct } = storeToRefs(useStore())

    const localState = reactive({
      showErrors: false,
      orgLookupConfig: computed((): OrgLookupConfigIF => UserAccessOrgLookupConfig[getMhrSubProduct.value])
    })

    const updateQsInfoValid = (isValid: boolean): void => {
      localState.showErrors = !isValid
      setMhrQsValidation({ key: 'qsInformationValid', value: isValid })
    }

    watch(() => props.validate, (val: boolean) => {
      localState.showErrors = val
      qsInformationRef.value?.validatePartyForm()
    })

    return {
      qsInformationRef,
      PartyFormSchema,
      updateQsInfoValid,
      getMhrQsInformation,
      getMhrSubProduct,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
section:first-child,
section:not(:first-child) h2 + section {
  counter-reset: section 0;
}
section h2:before {
  counter-increment: section;
  content: counters(section, ".") ". ";
}
</style>
