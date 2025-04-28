<script setup lang="ts">
defineProps({
  name: {
    type: String,
    required: true
  }
})
</script>
<template>
  <div
    :data-cy="'form_wrapper_' + name"
    class="grid grid-cols-4 py-10 px-10"
  >
    <div
      :data-cy="'form_label_' + name"
      class="col-span-1 pr-5"
    >
      <slot name="label" />
    </div>
    <div
      :data-cy="'form_body_' + name"
      class="col-span-3"
    >
      <slot name="form" />
    </div>
  </div>
</template>
