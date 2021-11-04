<template>
  <base-dialog :setDisplay="display" :setOptions="options" @proceed="proceed($event)">
    <template v-slot:content>
      <dialog-content :setBaseText="options.text" />
      <v-checkbox
        class="dialog-checkbox pt-5 ma-0"
        :error-messages="updateFailed ? 'error' : ''"
        :hide-details="!updateFailed"
        label="Don't show this message again"
        v-model="preventDialog"
      >
        <template v-slot:message>
          <p class="ma-0 pl-8">
            We were unable to update your user settings. Please try again later.
          </p>
        </template>
      </v-checkbox>
    </template>
  </base-dialog>
</template>

<script lang="ts">
// external
import {
  computed,
  defineComponent,
  reactive,
  toRefs,
  watch
} from '@vue/composition-api'
import { useActions } from 'vuex-composition-helpers'
// local components
import { BaseDialog } from '.'
import { DialogContent } from './common'
// local types/helpers/etc.
import { SettingOptions } from '@/enums' // eslint-disable-line
import { DialogOptionsIF, UserSettingsIF } from '@/interfaces' // eslint-disable-line
import { updateUserSettings } from '@/utils'

export default defineComponent({
  name: 'ConfirmationDialog',
  components: {
    BaseDialog,
    DialogContent
  },
  props: {
    setDisplay: { default: false },
    setOptions: Object as () => DialogOptionsIF,
    setSettingOption: { default: null }
  },
  emits: ['proceed'],
  setup (props, { emit }) {
    const { setUserSettings } = useActions<any>(['setUserSettings'])

    const localState = reactive({
      preventDialog: false,
      updateFailed: false,
      display: computed(() => {
        return props.setDisplay
      }),
      options: computed(() => {
        return props.setOptions
      }),
      settingOption: computed(() => {
        return props.setSettingOption as SettingOptions
      })
    })

    const proceed = (val: boolean) => {
      emit('proceed', val)
    }

    watch(() => localState.preventDialog, async (val) => {
      const settings: UserSettingsIF = await updateUserSettings(localState.settingOption, !val)
      if (!settings?.error) {
        localState.updateFailed = false
        setUserSettings(settings)
      } else {
        // show error message
        localState.updateFailed = true
      }
    })

    return {
      proceed,
      ...toRefs(localState)
    }
  }
})
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
::v-deep .dialog-checkbox .v-input__control .v-input__slot .v-label {
  color: $gray7;
  font-size: 1rem;
  line-height: 1.5rem;
}
</style>
