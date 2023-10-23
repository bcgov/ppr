<template>
  <section id="qs-select-access" class="mt-9">
    <h2>Qualified Supplier Access Type</h2>
    <p class="mt-4">
      If you are an
      <v-tooltip
        location="top" content-class="top-tooltip"
        transition="fade-transition"
      >
        <template v-slot:activator="{ on }">
          <span v-on="on" class="dotted-underline" tabindex="0">active B.C. lawyer or notary</span>
        </template>
        <div class="pt-2 pb-2">
          A practising member in good standing of the Law Society of British Columbia, or a practising member in good
          standing of the Society of Notaries Public of British Columbia.
        </div>
      </v-tooltip>
      , a home manufacturer or a home dealer, and would like to have access
      to perform additional transactions in the Manufactured Home Registry, you must apply to be a Qualified Supplier.
      Indicate the type of Qualified Supplier access you would like to request.
    </p>

    <FormCard label="Select Access Type" :showErrors="showErrors" :class="{'border-error-left': showErrors}">
      <template v-slot:formSlot>
        <SubProductSelector
          :subProductConfig="MhrSubProductConfig"
          :defaultProduct="getMhrSubProduct"
          @updateSubProduct="setMhrSubProduct"
        />
      </template>
    </FormCard>
  </section>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import { FormCard, SubProductSelector } from '@/components/common'
import { MhrSubProductConfig } from '@/resources'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'QsSelectAccess',
  components: {
    FormCard,
    SubProductSelector
  },
  props: {
    showErrors: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const { setMhrSubProduct } = useStore()
    const { getMhrSubProduct } = storeToRefs(useStore())
    const localState = reactive({})

    return {
      setMhrSubProduct,
      getMhrSubProduct,
      MhrSubProductConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
