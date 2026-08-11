import { computed, ref } from 'vue';
const props = defineProps();
// Kategorial slot-1 ko'k (references/palette.md, dataviz skill) — bitta seriya, shu
// sabab barcha ustunlar bir xil rangda: uzunlik qiymatni, tartib (yosh/ta'lim darajasi
// kabi) esa qator ketma-ketligini allaqachon ifodalaydi, rangga qo'shimcha yuk tushmaydi.
const BAR_COLOR = '#2a78d6';
const hoverIndex = ref(null);
const maxCount = computed(() => Math.max(1, ...props.data.map((d) => d.count)));
function barWidthPercent(count) {
    return (count / maxCount.value) * 100;
}
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "space-y-1" },
});
for (const [item, i] of __VLS_getVForSourceType((props.data))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ onPointerenter: (...[$event]) => {
                __VLS_ctx.hoverIndex = i;
            } },
        ...{ onPointerleave: (...[$event]) => {
                __VLS_ctx.hoverIndex = null;
            } },
        ...{ onFocus: (...[$event]) => {
                __VLS_ctx.hoverIndex = i;
            } },
        ...{ onBlur: (...[$event]) => {
                __VLS_ctx.hoverIndex = null;
            } },
        key: (item.label),
        tabindex: "0",
        ...{ class: "flex items-center gap-2 rounded outline-none focus-visible:ring-2 focus-visible:ring-slate-300" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "w-28 shrink-0 truncate text-right text-xs text-slate-500" },
        title: (item.label),
    });
    (item.label);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "h-5 flex-1 rounded-r bg-slate-100" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div)({
        ...{ class: "h-5 rounded-r transition-[filter] duration-150" },
        ...{ style: ({
                width: `${__VLS_ctx.barWidthPercent(item.count)}%`,
                backgroundColor: __VLS_ctx.BAR_COLOR,
                filter: __VLS_ctx.hoverIndex === i ? 'brightness(1.15)' : 'none',
            }) },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "w-8 shrink-0 text-right text-xs text-slate-600" },
        ...{ style: {} },
    });
    (item.count);
}
if (!props.data.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "text-sm text-slate-400" },
    });
}
/** @type {__VLS_StyleScopedClasses['space-y-1']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['outline-none']} */ ;
/** @type {__VLS_StyleScopedClasses['focus-visible:ring-2']} */ ;
/** @type {__VLS_StyleScopedClasses['focus-visible:ring-slate-300']} */ ;
/** @type {__VLS_StyleScopedClasses['w-28']} */ ;
/** @type {__VLS_StyleScopedClasses['shrink-0']} */ ;
/** @type {__VLS_StyleScopedClasses['truncate']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['h-5']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-1']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-r']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-100']} */ ;
/** @type {__VLS_StyleScopedClasses['h-5']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-r']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-[filter]']} */ ;
/** @type {__VLS_StyleScopedClasses['duration-150']} */ ;
/** @type {__VLS_StyleScopedClasses['w-8']} */ ;
/** @type {__VLS_StyleScopedClasses['shrink-0']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            BAR_COLOR: BAR_COLOR,
            hoverIndex: hoverIndex,
            barWidthPercent: barWidthPercent,
        };
    },
    __typeProps: {},
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
