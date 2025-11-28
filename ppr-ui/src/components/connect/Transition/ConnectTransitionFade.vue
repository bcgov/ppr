<template>
  <Transition name="fade">
    <slot />
  </Transition>
</template>
<style>
.fade-enter-active {
  transition: opacity 0.3s ease-in-out;
}
.fade-leave-active {
  transition: opacity 0s ease-in-out;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion) {
  .fade-enter-active {
    transition: opacity 0s ease-in-out;
  }
  .fade-leave-active {
    transition: opacity 0s ease-in-out;
  }
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
}
</style>
