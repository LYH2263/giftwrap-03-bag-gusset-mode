<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const route = useRoute()
const boxes = ref([])
const bid = ref(1)
const mode = ref('box')            // box | bag
const gusset = ref(0.08)           // 袋装底风琴褶（米）
const out = ref(null)
const snapshot = ref(null)         // 回看的落库快照（唯一真相）
const err = ref('')
const busy = ref(false)

function buildQS(save) {
  const p = new URLSearchParams({ box_id: bid.value, mode: mode.value })
  if (mode.value === 'bag') p.set('gusset_m', String(gusset.value))
  if (save) p.set('save', 'true')
  return p.toString()
}

async function go(save) {
  err.value = ''
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', {
          box_id: bid.value, save: true, mode: mode.value,
          gusset_m: mode.value === 'bag' ? Number(gusset.value) : null,
        })
      : await getJSON(`/api/estimate?${buildQS(false)}`)
    if (save && out.value.run_id) {
      snapshot.value = await getJSON(`/api/runs/${out.value.run_id}`)
    }
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  try {
    const [bs, st] = await Promise.all([getJSON('/api/boxes'), getJSON('/api/settings')])
    boxes.value = bs.items.filter((b) => b.data_quality === 'clean')
    gusset.value = Number(st.bag_gusset ?? 0.08)
    if (route.query.box_id) bid.value = Number(route.query.box_id)
    else if (boxes.value.length) bid.value = boxes.value[0].id
    if (route.query.mode === 'bag' || route.query.mode === 'box') mode.value = route.query.mode
    if (route.query.gusset) gusset.value = Number(route.query.gusset)
    // 从用纸档打开：以落库快照为唯一真相预填表单
    if (route.query.run) {
      const r = await getJSON(`/api/runs/${route.query.run}`)
      snapshot.value = r
      bid.value = r.box_id
      mode.value = r.result?.mode ?? 'box'
      if (r.result?.gusset_m != null) gusset.value = r.result.gusset_m
    }
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">先试算看面积与展开，确认后再写入用纸档。盒装走六面；袋装走袋面两片＋底风琴褶。</p>

    <!-- 回看落库快照：写入值即唯一真相 -->
    <div v-if="snapshot" class="snapshot-bar">
      <span class="pill">用纸档 #{{ snapshot.id }} 落库快照</span>
      <span class="meta">
        mode=<strong>{{ snapshot.result?.mode }}</strong>
        ｜ gusset_m=<strong>{{ snapshot.result?.gusset_m ?? '—' }}</strong>
        ｜ paper_m²=<strong>{{ snapshot.result?.paper_m2 }}</strong>
      </span>
    </div>

    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <div class="mode-switch">
        <button :class="{ on: mode === 'box' }" @click="mode = 'box'">盒装·六面</button>
        <button :class="{ on: mode === 'bag' }" @click="mode = 'bag'">袋装·风琴褶</button>
      </div>
      <label v-if="mode === 'bag'" class="field-label">
        底风琴褶 m
        <input type="number" step="0.01" min="0.001" v-model.number="gusset" />
      </label>
    </div>
    <div class="row">
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
      <span v-if="mode === 'bag' && !(gusset > 0)" class="bad">袋装底风琴褶须为正，否则整单失败不落库</span>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>

    <!-- 同参再干算与回看快照互证 -->
    <p v-if="snapshot && out && !err"
       class="stat-line"
       :class="out.mode === snapshot.result?.mode
          && (out.gusset_m ?? null) === (snapshot.result?.gusset_m ?? null)
          && out.paper_m2 === snapshot.result?.paper_m2 ? 'match' : 'mismatch'">
      {{ out.mode === snapshot.result?.mode
          && (out.gusset_m ?? null) === (snapshot.result?.gusset_m ?? null)
          && out.paper_m2 === snapshot.result?.paper_m2
        ? '✓ 同参再算与落库快照三路一致（mode / gusset_m / paper_m2）'
        : '✗ 当前试算与落库快照不一致（参数已变）' }}
    </p>

    <div v-if="out" class="result-board">
      <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
      <p class="stat-line">
        <span class="pill">{{ out.mode === 'bag' ? '袋装' : '盒装' }}</span>
        <template v-if="out.mode === 'bag'">底风琴褶 {{ out.gusset_m }} m ｜</template>
        十字丝带约 {{ out.ribbon?.ribbon_m ?? out.ribbon }} m
      </p>
      <BoxUnfold
        :l="out.box.length"
        :w="out.box.width"
        :h="out.box.height"
        :paper-m2="out.paper_m2"
        :mode="out.mode"
        :gusset="out.gusset_m"
      />
    </div>
  </div>
</template>
