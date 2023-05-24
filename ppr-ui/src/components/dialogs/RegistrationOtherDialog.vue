<template>
  <v-dialog v-model="displayDialog" width="45rem" persistent :attach="attach">
    <v-card>
      <v-row no-gutters class="px-7 pt-7">
        <v-col cols="11">
          <p class="dialog-title ma-0"><b>{{ options.title }}</b></p>
          <p class="dialog-text pt-5 ma-0" v-html="options.text" />
          <v-text-field
            id="dialog-text-field"
            class="rounded-top pt-5"
            :error-messages="validationErrors"
            filled
            :label="options.label"
            v-model="userInput"
          />
        </v-col>
        <v-col cols="1">
          <v-row no-gutters justify="end">
            <v-btn id="close-btn" color="primary" icon :ripple="false" @click="proceed(false)">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters justify="center" class="pt-5 pb-7">
        <v-col v-if="options.cancelText" cols="auto" class="pr-3">
          <v-btn id="cancel-btn" class="outlined dialog-btn" outlined @click="proceed(false)">
            {{ options.cancelText }}
          </v-btn>
        </v-col>
        <v-col v-if="options.acceptText" cols="auto">
          <v-btn id="accept-btn" class="primary dialog-btn" @click="submit()">{{ options.acceptText }}
            <v-icon color="white">mdi-chevron-right</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue-demi'
import { useStore } from '@/store/store'
// eslint-disable-next-line no-unused-vars
import { DialogOptionsIF } from '@/interfaces'

export default defineComponent({
  name: 'RegistrationOtherDialog',
  emits: ['proceed'],
  props: {
    attach: {
      type: String,
      default: ''
    },
    display: {
      type: Boolean,
      default: false
    },
    options: {
      type: Object as () => DialogOptionsIF,
      default: null
    }
  },
  setup (props, context) {
    const { setRegistrationTypeOtherDesc } = useStore()
    const localState = reactive({
      displayDialog: computed(() => {
        return props.display
      }),
      validationErrors: '',
      userInput: ''
    })

    const submit = (): void => {
      if (localState.userInput) {
        setRegistrationTypeOtherDesc(localState.userInput)
        proceed(true)
      } else {
        localState.validationErrors = 'This field is required'
      }
    }
    const proceed = (val: boolean) => {
      context.emit('proceed', val)
    }

    watch(() => localState.userInput, (val: string) => {
      if (!val) localState.validationErrors = 'This field is required'
    })

    return {
      submit,
      proceed,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.v-btn.primary {
  font-weight: normal;
}
</style>
