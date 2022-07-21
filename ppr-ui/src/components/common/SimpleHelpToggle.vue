<template>
  <div>
    <v-btn
      text
      color="primary"
      class="help-btn px-0"
      :ripple="false"
      @click="isHelpContentOpen = !isHelpContentOpen"
    >
      <v-icon>
        mdi-information-outline
      </v-icon>
      {{ isHelpContentOpen ? 'Hide ' + title : title }}
    </v-btn>
    <v-expand-transition>
      <div v-show="isHelpContentOpen" class="help-content">
        <hr class="my-4" />
        <slot></slot>
        <div class="align-right" v-if="hasBottomHideToggle">
          <v-btn
            text
            color="primary"
            class="hide-help-btn pa-0"
            :ripple="false"
            @click="isHelpContentOpen = !isHelpContentOpen"
          >
            Hide Help
          </v-btn>
        </div>
        <hr class="my-4" />
      </div>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'

export default defineComponent({
  name: 'SimleHelpToggle',
  props: {
    toggleButtonTitle: { default: '' },
    /* show or hide secondary toggle within content */
    hasBottomHideToggle: { default: true }
  },
  setup (props) {
    const localState = reactive({
      isHelpContentOpen: false,
      title: props.toggleButtonTitle,
      hasBottomHideToggle: props.hasBottomHideToggle
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
// Remove background on hover
.help-btn::before,
.hide-help-btn::before {
  display: none;
}

.help-btn {
  font-size: 16px;
}

.hide-help-btn {
  font-size: 14px;
  text-decoration: underline;
  height: 25px;
}

.help-content {
  h3,
  h4 {
    color: #495057;
  }
}
</style>
