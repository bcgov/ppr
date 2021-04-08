<template>
  <v-dialog v-model="display" width="40rem" persistent :attach="attach">
    <v-card>
      <v-card-title id="dialog-title">{{ options.title }}</v-card-title>
      <v-row no-gutters class="px-7 pt-7">
        <span class="dialog-text" v-html="options.text">
          {{ options.text }}
        </span>
      </v-row>
      <v-row no-gutters class="px-7 pt-7">
        <template>
          <span class="dialog-text">If this error persists, please contact us:</span>
          <error-contact />
        </template>
      </v-row>
      <v-row no-gutters justify="center" class="py-7">
        <v-col v-if="options.acceptText" cols="auto">
          <v-btn id="accept-btn" class="primary dialog-btn" @click="proceed(true)">{{ options.acceptText }}</v-btn>
        </v-col>
        <v-col v-if="options.cancelText" cols="auto" :class="options.acceptText? 'pl-3' : ''">
          <v-btn id="cancel-btn"
                 :class="options.acceptText? 'outlined dialog-btn' : 'primary dialog-btn'"
                 @click="proceed(false)">
            {{ options.cancelText }}
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
// external
import { Component, Vue, Prop, Emit } from 'vue-property-decorator'

// local
import { ErrorContact } from '@/components/common'
import { DialogOptionsIF } from '@/interfaces' // eslint-disable-line

@Component({
  components: { ErrorContact }
})
export default class ErrorDialog extends Vue {
  @Prop() private attach: string
  @Prop() private display: boolean
  @Prop() private options: DialogOptionsIF

  @Emit() private proceed (val: boolean) { }
}
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
