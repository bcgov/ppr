<template>
  <v-chip
    v-if="action"
    class="info-chip-badge mr-4"
    variant="elevated"
    xSmall
    :color="chipColors.bgColor"
    :data-test-id="`${action}-badge`"
  >
    <img
      v-if="isLockedAction"
      src="@/assets/svgs/lockicon_white.svg"
    ><b>{{ action }}</b>
  </v-chip>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'

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
            return { bgColor: 'grey-lighten-2' }
          case 'LIEN':
          case 'LOCKED':
            return { bgColor: 'darkGray' }
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
.info-chip-badge img {
  height: 9px;
  margin-right: 6px;
}
</style>
