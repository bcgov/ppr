<template>
  <v-dialog v-model="display" width="40rem" persistent :attach="attach">
    <v-card>
      <v-row no-gutters class="px-7 pt-7">
        <v-col cols="11">
          <v-row no-gutters>
            <v-col align-self="start">
              <span class="dialog-title">
                <b>{{ options.title }}</b>
              </span>
            </v-col>
          </v-row>
          <v-row no-gutters class="pt-5">
            <span class="dialog-text" v-html="options.text">
              {{ options.text }}
            </span>
          </v-row>
          <v-row no-gutters class="pt-5">
            <v-checkbox class="dialog-checkbox pa-0 ma-0"
                        :error-messages="updateFailed ? 'error' : ''"
                        :hide-details="false"
                        label=""
                        v-model="preventDialog">
              <template v-slot:label>
                <span class="dialog-text">Don't show this message again</span>
              </template>
              <template v-slot:message>
                <v-row no-gutters class="pl-8">
                  We were unable to update your user settings. Please try again later.
                </v-row>
              </template>
            </v-checkbox>
          </v-row>
        </v-col>
        <v-col cols="1">
          <v-row no-gutters justify="end">
            <v-btn color="primary" icon :ripple="false" @click="proceed(false)">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters justify="center" class="pt-5 pb-7">
        <v-col v-if="options.acceptText" cols="auto">
          <v-btn id="accept-btn" class="primary dialog-btn" @click="proceed(true)">{{ options.acceptText }}</v-btn>
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
import { SettingOptions } from '@/enums' // eslint-disable-line
import { ActionBindingIF, DialogOptionsIF, UserSettingsIF } from '@/interfaces' // eslint-disable-line
import { updateUserSettings } from '@/utils'

@Component({})
export default class ConfirmationDialog extends Vue {
  @Action setUserSettings: ActionBindingIF

  @Prop() private attach: string
  @Prop() private display: boolean
  @Prop() private options: DialogOptionsIF
  @Prop() private settingOption: SettingOptions

  private preventDialog: boolean = false
  private updateFailed: boolean = false

  @Watch('preventDialog')
  private async patchUserSettings (val: boolean): Promise<void> {
    const settings: UserSettingsIF = await updateUserSettings(this.settingOption, !val)
    if (!settings?.error) {
      this.updateFailed = false
      this.setUserSettings(settings)
    } else {
      // show error message
      this.updateFailed = true
    }
  }

  @Emit() private proceed (val: boolean) { }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
