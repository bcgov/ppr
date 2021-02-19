<template>
  <v-dialog v-model="dialog" width="45rem" persistent :attach="attach" content-class="save-error-dialog">
    <v-card>
      <!-- if there are errors, or neither errors nor warnings... -->
      <v-card-title id="dialog-title" v-if="numErrors > 0 || numWarnings < 1">
        Unable to save this search
      </v-card-title>

      <!-- otherwise there are only warnings... -->
      <v-card-title id="dialog-title" v-else>
        Search saved with warnings
      </v-card-title>

      <v-card-text id="dialog-text">
        <!-- display generic message (no errors or warnings) -->
        <div class="genErr" v-if="(numErrors + numWarnings) < 1">
          <p>We were unable to save this search. You can continue to try to save this
            search or you can exit and retry at another time.</p>
        </div>

        <!-- display errors -->
        <div class="genErr mb-4" v-if="numErrors > 0">
          <p>We were unable to save your search due to the following errors:</p>
          <ul>
            <li v-for="(error, index) in errors" :key="index">{{ error.error }}</li>
          </ul>
        </div>

        <!-- display warnings-->
        <div class="genErr mb-4" v-if="numWarnings > 0">
          <p>Please note the following warnings:</p>
          <ul>
            <li v-for="(warning, index) in warnings" :key="index">{{ warning.warning }}</li>
          </ul>
        </div>

        <template v-if="!isRoleStaff">
          <p class="genErr">If this error persists, please contact us:</p>
          <error-contact />
        </template>
      </v-card-text>

      <v-divider class="my-0"></v-divider>

      <!-- if there are errors, or neither errors nor warnings... -->
      <v-card-actions v-if="numErrors > 0 || numWarnings < 1">
        <v-spacer></v-spacer>
        <v-btn id="dialog-okay-button" text @click="okay()">OK</v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>

      <!-- otherwise there are only warnings... -->
      <v-card-actions v-else>
        <v-spacer></v-spacer>
        <v-btn id="dialog-okay-button" text @click="okay()">OK</v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Vue, Prop, Emit } from 'vue-property-decorator'
import { Getter } from 'vuex-class'
import { ErrorContact } from '@/components/common'

@Component({
  components: { ErrorContact }
})
export default class SaveErrorDialog extends Vue {
  @Getter isRoleStaff!: boolean

  /** Prop to display the dialog. */
  @Prop() private dialog: boolean

  /** Prop to provide attachment selector. */
  @Prop() private attach: string

  /** Prop containing error messages. */
  @Prop({ default: () => [] }) private errors: object[]

  /** Prop containing warning messages. */
  @Prop({ default: () => [] }) private warnings: object[]

  // Pass click events to parent.
  @Emit() private exit () { }
  @Emit() private okay () { }

  /** The number of errors in the passed-in array. */
  private get numErrors (): number {
    return this.errors?.length || 0
  }

  /** The number of warnings in the passed-in array. */
  private get numWarnings (): number {
    return this.warnings?.length || 0
  }
}
</script>
