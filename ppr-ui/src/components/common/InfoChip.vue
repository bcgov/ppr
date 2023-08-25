<template>
  <v-chip
    v-if="action"
    class="info-chip-badge mr-4"
    label x-small
    :color="chipColors.bgColor"
    :textColor="chipColors.textColor"
    :data-test-id="`${action}-badge`"
  >
    <v-icon v-if="isLockedAction" class="mr-1">mdi-lock</v-icon><b>{{ action }}</b>
    <v-icon class="mr-1">mdi-lock</v-icon><b>{{ action }}</b>
  </v-chip>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'

export default defineComponent({
  name: 'InfoChip',
  components: {},
  props: {
    action: {
      type: String,
      default: ''
    }
  },
  setup (props) {
    interface colorConfig {
      bgColor: string
      textColor?: string
    }

    const localState = reactive({
      chipColors: computed((): colorConfig => {
        switch (props.action) {
          case 'DELETED':
          case 'DECEASED':
            return { bgColor: '#grey lighten-2' }
          case 'LIEN':
          case 'LOCKED':
            return { bgColor: 'darkGray', textColor: 'white' }
          default:
            return { bgColor: 'primary' }
        }
      }),
      isLockedAction: computed((): boolean => props.action === 'LOCKED')
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.info-chip-badge .mdi-lock {
  font-size: 9px !important;
}
</style>
