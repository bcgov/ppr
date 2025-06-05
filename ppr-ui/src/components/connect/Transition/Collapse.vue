<template>
  <Transition name="collapse">
    <slot />
  </Transition>
</template>
<style>
.collapse-enter-active,
.collapse-leave-active {
  transition: max-height 0.3s ease-in-out, opacity 0.3s ease-in-out;
}
.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
}
.collapse-enter-to,
.collapse-leave-from {
  max-height: 1000px;
  opacity: 1;
}

@media (prefers-reduced-motion) {
  .collapse-enter-active,
  .collapse-leave-active {
    transition: max-height 0s ease-out, opacity 0s ease-out;
  }
  .collapse-enter-from,
  .collapse-leave-to {
    max-height: 0;
    opacity: 0;
  }
  .collapse-enter-to,
  .collapse-leave-from {
    max-height: 1000px;
    opacity: 1;
  }
}
</style>
