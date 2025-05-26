<template>
  <v-chip
    v-if="action"
    class="info-chip-badge mr-4"
    variant="flat"
    x-small
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
          case 'HISTORICAL':
          case 'CANCELLED':
          case 'VOID':
          case 'COMPLETED':
            return { bgColor: 'grey-lighten-2' }
          case 'LIEN':
          case 'LOCKED':
          case 'PAYMENT PENDING':
            return { bgColor: 'darkGray' }
          default:
            return { bgColor: 'primary' }
        }
      }),
      isLockedAction: computed((): boolean => ['LOCKED', 'PAYMENT PENDING'].includes(props.action))
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.info-chip-badge {
  img {
    height: 10px;
    margin-right: 6px;
  }
  padding-top: 2px !important;
  padding-bottom: 2px !important;
}

</style>
