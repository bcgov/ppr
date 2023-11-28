<template>
  <div class="observer" />
</template>

<script>

export default {
  props: {
    options: {
      type: Object,
      default: () => {}
    }
  },
  emits: ['intersect'],
  data: () => ({
    observer: null
  }),
  mounted () {
    const options = this.options || {}
    this.observer = new IntersectionObserver(([entry]) => {
      if (entry && entry.isIntersecting) {
        this.$emit('intersect', entry)
      }
    }, options)
    this.observer?.observe(this.$el)
  },
  unmounted () {
    this.observer?.disconnect()
  }
}
</script>
