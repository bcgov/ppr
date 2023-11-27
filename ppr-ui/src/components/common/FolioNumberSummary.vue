<template>
  <v-container
    id="folio-summary"
    class="pa-0 flat"
  >
    <v-form
      ref="form"
      v-model="isValid"
    >
      <v-row noGutters>
        <v-col class="generic-label">
          <h2>1. Folio or Reference Number</h2>
        </v-col>
      </v-row>
      <v-row
        noGutters
        class="pt-4"
      >
        <v-col>
          <p>
            Add an optional number for this transaction for your own tracking purposes.
            This information is not used by the {{ getTypeLabel }}.
          </p>
        </v-col>
      </v-row>

      <v-card
        flat
        class="mt-6 px-6"
        :class="showErrors && !isValid ? 'border-error-left': ''"
      >
        <v-row
          noGutters
        >
          <v-col
            cols="3"
            class="generic-label pt-10"
          >
            Folio Number
          </v-col>
          <v-col
            cols="9"
            class="pt-8"
          >
            <v-text-field
              id="txt-folio"
              v-model="folioNumber"
              class="text-folio"
              variant="filled"
              label="Folio or Reference Number (Optional)"
              persistentHint
              :rules="rules"
            />
          </v-col>
        </v-row>
      </v-card>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  ref,
  computed
} from 'vue'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { FormIF } from '@/interfaces'

export default defineComponent({
  props: {
    setShowErrors: {
      type: Boolean,
      default: false
    },
    setIsMhr: {
      type: Boolean,
      default: false
    }
  },
  emits: ['folioValid'],
  setup (props, context) {
    const { setFolioOrReferenceNumber } = useStore()
    const { getFolioOrReferenceNumber } = storeToRefs(useStore())
    const form = ref(null) as FormIF

    const localState = reactive({
      isValid: true,
      folioNumber: getFolioOrReferenceNumber.value || '',
      showErrors: props.setShowErrors,
      rules: [
        (v: string) => !v || v.length <= 50 || 'Maximum 50 characters reached' // maximum character count
      ],
      getTypeLabel: computed((): string => {
        return props.setIsMhr ? 'Manufactured Home Registry' : 'Personal Property Registry'
      })
    })

    watch(() => props.setShowErrors, (val) => {
      localState.showErrors = val
    })

    watch(
      () => localState.folioNumber,
      (val: string) => {
        setFolioAndEmit(val)
      }
    )

    const setFolioAndEmit = (val: string) => {
      form.value.validate()
      context.emit('folioValid', localState.isValid)
      setFolioOrReferenceNumber(val)
    }

    return {
      form,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
