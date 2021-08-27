<template>
  <v-dialog v-model="display" width="40rem" persistent :attach="attach">
    <v-card>
      <v-row no-gutters class="px-7 pt-7">
        <v-col cols="11">
          <p class="dialog-title ma-0">
            <b>{{ options.title }}</b>
          </p>
          <p class="dialog-text pt-5 ma-0">
            To ensure you are performing a Total Discharge on the correct
            registration (Base Registration Number: ) please enter the
            <b>individual person's last name or full business name</b> of any
            <b>Debtor</b> associated with this registration.
          </p>
          <v-text-field
            id="dialog-text-field"
            class="rounded-top pt-5"
            :error-messages="validationErrors"
            filled
            :label="options.label"
            v-model="userInput"
          />

          <v-autocomplete
            auto-select-first
            :items="debtors"
            filled
            clearable
            label="Enter a Debtor (last name of individual person of full business name)"
            id="debtor-drop"
            v-model="userInput"
            :error-messages="validationErrors"
            persistent-hint
            return-object
          ></v-autocomplete>
        </v-col>
        <v-col cols="1">
          <v-row no-gutters justify="end">
            <v-btn
              id="close-btn"
              color="primary"
              icon
              :ripple="false"
              @click="proceed(false)"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters justify="center" class="pt-5 pb-7">
        <v-col v-if="options.cancelText" cols="auto" class="pl-3">
          <v-btn
            id="cancel-btn"
            class="outlined dialog-btn"
            outlined
            @click="proceed(false)"
          >
            {{ options.cancelText }}
          </v-btn>
        </v-col>
        <v-col v-if="options.acceptText" cols="auto">
          <v-btn id="accept-btn" class="primary dialog-btn" @click="submit()">{{
            options.acceptText
          }}</v-btn>
          <v-icon>mdi-chevron-right</v-icon>
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
// external
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  onMounted
} from '@vue/composition-api'

// local
import { DebtorNameIF, DialogOptionsIF } from '@/interfaces' // eslint-disable-line
import { debtorNames } from '@/utils'

export default defineComponent({
  props: {
    attach: String,
    display: Boolean,
    options: {
      type: Object as () => DialogOptionsIF
    },
    registrationNumber: String
  },
  emits: ['proceed'],
  setup (props, context) {
    const localState = reactive({
      validationErrors: '',
      userInput: '',
      debtors: [],
      options: props.options,
      attach: props.attach,
      display: props.display
    })

    const submit = (): void => {
      if (localState.userInput) {
        context.emit('proceed')
      } else {
        localState.validationErrors = 'This field is required'
      }
    }

    onMounted(async () => {
      const names: Array<DebtorNameIF> = await debtorNames(
        props.registrationNumber
      )
      for (let i = 0; i < names.length; i++) {
        localState.debtors.push({ text: names[i].businessName, value: names[i].businessName })
      }
    })

    watch(
      () => localState.userInput,
      (val: string) => {
        if (!val) localState.validationErrors = 'This field is required'
      }
    )
    return {
      submit,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
