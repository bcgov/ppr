<template>
  <section :id="sectionId" class="mt-13">
    <h2 :data-test-id="`${sectionId}-title`">
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${folioOrRefConfig.title}`}}
    </h2>
    <p class="mt-2" :data-test-id="`${sectionId}-description`">
      {{ folioOrRefConfig.description }}
    </p>

    <v-form ref="folioOrRefForm" v-model="isFormValid" :data-test-id="`${sectionId}-form`">
      <v-card
        flat
        rounded
        class="mt-6 pt-10 px-7 pb-5"
        :class="{ 'border-error-left': setShowErrors }"
        :data-test-id="`${sectionId}-card`"
      >
        <FormField
          :sectionId="sectionId"
          :initialValue="getFolioOrReferenceNumber"
          :inputTitle="folioOrRefConfig.inputTitle"
          :inputLabel="folioOrRefConfig.inputLabel"
          :rules="maxLength(30)"
          :setValue="setFolioOrReferenceNumber"
          :showErrors="setShowErrors"
        />
      </v-card>
    </v-form>
  </section>
</template>

<script lang="ts">
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { defineComponent, toRefs, ref, computed, reactive, watch } from 'vue-demi'
import { useInputRules } from '@/composables'
import { FormField } from '@/components/common'
import { folioOrRefConfig } from '@/resources/attnRefConfigs'

export default defineComponent({
  name: 'FolioOrReferenceNumber',
  components: { FormField },
  emits: ['isFolioOrRefNumValid'],
  props: {
    sectionId: {
      type: String,
      required: true
    },
    sectionNumber: {
      type: Number,
      required: false
    },
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { setFolioOrReferenceNumber } = useStore()
    const { getFolioOrReferenceNumber } = storeToRefs(useStore())
    const { maxLength } = useInputRules()

    const folioOrRefForm = ref(null)

    const localState = reactive({
      isFormValid: false,
      setShowErrors: computed(() => props.validate && !localState.isFormValid)
    })

    watch(() => localState.isFormValid, (val: boolean) => {
      emit('isFolioOrRefNumValid', val)
    })

    watch(() => props.validate, (validate: boolean) => {
      validate && folioOrRefForm.value?.validate()
    })

    return {
      folioOrRefConfig,
      folioOrRefForm,
      getFolioOrReferenceNumber,
      maxLength,
      setFolioOrReferenceNumber,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
