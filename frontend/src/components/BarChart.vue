<script setup lang="ts">
import type { LabelCount } from '@/types/employee'
import { computed, ref } from 'vue'

const props = defineProps<{ data: LabelCount[] }>()

// Kategorial slot-1 ko'k (references/palette.md, dataviz skill) — bitta seriya, shu
// sabab barcha ustunlar bir xil rangda: uzunlik qiymatni, tartib (yosh/ta'lim darajasi
// kabi) esa qator ketma-ketligini allaqachon ifodalaydi, rangga qo'shimcha yuk tushmaydi.
const BAR_COLOR = '#2a78d6'

const hoverIndex = ref<number | null>(null)

const maxCount = computed(() => Math.max(1, ...props.data.map((d) => d.count)))

function barWidthPercent(count: number): number {
  return (count / maxCount.value) * 100
}
</script>

<template>
  <div class="space-y-1">
    <div
      v-for="(item, i) in props.data"
      :key="item.label"
      tabindex="0"
      class="flex items-center gap-2 rounded outline-none focus-visible:ring-2 focus-visible:ring-slate-300"
      @pointerenter="hoverIndex = i"
      @pointerleave="hoverIndex = null"
      @focus="hoverIndex = i"
      @blur="hoverIndex = null"
    >
      <div class="w-28 shrink-0 truncate text-right text-xs text-slate-500" :title="item.label">{{ item.label }}</div>
      <div class="h-5 flex-1 rounded-r bg-slate-100">
        <div
          class="h-5 rounded-r transition-[filter] duration-150"
          :style="{
            width: `${barWidthPercent(item.count)}%`,
            backgroundColor: BAR_COLOR,
            filter: hoverIndex === i ? 'brightness(1.15)' : 'none',
          }"
        />
      </div>
      <div class="w-8 shrink-0 text-right text-xs text-slate-600" style="font-variant-numeric: tabular-nums">
        {{ item.count }}
      </div>
    </div>
    <p v-if="!props.data.length" class="text-sm text-slate-400">Ma'lumot yo'q.</p>
  </div>
</template>
