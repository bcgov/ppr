<template>
  <v-chip
    v-if="action"
    class="info-chip-badge mr-4"
    label x-small
    :color="chipColors.bgColor"
    :textColor="chipColors.textColor"
    :data-test-id="`${action}-badge`"
  >
    <b>{{ action }}</b>
  </v-chip>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'

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
            return { bgColor: 'darkGray', textColor: 'white' }
          default:
            return { bgColor: 'primary' }
        }
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
