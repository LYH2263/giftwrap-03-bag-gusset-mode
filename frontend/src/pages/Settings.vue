<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'

const s = ref({})
const gusset = ref(0.08)
const err = ref('')
const saved = ref('')
const busy = ref(false)

async function load() {
  s.value = await getJSON('/api/settings')
  gusset.value = Number(s.value.bag_gusset ?? 0.08)
}

async function saveGusset() {
  err.value = ''
  saved.value = ''
  busy.value = true
  try {
    await putJSON('/api/settings/bag-gusset', { bag_gusset: Number(gusset.value) })
    await load()
    saved.value = '已保存。只影响之后新建的袋装单，旧用纸档快照不变。'
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}

onMounted(() => load().catch((e) => { err.value = String(e.message || e) }))
</script>

<template>
  <div class="page">
    <h1>设置</h1>
    <p class="lede">全局参数。折边系数只读；袋装默认底风琴褶可在此调整。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <ul class="item-list">
      <li>
        <span>折边系数 overlap</span>
        <span class="meta">{{ s.overlap }}</span>
      </li>
      <li>
        <span>袋装默认底风琴褶 bag_gusset（m）</span>
        <span class="meta">
          <input type="number" step="0.01" min="0.001" v-model.number="gusset" />
        </span>
      </li>
    </ul>
    <div class="row" style="margin-top: 1rem">
      <button :disabled="busy || !(gusset > 0)" @click="saveGusset">保存默认底褶</button>
      <span v-if="saved" class="pill">{{ saved }}</span>
      <span v-if="!(gusset > 0)" class="bad">底风琴褶须为正</span>
    </div>
  </div>
</template>
