<template>
  <div class="col my-2" @click="$emit('select', league)">
    <div
      :id="league.slug"
      :class="['card', 'text-center', 'h-100', 'bg-light', 'league-button', { clicked: selected }]"
    >
      <img
        :src="`/assets/img/${league.slug}.png`"
        class="card-img-top bg-dark"
        :alt="league.name"
      />
      <div class="p-2 my-auto">
        <h5 class="card-text">{{ league.name }}</h5>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  league: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['select'])
</script>