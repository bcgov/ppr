<template>
  <div id="help-toggle-container">
    <v-btn
      text
      color="primary"
      class="help-btn px-0"
      :ripple="false"
      @click="isHelpContentOpen = !isHelpContentOpen"
      data-test-id="help-toggle-btn"
    >
      <v-icon class="mr-1">
        mdi-help-circle-outline
      </v-icon>
      {{ title }}
    </v-btn>
    <v-expand-transition>
      <div v-show="isHelpContentOpen" class="help-content mb-10">
        <hr class="my-4" />
        <slot class="content"></slot>
        <div class="align-right" v-if="showBottomToggle">
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
import { computed } from 'vue'
import { defineComponent, reactive, toRefs } from 'vue-demi'

export default defineComponent({
  name: 'SimpleHelpToggle',
  props: {
    toggleButtonTitle: { default: '' },
    /* show or hide secondary toggle within content */
    hasBottomHideToggle: { default: true },
    defaultHideText: { default: true }
  },
  setup (props) {
    const localState = reactive({
      isHelpContentOpen: false,
      hideText: props.defaultHideText ? 'Hide Help' : 'Hide ' + props.toggleButtonTitle,
      title: computed(() : string => localState.isHelpContentOpen ? localState.hideText : props.toggleButtonTitle),
      showBottomToggle: props.hasBottomHideToggle
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#help-toggle-container::v-deep {
  // Remove background on hover
  .help-btn::before,
  .hide-help-btn::before {
    display: none;
  }

  .help-btn {
    font-size: 16px;
    height: 24px;
  }

  .hide-help-btn {
    font-size: 14px;
    text-decoration: underline;
    height: 25px;
  }

  .help-content {
    h3 {
      color: $gray9;
    }
    h4,
    p {
      color: $gray7;
    }
    hr {
      border-top: 1px dashed $gray6;
    }
  }
}
</style>
