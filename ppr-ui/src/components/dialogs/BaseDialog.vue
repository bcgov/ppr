<template>
  <v-dialog v-model="display" width="45rem" persistent :attach="attach">
    <v-card>
      <v-row no-gutters class="px-7 pt-7">
        <v-col cols="11">
          <div class="dialog-title">
            <b>{{ options.title }}</b>
          </div>
          <div class="dialog-text pt-5" v-html="options.text" />
        </v-col>
        <v-col cols="1">
          <v-btn class="float-right" color="primary" icon :ripple="false" @click="proceed(false)">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <v-row no-gutters justify="center" class="py-7">
        <v-col v-if="options.acceptText" cols="auto">
          <v-btn id="cancel-btn" class="outlined dialog-btn" outlined @click="proceed(false)">
            {{ options.cancelText }}
          </v-btn>
        </v-col>
        <v-col v-if="options.cancelText" cols="auto" class="pl-3">
          <v-btn id="accept-btn" class="primary dialog-btn" @click="proceed(true)">
            {{ options.acceptText }}
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
import { DialogOptionsIF } from '@/interfaces' // eslint-disable-line

@Component({})
export default class ConfirmationDialog extends Vue {
  @Prop() private attach: string
  @Prop() private display: boolean
  @Prop() private options: DialogOptionsIF

  @Emit() private proceed (val: boolean) { }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#accept-btn {
  font-weight: normal;
}
</style>
