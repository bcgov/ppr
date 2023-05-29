<template>
  <v-dialog v-model="displayDialog" width="45rem" persistent :attach="attach">
    <v-card>
      <v-row no-gutters class="pl-10 pt-7">
        <v-col cols="11">
          <v-row no-gutters>
            <v-col align-self="start">
              <span class="dialog-title">
                <b>Change Secured Party?</b>
              </span>
            </v-col>
          </v-row>
          <v-row no-gutters class="pt-5">
            <span class="dialog-text">
              The Secured Party role is already assigned to
              {{ securedPartyName }}. Selecting "Change Secured Party" here will
              update the secured party.
            </span>
          </v-row>
        </v-col>
        <v-col cols="1">
          <v-row no-gutters>
            <v-btn color="primary" icon :ripple="false" @click="proceed(false)">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters justify="center" class="pt-5 pb-10">
        <v-col cols="auto" class="pr-3">
          <v-btn
            id="cancel-btn"
            class="outlined dialog-btn"
            outlined
            @click="proceed(false)"
          >
            Cancel
          </v-btn>
        </v-col>
        <v-col cols="auto">
          <v-btn
            id="accept-btn"
            class="primary dialog-btn"
            @click="proceed(true)"
            >Change Secured Party</v-btn
          >
        </v-col>
      </v-row>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'

export default defineComponent({
  name: 'ChangeSecuredPartyDialog',
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
    securedPartyName: {
      type: String,
      default: ''
    }
  },
  setup (props, context) {
    const localState = reactive({
      displayDialog: computed(() => {
        return props.display
      })
    })

    const proceed = (val: boolean) => {
      context.emit('proceed', val)
    }

    return {
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
