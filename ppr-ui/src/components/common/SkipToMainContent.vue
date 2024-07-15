<template>
  <a
    :href="`#${props.mainContentId}`"
    class="skip-main-content-link py-6 fs-16"
    @click="skipToContent"
  >
    Skip to Main Content
  </a>
</template>

<script setup lang="ts">
const props = defineProps<{
  mainContentId: string
}>()

// Focuses on main content id and prevents anchor link in url
const skipToContent = event => {
  event.preventDefault()
  const mainContent = document.getElementById(props.mainContentId)
  if (mainContent) {
    mainContent.focus()
  }
}
</script>

<style lang="scss">
.skip-main-content-link {
  position: absolute;
  z-index: 100;
  left: calc(50% - 100px);
  transform: translateY(-100%);
  width: 200px;
  border: 2px solid #000;
  border-radius: 4px;
  color: black;
  text-align: center;
  text-decoration: none;
  background: #fff;
}

.skip-main-content-link:focus {
  transform: translateY(0%);
}
</style>
