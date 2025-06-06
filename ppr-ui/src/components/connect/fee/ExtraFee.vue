<script setup lang="ts">
defineProps<{ description: string, fee: number, showFeeValue: boolean }>()
</script>
<template>
  <div class="flex justify-between border-b border-bcGovGray-300 py-3 pl-4">
    <p class="font-bold">
      {{ description }}
    </p>
    <p>{{ showFeeValue ? `$${fee.toFixed(2)}`: '$ -' }}</p>
  </div>
</template>
