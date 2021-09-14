<template>
  <div>
    <v-row no-gutters>
      <v-col v-if="backBtn">
        <v-btn
          id="btn-stacked-back"
          class="btn-stacked"
          outlined
          @click="back()"
        >
          <v-icon color="primary" style="padding-top: 2px;">mdi-chevron-left</v-icon>
          {{ backBtn }}
        </v-btn>
      </v-col>
      <v-col v-if="cancelBtn" :class="{ 'pl-3': backBtn }">
        <v-btn
          id="btn-stacked-cancel"
          class="btn-stacked"
          outlined
          @click="cancel()"
        >
          {{ cancelBtn }}
        </v-btn>
      </v-col>
    </v-row>
    <div class="pt-4">
      <v-btn
        v-if="submitBtn"
        id="btn-stacked-submit"
        class="btn-stacked"
        color="primary"
        @click="submit"
      >
        {{ submitBtn }}
        <v-icon color="white" style="padding-top: 2px;">mdi-chevron-right</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs
} from '@vue/composition-api'

export default defineComponent({
  name: 'ButtonsStacked',
  props: {
    setBackBtn: {
      default: ''
    },
    setCancelBtn: {
      default: ''
    },
    setSubmitBtn: {
      default: ''
    }
  },
  setup (props, { emit, root }) {
    const localState = reactive({
      backBtn: props.setBackBtn,
      cancelBtn: props.setCancelBtn,
      submitBtn: props.setSubmitBtn
    })
    const back = () => {
      emit('back', true)
    }
    const cancel = () => {
      emit('cancel', true)
    }
    const submit = () => {
      emit('submit', true)
    }

    return {
      back,
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
  box-shadow: none;
  color: $primary-blue;
  width: 100%;
}
</style>
