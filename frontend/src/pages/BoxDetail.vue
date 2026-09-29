<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const props = defineProps({ id: String })
const box = ref(null)
const err = ref('')
const busy = ref(false)
const mode = ref('box')
const gusset = ref(0.08)
const out = ref(null)

async function go() {
  err.value = ''
  busy.value = true
  try {
    const p = new URLSearchParams({ mode: mode.value })
    if (mode.value === 'bag') p.set('gusset_m', String(gusset.value))
    out.value = await getJSON(`/api/estimate?box_id=${props.id}&${p.toString()}`)
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  try {
    const [b, st] = await Promise.all([
      getJSON(`/api/boxes/${props.id}`),
      getJSON('/api/settings'),
    ])
    box.value = b
    gusset.value = Number(st.bag_gusset ?? 0.08)
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="box">
      <h1>{{ box.name }}</h1>
      <p class="lede">
        {{ box.length }} × {{ box.width }} × {{ box.height }} m
        <span class="pill" :class="{ warn: box.data_quality === 'dirty' }">
          {{ box.data_quality === 'dirty' ? '脏数据' : '可用' }}
        </span>
      </p>
      <p v-if="box.data_quality === 'dirty'" class="bad">{{ box.note }}</p>

      <div class="row" style="margin-top: 1rem">
        <div class="mode-switch">
          <button :class="{ on: mode === 'box' }" @click="mode = 'box'">盒装·六面</button>
          <button :class="{ on: mode === 'bag' }" @click="mode = 'bag'">袋装·风琴褶</button>
        </div>
        <label v-if="mode === 'bag'" class="field-label">
          底风琴褶 m
          <input type="number" step="0.01" min="0.001" v-model.number="gusset" />
        </label>
        <button :disabled="busy || (mode === 'bag' && !(gusset > 0))" @click="go">试算</button>
      </div>
      <p v-if="mode === 'bag' && !(gusset > 0)" class="bad">袋装底风琴褶须为正，否则整单失败不落库</p>

      <BoxUnfold
        :l="box.length"
        :w="box.width"
        :h="box.height"
        :paper-m2="out?.paper_m2 ?? null"
        :mode="mode"
        :gusset="mode === 'bag' ? gusset : null"
      />
      <p v-if="out" class="stat-line">
        <span class="pill">{{ out.mode === 'bag' ? '袋装' : '盒装' }}</span>
        用纸 <strong>{{ out.paper_m2 }}</strong> m²
        <template v-if="out.mode === 'bag'">｜ 底褶 {{ out.gusset_m }} m</template>
        ｜ 十字丝带约 {{ out.ribbon?.ribbon_m ?? out.ribbon }} m
      </p>

      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn" :to="`/bench?box_id=${box.id}&mode=${mode}${mode === 'bag' ? `&gusset=${gusset}` : ''}`">
          用此参数去算纸
        </router-link>
        <router-link class="btn ghost" to="/boxes">返回清单</router-link>
      </div>
    </template>
  </div>
</template>
