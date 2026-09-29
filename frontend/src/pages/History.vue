<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const err = ref('')

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})

const modeLabel = (r) => (r.result?.mode === 'bag' ? '袋装' : '盒装')
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="lede">算纸页「写入用纸档」后的落库快照，按次保留盒名、模式、底褶与面积；快照即唯一真相。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/runs/${r.id}`">
          {{ r.box_name }}
          <span class="pill" :class="{ bag: r.result?.mode === 'bag' }">{{ modeLabel(r) }}</span>
        </router-link>
        <span class="meta">
          <template v-if="r.result?.mode === 'bag'">底褶 {{ r.result?.gusset_m }} m · </template>
          {{ r.result?.paper_m2 ?? '—' }} m²
        </span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.pill.bag {
  background: rgba(184, 151, 59, 0.18);
  color: var(--foil);
  margin-left: 0.5rem;
}
</style>
