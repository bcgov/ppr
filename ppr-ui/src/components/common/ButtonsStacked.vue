<template>
  <div>
    <div>
      <v-btn
        id="btn-stacked-cancel"
        class="btn-stacked"
        outlined
        @click="cancel()"
      >
        {{ cancelBtn }}
      </v-btn>
    </div>
    <div class="pt-4">
      <v-btn id="btn-stacked-submit" class="btn-stacked" color="primary">
        {{ submitBtn }}
        <v-icon color="white" style="padding-top: 2px;">mdi-chevron-right</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script lang="ts">
// external
import { RouteNames } from '@/enums'
import {
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'

export default defineComponent({
  name: 'ButtonsStacked',
  props: {
    setCancelBtn: {
      default: 'Cancel'
    },
    setSubmitBtn: {
      default: 'Confirm and Complete'
    }
  },
  setup (props, { emit, root }) {
    const localState = reactive({
      cancelBtn: props.setCancelBtn,
      submitBtn: props.setSubmitBtn
    })
    const cancel = () => {
      root.$router.push({
        name: RouteNames.DASHBOARD
      })
    }
    const submit = () => {
      emit('submit', true)
    }

    return {
      cancel,
      submit,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.btn-stacked {
  color: $primary-blue;
  width: 100%;
}
</style>
