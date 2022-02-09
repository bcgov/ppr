<template>
  <div>
    <div v-if="isDoubledUp">
      <v-row no-gutters>
      <v-col v-if="backBtn">
        <v-btn
          id="btn-stacked-back"
          class="btn-stacked"
          outlined
          @click="back()"
        >
          <v-icon v-if="backBtn !== 'Save and Resume Later'" color="primary" style="padding-top: 2px;">
            mdi-chevron-left
          </v-icon>
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
    </div>
    <div v-else>
      <div v-if="cancelBtn">
          <v-btn
            id="btn-stacked-cancel"
            class="btn-stacked"
            outlined
            @click="cancel()"
          >
            {{ cancelBtn }}
          </v-btn>
      </div>
      <div v-if="backBtn" :class="{ 'pt-4': cancelBtn }">
          <v-btn
            id="btn-stacked-back"
            class="btn-stacked"
            outlined
            @click="back()"
          >
            <v-icon v-if="backBtn !== 'Save and Resume Later'" color="primary" style="padding-top: 2px;">
              mdi-chevron-left
            </v-icon>
            {{ backBtn }}
          </v-btn>
      </div>
    </div>
    <div v-if="saveBtn" :class="{ 'pt-4': saveBtn }">
      <v-btn
        v-if="saveBtn"
        id="btn-stacked-save"
        class="btn-stacked"
        outlined
        @click="save"
      >
        {{ saveBtn }}
      </v-btn>
    </div>
    <div class="pt-4">
      <v-btn
        v-if="submitBtn"
        id="btn-stacked-submit"
        class="btn-stacked"
        color="primary"
        @click="submit"
        :disabled="disableSubmitBtn"
      >
        {{ submitBtn }}
        <v-icon color="white" style="padding-top: 2px;">mdi-chevron-right</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script lang="ts">
import {
  computed,
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
    },
    setDisableSubmitBtn: {
      default: false
    },
    setSaveButton: {
      default: ''
    }
  },
  setup (props, { emit, root }) {
    const localState = reactive({
      backBtn: props.setBackBtn,
      cancelBtn: props.setCancelBtn,
      submitBtn: props.setSubmitBtn,
      saveBtn: props.setSaveButton,
      disableSubmitBtn: props.setDisableSubmitBtn,
      isDoubledUp: computed(() => {
        if (localState.submitBtn !== 'Review and Complete') {
          return true
        }
        return false
      })
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
    const save = () => {
      emit('save', true)
    }

    return {
      back,
      cancel,
      submit,
      save,
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
