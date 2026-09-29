<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const route = useRoute()
const boxes = ref([])
const bid = ref(1)
const mode = ref('box') // box=盒装 / bag=袋装
const gusset = ref(0.08)
const defaultGusset = ref(0.08)
const out = ref(null)
const err = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    const [blist, settings] = await Promise.all([getJSON('/api/boxes'), getJSON('/api/settings')])
    boxes.value = blist.items.filter((b) => b.data_quality === 'clean')
    if (boxes.value.length) bid.value = boxes.value[0].id
    defaultGusset.value = Number(settings.gusset_m ?? 0.08)
    gusset.value = defaultGusset.value
    if (route.query.box && boxes.value.some((b) => b.id === Number(route.query.box))) {
      bid.value = Number(route.query.box)
    }
    if (route.query.mode === 'bag' || route.query.mode === 'box') mode.value = route.query.mode
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function onModeChange() {
  out.value = null
  err.value = ''
  if (mode.value === 'bag') gusset.value = defaultGusset.value
}

function payload(save) {
  const p = { box_id: bid.value, mode: mode.value, wrap_style: 'cross', save }
  if (mode.value === 'bag') p.gusset_m = Number(gusset.value)
  return p
}

async function go(save) {
  err.value = ''
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', payload(true))
      : await getJSON(
          `/api/estimate?box_id=${bid.value}&mode=${mode.value}` +
            (mode.value === 'bag' ? `&gusset_m=${Number(gusset.value)}` : ''),
        )
  } catch (e) {
    out.value = null
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">先试算看面积与展开，确认后再写入用纸档。盒装走六面，袋装走袋面风琴褶，两套口径互不相替。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <div class="seg" role="group" aria-label="包装模式">
        <button
          type="button"
          :class="{ ghost: mode !== 'box' }"
          :aria-pressed="mode === 'box'"
          @click="mode = 'box'; onModeChange()"
        >盒装</button>
        <button
          type="button"
          :class="{ ghost: mode !== 'bag' }"
          :aria-pressed="mode === 'bag'"
          @click="mode = 'bag'; onModeChange()"
        >袋装</button>
      </div>
      <label v-if="mode === 'bag'" class="gusset-field">
        底风琴褶(m)
        <input v-model.number="gusset" type="number" min="0.001" step="0.01" />
      </label>
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="mode === 'bag' && Number(gusset) <= 0" class="bad">
      袋装底风琴褶必须大于 0，否则整单不落库。
    </p>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <p class="stat-line">
        <span class="pill">{{ out.mode === 'bag' ? '袋装' : '盒装' }}</span>
        <template v-if="out.mode === 'bag'">底风琴褶 {{ out.gusset_m }} m</template>
      </p>
      <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
      <p class="stat-line" v-if="out.ribbon">
        {{ out.mode === 'bag' ? '袋装十字' : '十字' }}丝带约 {{ out.ribbon.ribbon_m ?? out.ribbon }} m
      </p>
      <BoxUnfold
        :mode="out.mode"
        :l="out.box.length"
        :w="out.box.width"
        :h="out.box.height"
        :gusset="out.gusset_m"
        :paper-m2="out.paper_m2"
      />
    </div>
  </div>
</template>

<style scoped>
.seg {
  display: inline-flex;
  gap: 0.35rem;
}
.gusset-field {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.92rem;
  color: var(--ink-soft);
}
.gusset-field input {
  width: 110px;
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.72);
  font: inherit;
}
</style>
