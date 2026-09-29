<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const props = defineProps({ id: String })
const run = ref(null)
const box = ref(null)
const dry = ref(null)
const err = ref('')
const busy = ref(false)

const snap = () => run.value?.result ?? {}

onMounted(load)

async function load() {
  err.value = ''
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
    box.value = await getJSON(`/api/boxes/${run.value.box_id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
}

// 以落库快照的同一组参数去算纸台干算（不落库），与回看互证。
async function rerunDry() {
  err.value = ''
  busy.value = true
  try {
    const s = snap()
    const params = new URLSearchParams({
      box_id: String(run.value.box_id),
      mode: s.mode ?? 'box',
      overlap: String(run.value.overlap ?? s.overlap),
      save: 'false',
    })
    if (s.mode === 'bag') params.set('gusset_m', String(s.gusset_m))
    dry.value = await getJSON(`/api/estimate?${params.toString()}`)
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}

const consistent = () => {
  if (!dry.value) return null
  const s = snap()
  return (
    dry.value.mode === s.mode &&
    Number(dry.value.gusset_m) === Number(s.gusset_m) &&
    Number(dry.value.paper_m2) === Number(s.paper_m2)
  )
}
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>{{ run.box_name }} · 用纸档 #{{ run.id }}</h1>
      <p class="lede">以下数字取自落库快照，不随后续默认参数变动而重算。</p>

      <ul class="item-list snapshot">
        <li>
          <span>模式 mode</span>
          <span class="meta">
            <span class="pill" :class="{ bag: snap().mode === 'bag' }">
              {{ snap().mode === 'bag' ? '袋装' : '盒装' }}
            </span>
          </span>
        </li>
        <li v-if="snap().mode === 'bag'">
          <span>底风琴褶 gusset_m</span>
          <span class="meta">{{ snap().gusset_m }} m</span>
        </li>
        <li>
          <span>用纸 paper_m2</span>
          <span class="meta strong">{{ snap().paper_m2 }} m²</span>
        </li>
        <li>
          <span>折边系数 overlap</span>
          <span class="meta">{{ run.overlap }}</span>
        </li>
        <li v-if="snap().ribbon">
          <span>十字丝带</span>
          <span class="meta">{{ snap().ribbon.ribbon_m }} m</span>
        </li>
      </ul>

      <BoxUnfold
        :mode="snap().mode ?? 'box'"
        :l="box?.length"
        :w="box?.width"
        :h="box?.height"
        :gusset="snap().gusset_m"
        :paper-m2="snap().paper_m2"
      />

      <div class="row" style="margin-top: 1.25rem">
        <button :disabled="busy" @click="rerunDry">同参再干算（互证）</button>
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
      </div>

      <div v-if="dry" class="result-board">
        <p v-if="consistent()" class="ok">
          ✓ 互证一致：mode / gusset_m / paper_m2 三路与落库快照相同（{{ dry.paper_m2 }} m²）。
        </p>
        <p v-else class="bad">
          ✗ 不一致：干算 {{ dry.mode }} / {{ dry.gusset_m }} / {{ dry.paper_m2 }}
          与快照 {{ snap().mode }} / {{ snap().gusset_m }} / {{ snap().paper_m2 }} 有出入。
        </p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.snapshot {
  margin-top: 0.5rem;
}
.pill.bag {
  background: rgba(184, 151, 59, 0.18);
  color: var(--foil);
}
.meta.strong {
  font-weight: 700;
  color: var(--wash-b);
}
.ok {
  color: var(--ok);
  font-weight: 600;
}
</style>
