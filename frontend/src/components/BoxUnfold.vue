<script setup>
import { computed } from 'vue'

const props = defineProps({
  l: { type: Number, default: 0 }, // 盒：长 / 袋：袋宽
  w: { type: Number, default: 0 }, // 盒：宽 / 袋：袋高
  h: { type: Number, default: 0 }, // 盒：高
  gusset: { type: Number, default: null }, // 袋：底风琴褶
  mode: { type: String, default: 'box' }, // box=盒装六面 / bag=袋装袋面
  paperM2: { type: Number, default: null },
})

const isBag = computed(() => props.mode === 'bag')
const num = (v) => Number(v || 0).toFixed(2)
</script>

<template>
  <div class="unfold">
    <!-- 袋装：袋面 + 底风琴褶示意 -->
    <template v-if="isBag">
      <p class="unfold-title">袋面展开示意（风琴褶）</p>
      <svg class="unfold-svg" viewBox="0 0 280 210" aria-hidden="true">
        <!-- 后片（翻折提示） -->
        <rect class="panel faint" x="80" y="14" width="120" height="26" rx="2" />
        <line x1="80" y1="40" x2="200" y2="40" class="fold" stroke-dasharray="4 3" />
        <text x="140" y="31" text-anchor="middle">后片（前后共 ×2）</text>
        <!-- 前片主体：袋宽 × 袋高 -->
        <rect class="panel top" x="80" y="44" width="120" height="104" rx="2" />
        <text x="140" y="92" text-anchor="middle">前片</text>
        <text x="140" y="110" text-anchor="middle">
          {{ num(l) }} × {{ num(w) }}
        </text>
        <!-- 底风琴褶 -->
        <rect class="panel gusset" x="80" y="148" width="120" height="26" rx="2" />
        <path class="gusset-fold" d="M80 161 L100 150 L120 161 L140 150 L160 161 L180 150 L200 161" fill="none" />
        <text x="140" y="188" text-anchor="middle">
          底风琴褶 {{ num(gusset) }}
        </text>
        <!-- 袋宽标注 -->
        <text x="60" y="100" text-anchor="middle">袋宽</text>
      </svg>
      <p class="stat-line">
        用纸 = 袋宽 ×（袋高 + 底风琴褶）× 2 × 折边系数
      </p>
      <p v-if="paperM2 != null" class="stat-line">
        估算用纸 <strong>{{ Number(paperM2).toFixed(4) }}</strong> m²
      </p>
    </template>

    <!-- 盒装：六面展开示意 -->
    <template v-else>
      <p class="unfold-title">盒体展开示意</p>
      <svg class="unfold-svg" viewBox="0 0 280 180" aria-hidden="true">
        <rect class="panel" x="95" y="18" width="90" height="42" rx="2" />
        <rect class="panel top" x="95" y="68" width="90" height="52" rx="2" />
        <rect class="panel" x="20" y="68" width="68" height="52" rx="2" />
        <rect class="panel" x="192" y="68" width="68" height="52" rx="2" />
        <rect class="panel" x="95" y="128" width="90" height="38" rx="2" />
        <text x="140" y="44" text-anchor="middle">顶 {{ num(l) }}×{{ num(w) }}</text>
        <text x="140" y="98" text-anchor="middle">正面</text>
        <text x="54" y="98" text-anchor="middle">侧</text>
        <text x="226" y="98" text-anchor="middle">侧</text>
        <text x="140" y="152" text-anchor="middle">h≈{{ num(h) }}</text>
      </svg>
      <p v-if="paperM2 != null" class="stat-line">
        估算用纸 <strong>{{ Number(paperM2).toFixed(4) }}</strong> m²（含折边系数）
      </p>
      <p v-else class="stat-line">
        外形 {{ num(l) }} × {{ num(w) }} × {{ num(h) }} m
      </p>
    </template>
  </div>
</template>

<style scoped>
.unfold-svg .panel.faint {
  fill: rgba(31, 92, 87, 0.06);
}
.unfold-svg .panel.gusset {
  fill: rgba(184, 151, 59, 0.16);
  stroke: var(--foil);
}
.gusset-fold {
  stroke: var(--foil);
  stroke-width: 1.4;
}
.fold {
  stroke: var(--ink-soft);
  stroke-width: 1;
}
</style>
