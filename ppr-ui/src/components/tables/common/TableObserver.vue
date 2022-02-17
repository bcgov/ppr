<template>
  <tr class="observer" style="height: 40px;"/>
</template>

<script>
export default {
  props: ['options'],
  data: () => ({
    observer: null
  }),
  mounted () {
    const options = this.options || {}
    this.observer = new IntersectionObserver(([entry]) => {
      if (entry && entry.isIntersecting) {
        console.log('emitting intersect event')
        this.$emit('intersect', entry)
      }
    }, options)
    console.log('starting observer..')
    this.observer?.observe(this.$el) // eslint-disable-line no-unused-expressions
    console.log('done')
  },
  destroyed () {
    console.log('disconnecting observer..')
    this.observer?.disconnect() // eslint-disable-line no-unused-expressions
    console.log('done')
  }
}
</script>
