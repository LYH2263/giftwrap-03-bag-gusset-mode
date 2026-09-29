<script setup>
import { onMounted, ref, watch } from 'vue'
import { getJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const props = defineProps({ id: String })
const box = ref(null)
const mode = ref('box')
const gusset = ref(0.08)
const defaultGusset = ref(0.08)
const preview = ref(null)
const err = ref('')

async function loadPreview() {
  if (!box.value || box.value.data_quality === 'dirty') {
    preview.value = null
    return
  }
  err.value = ''
  try {
    const qs =
      mode.value === 'bag'
        ? `/api/estimate?box_id=${props.id}&mode=bag&gusset_m=${Number(gusset.value)}`
        : `/api/estimate?box_id=${props.id}&mode=box`
    preview.value = await getJSON(qs)
  } catch (e) {
    preview.value = null
    err.value = String(e.message || e)
  }
}

onMounted(async () => {
  try {
    const [b, settings] = await Promise.all([
      getJSON(`/api/boxes/${props.id}`),
      getJSON('/api/settings'),
    ])
    box.value = b
    defaultGusset.value = Number(settings.gusset_m ?? 0.08)
    gusset.value = defaultGusset.value
    await loadPreview()
  } catch (e) {
    err.value = String(e.message || e)
  }
})

watch([mode, gusset], loadPreview)
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

      <div v-else class="row">
        <div class="seg" role="group" aria-label="包装模式">
          <button type="button" :class="{ ghost: mode !== 'box' }" @click="mode = 'box'">盒装</button>
          <button type="button" :class="{ ghost: mode !== 'bag' }" @click="mode = 'bag'">袋装</button>
        </div>
        <label v-if="mode === 'bag'" class="gusset-field">
          底风琴褶(m)
          <input v-model.number="gusset" type="number" min="0.001" step="0.01" />
        </label>
      </div>

      <BoxUnfold
        v-if="box.data_quality !== 'dirty'"
        :mode="mode"
        :l="preview?.box.length ?? box.length"
        :w="preview?.box.width ?? box.width"
        :h="box.height"
        :gusset="preview?.gusset_m ?? gusset"
        :paper-m2="preview?.paper_m2 ?? null"
      />
      <BoxUnfold v-else :l="box.length" :w="box.width" :h="box.height" />

      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn" :to="`/bench?box=${box.id}&mode=${mode}`">用此盒去算纸</router-link>
        <router-link class="btn ghost" to="/boxes">返回清单</router-link>
      </div>
    </template>
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
