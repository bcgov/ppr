<template>
  <v-dialog v-model="display" width="40rem" persistent :attach="attach">
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
        <v-col v-if="options.acceptText" cols="auto">
          <v-btn id="accept-btn" class="primary dialog-btn" @click="submit()">{{ options.acceptText }}</v-btn>
        </v-col>
        <v-col v-if="options.cancelText" cols="auto" class="pl-3">
          <v-btn id="cancel-btn" class="outlined dialog-btn" outlined @click="proceed(false)">
            {{ options.cancelText }}
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
// external
import { Component, Vue, Prop, Emit, Watch } from 'vue-property-decorator'
import { Action } from 'vuex-class'

// local
import { ActionBindingIF, DialogOptionsIF } from '@/interfaces' // eslint-disable-line

@Component({})
export default class RegistrationOtherDialog extends Vue {
  @Action setRegistrationTypeOtherDesc: ActionBindingIF

  @Prop() private attach: string
  @Prop() private display: boolean
  @Prop() private options: DialogOptionsIF

  private validationErrors = ''
  private userInput = ''

  private submit (): void {
    if (this.userInput) {
      this.setRegistrationTypeOtherDesc(this.userInput)
      this.proceed(true)
    } else {
      this.validationErrors = 'This field is required'
    }
  }

  @Watch('userInput')
  private validateInput (val: string): void {
    if (!val) this.validationErrors = 'This field is required'
  }

  @Emit() private proceed (val: boolean) { }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
