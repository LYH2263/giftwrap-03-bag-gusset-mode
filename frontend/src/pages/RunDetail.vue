<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>用纸档 #{{ run.id }}</h1>
      <p class="lede">
        {{ run.box_name }} ｜ 折边系数 {{ run.overlap }}
      </p>
      <div class="result-board">
        <!-- 落库快照：唯一真相 -->
        <ul class="snapshot-grid">
          <li><span>mode</span><strong>{{ run.result?.mode }}</strong></li>
          <li><span>gusset_m</span><strong>{{ run.result?.gusset_m ?? '—' }}</strong></li>
          <li><span>paper_m²</span><strong>{{ run.result?.paper_m2 }}</strong></li>
          <li><span>ribbon_m</span><strong>{{ run.result?.ribbon?.ribbon_m ?? '—' }}</strong></li>
        </ul>
        <BoxUnfold
          :l="run.box_length"
          :w="run.box_width"
          :h="run.box_height"
          :paper-m2="run.result?.paper_m2"
          :mode="run.result?.mode ?? 'box'"
          :gusset="run.result?.gusset_m ?? null"
        />
        <div class="row" style="margin-top: 1.25rem">
          <router-link class="btn" :to="`/bench?run=${run.id}`">拿此快照去算纸台同参再算</router-link>
          <router-link class="btn ghost" to="/history">返回用纸档</router-link>
        </div>
      </div>
    </template>
  </div>
</template>
