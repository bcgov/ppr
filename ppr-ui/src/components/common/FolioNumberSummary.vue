<template>
  <v-container class="pa-0 flat" id="folio-summary">
    <v-form ref="form" v-model="isValid">
      <v-row no-gutters>
        <v-col class="generic-label"
          ><h2>1. Folio or Reference Number</h2></v-col
        >
      </v-row>
      <v-row no-gutters class="pb-6 pt-4">
        <v-col>
          Add an optional number for this transaction for your own tracking purposes.
          This information is not used by the {{ getTypeLabel }}.
        </v-col>
      </v-row>

      <v-row class="no-gutters">
        <v-col cols="12" class="pa-0" :class="showErrors && !isValid ? 'border-error-left': ''">
          <v-card flat>
            <v-row no-gutters style="padding: 0 30px;">
              <v-col cols="3" class="generic-label pt-10"
                >Folio Number</v-col
              >
              <v-col cols="9" class="pt-8">
                <v-text-field
                  filled
                  id="txt-folio"
                  label="Folio or Reference Number (Optional)"
                  v-model="folioNumber"
                  persistent-hint
                  :rules="rules"
                />
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>
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
  onMounted,
  computed
} from 'vue-demi'
import { useStore } from '@/store/store'

export default defineComponent({
  props: {
    setShowErrors: {
      default: false
    },
    setIsMhr: {
      default: false
    }
  },
  setup (props, context) {
    const { getFolioOrReferenceNumber, setFolioOrReferenceNumber } = useStore()
    const form = ref(null)

    const localState = reactive({
      isValid: true,
      folioNumber: '',
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

    const setFolioAndEmit = async (val: string) => {
      // @ts-ignore - function exists
      await context.refs.form.validate()
      context.emit('folioValid', localState.isValid)
      setFolioOrReferenceNumber(val)
    }

    onMounted(() => {
      localState.folioNumber = getFolioOrReferenceNumber
    })

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
