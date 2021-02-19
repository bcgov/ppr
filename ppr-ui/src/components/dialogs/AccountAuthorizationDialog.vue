<template>
  <v-dialog v-model="dialog" width="45rem" persistent :attach="attach" content-class="account-authorization-dialog">
    <v-card>
      <v-card-title id="dialog-title">Account Authorization</v-card-title>

      <v-card-text>
        <p class="genErr">There was an issue logging in to your account. Please try again later.</p>

        <template>
          <p class="genErr">If this error persists, please contact us:</p>
          <error-contact />
        </template>
      </v-card-text>

      <v-divider class="my-0"></v-divider>

      <v-card-actions>
        <v-btn id="dialog-retry-button" text @click="retry()">Retry</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Vue, Prop, Emit } from 'vue-property-decorator'
import { ErrorContact } from '@/components/common'

@Component({
  components: { ErrorContact }
})
export default class AccountAuthorizationDialog extends Vue {
  // Prop to display the dialog.
  @Prop() private dialog: boolean

  // Prop to provide attachment selector.
  @Prop() private attach: string

  // Pass click events to parent.
  @Emit() private retry () { }
}
</script>

<style lang="scss" scoped>
</style>
