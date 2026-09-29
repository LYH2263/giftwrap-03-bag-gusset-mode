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
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="lede">算纸页「写入用纸档」后的落库快照。mode / gusset_m / paper_m² 以写入值为准，改默认底褶不影响旧档。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/runs/${r.id}`">
          #{{ r.id }} {{ r.box_name }}
          <span class="pill" :class="{ warn: r.result?.mode === 'bag' }">
            {{ r.result?.mode === 'bag' ? '袋装' : '盒装' }}
          </span>
        </router-link>
        <span class="meta">
          gusset {{ r.result?.gusset_m ?? '—' }} m ｜
          {{ r.result?.paper_m2 ?? '—' }} m²
        </span>
      </li>
    </ul>
  </div>
</template>
