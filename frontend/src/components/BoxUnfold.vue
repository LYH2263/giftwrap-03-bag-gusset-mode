<script setup>
import { computed } from 'vue'

const props = defineProps({
  l: { type: Number, default: 0 },
  w: { type: Number, default: 0 },
  h: { type: Number, default: 0 },
  paperM2: { type: Number, default: null },
  mode: { type: String, default: 'box' },       // box | bag
  gusset: { type: Number, default: null },       // 袋装底风琴褶
})

const fmt = (n) => Number(n).toFixed(2)
const isBag = computed(() => props.mode === 'bag')
// 袋装：袋宽取盒长 l，袋高取盒宽 w，盒高 h 不参与。
const bagW = computed(() => props.l)
const bagH = computed(() => props.w)
</script>

<template>
  <div class="unfold">
    <!-- 袋装：前后两片袋面 + 底风琴褶 -->
    <template v-if="isBag">
      <p class="unfold-title">袋面展开示意（风琴褶底）</p>
      <svg class="unfold-svg" viewBox="0 0 280 170" aria-hidden="true">
        <g v-for="(x, i) in [26, 156]" :key="i">
          <rect class="panel top" :x="x" y="24" width="98" height="84" rx="2" />
          <rect class="panel gusset" :x="x" y="112" width="98" height="26" rx="2" />
          <text :x="x + 49" y="60" text-anchor="middle">袋面 {{ fmt(bagW) }}×{{ fmt(bagH) }}</text>
          <text :x="x + 49" y="82" text-anchor="middle">{{ i === 0 ? '前片' : '后片' }}</text>
          <text :x="x + 49" y="129" text-anchor="middle">底风琴褶 {{ fmt(gusset ?? 0) }}</text>
        </g>
        <text x="140" y="158" text-anchor="middle">袋宽 × (袋高 + 底褶) × 2 片 × 折边</text>
      </svg>
      <p v-if="paperM2 != null" class="stat-line">
        估算用纸 <strong>{{ Number(paperM2).toFixed(4) }}</strong> m²
        ＝ {{ fmt(bagW) }} × ({{ fmt(bagH) }} + {{ fmt(gusset ?? 0) }}) × 2 × 折边
      </p>
      <p v-else class="stat-line">
        袋面 {{ fmt(bagW) }} × {{ fmt(bagH) }} m，底风琴褶 {{ fmt(gusset ?? 0) }} m
      </p>
    </template>

    <!-- 盒装：六面展开 -->
    <template v-else>
      <p class="unfold-title">盒体展开示意</p>
      <svg class="unfold-svg" viewBox="0 0 280 180" aria-hidden="true">
        <rect class="panel" x="95" y="18" width="90" height="42" rx="2" />
        <rect class="panel top" x="95" y="68" width="90" height="52" rx="2" />
        <rect class="panel" x="20" y="68" width="68" height="52" rx="2" />
        <rect class="panel" x="192" y="68" width="68" height="52" rx="2" />
        <rect class="panel" x="95" y="128" width="90" height="38" rx="2" />
        <text x="140" y="44" text-anchor="middle">顶 {{ fmt(l) }}×{{ fmt(w) }}</text>
        <text x="140" y="98" text-anchor="middle">正面</text>
        <text x="54" y="98" text-anchor="middle">侧</text>
        <text x="226" y="98" text-anchor="middle">侧</text>
        <text x="140" y="152" text-anchor="middle">h≈{{ fmt(h) }}</text>
      </svg>
      <p v-if="paperM2 != null" class="stat-line">
        估算用纸 <strong>{{ Number(paperM2).toFixed(4) }}</strong> m²（含折边系数）
      </p>
      <p v-else class="stat-line">
        外形 {{ fmt(l) }} × {{ fmt(w) }} × {{ fmt(h) }} m
      </p>
    </template>
  </div>
</template>
