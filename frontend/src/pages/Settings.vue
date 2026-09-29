<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'

const s = ref({})
const gusset = ref(0.08)
const overlap = ref(1.15)
const err = ref('')
const ok = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    s.value = await getJSON('/api/settings')
    gusset.value = Number(s.value.gusset_m ?? 0.08)
    overlap.value = Number(s.value.overlap ?? 1.15)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function save() {
  err.value = ''
  ok.value = ''
  if (Number(gusset.value) <= 0) {
    err.value = '默认底风琴褶必须大于 0。'
    return
  }
  busy.value = true
  try {
    s.value = await putJSON('/api/settings', {
      overlap: Number(overlap.value),
      gusset_m: Number(gusset.value),
    })
    ok.value = '已保存。新单默认底褶随之更新；已落库快照不受影响。'
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>设置</h1>
    <p class="lede">全局默认参数。改默认底褶只影响之后的新单，已写入用纸档的快照仍以当时值为准。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-if="ok" class="ok">{{ ok }}</p>
    <ul class="item-list form">
      <li>
        <span>折边系数 overlap</span>
        <input v-model.number="overlap" type="number" min="0.001" step="0.01" />
      </li>
      <li>
        <span>袋装默认底风琴褶 gusset_m (m)</span>
        <input v-model.number="gusset" type="number" min="0.001" step="0.01" />
      </li>
    </ul>
    <div class="row" style="margin-top: 1.25rem">
      <button :disabled="busy" @click="save">保存设置</button>
    </div>
  </div>
</template>

<style scoped>
li.form,
.form li {
  gap: 1rem;
}
input {
  width: 130px;
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.72);
  font: inherit;
}
.ok {
  color: var(--ok);
  font-weight: 600;
}
</style>
