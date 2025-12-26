<template>
  <div class="container">
    <div class="row">
      <div class="col text-center m-2">
        <h1>LoL eSports Calendar Generator</h1>
      </div>
    </div>
    
    <div class="row">
      <div class="col alert alert-primary mx-3 text-center">
        <span>Your link: {{ selectedLeagues.length === 0 ? 'Select some leagues first!' : '' }}</span>
        <a id="calendar_url" :href="calendarUrl">{{ selectedLeagues.join(', ') }}</a>
      </div>
    </div>
    
    <div class="row">
      <div class="col alert alert-info mx-3 text-center">
        Copy the link above and paste it into your calendar application. There may be an option "Add calendar by URL."
      </div>
    </div>
    
    <div class="row row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5 row-cols-xl-6">
      <League
        v-for="league in leagues"
        :key="league.slug"
        :league="league"
        :selected="!!selected[league.slug]"
        @select="handleSelectLeague"
      />
    </div>
    
    <div class="row">
      <div class="col text-center">
        <p>
          <a href="https://github.com/asherdavidson/lol_esports_calendar_generator">Source Code</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import League from './components/League.vue'

const leagues = ref([])
const selected = ref({})

const selectedLeagues = computed(() => {
  return Object.keys(selected.value)
    .filter(slug => selected.value[slug])
    .sort()
})

const calendarUrl = computed(() => {
  const leaguesList = selectedLeagues.value
  if (leaguesList.length === 0) {
    return '#'
  }
  return `/api/query-leagues?leagues=${leaguesList.join(',')}`
})

const loadInitialData = async () => {
  try {
    const response = await fetch('/api/leagues')
    const data = await response.json()
    console.log(data)
    leagues.value = data.leagues
  } catch (error) {
    console.error('Error loading leagues:', error)
  }
}

const handleSelectLeague = (league) => {
  selected.value = {
    ...selected.value,
    [league.slug]: !selected.value[league.slug]
  }
}

onMounted(() => {
  loadInitialData()
})
</script>