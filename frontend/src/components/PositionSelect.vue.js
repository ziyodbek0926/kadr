import { createDepartment, createPosition, listDepartments, listPositions } from '@/api/departments';
import { onMounted, ref } from 'vue';
const modelValue = defineModel({ default: null });
const positions = ref([]);
const departments = ref([]);
const showAdd = ref(false);
const creatingDepartment = ref(false);
const newTitle = ref('');
const newDepartmentId = ref(null);
const newDepartmentName = ref('');
const saving = ref(false);
const error = ref('');
async function loadAll() {
    const [posList, depList] = await Promise.all([listPositions(), listDepartments()]);
    positions.value = posList;
    departments.value = depList;
}
onMounted(loadAll);
function resetAddForm() {
    showAdd.value = false;
    creatingDepartment.value = false;
    newTitle.value = '';
    newDepartmentId.value = null;
    newDepartmentName.value = '';
    error.value = '';
}
async function submitNewPosition() {
    error.value = '';
    if (!newTitle.value.trim()) {
        error.value = 'Lavozim nomini kiriting';
        return;
    }
    if (!creatingDepartment.value && !newDepartmentId.value) {
        error.value = "Bo'limni tanlang yoki yangi bo'lim qo'shing";
        return;
    }
    if (creatingDepartment.value && !newDepartmentName.value.trim()) {
        error.value = "Bo'lim nomini kiriting";
        return;
    }
    saving.value = true;
    try {
        let departmentId = newDepartmentId.value;
        if (creatingDepartment.value) {
            const dep = await createDepartment({ name: newDepartmentName.value.trim(), parent_id: null });
            departmentId = dep.id;
        }
        const position = await createPosition({
            title: newTitle.value.trim(),
            department_id: departmentId,
            category: null,
            is_vacant: true,
        });
        await loadAll();
        modelValue.value = position.id;
        resetAddForm();
    }
    catch {
        error.value = "Saqlashda xatolik yuz berdi";
    }
    finally {
        saving.value = false;
    }
}
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_defaults = {
    'modelValue': null,
};
const __VLS_modelEmit = defineEmits();
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.modelValue),
    ...{ class: "w-full rounded border px-2 py-1.5 text-sm" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: (null),
});
for (const [p] of __VLS_getVForSourceType((__VLS_ctx.positions))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        key: (p.id),
        value: (p.id),
    });
    (p.department.name);
    (p.title);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (...[$event]) => {
            __VLS_ctx.showAdd = !__VLS_ctx.showAdd;
        } },
    type: "button",
    ...{ class: "mt-1 text-xs text-blue-600 hover:underline" },
});
(__VLS_ctx.showAdd ? 'Bekor qilish' : "+ Ro'yxatda yo'q lavozimni qo'shish");
if (__VLS_ctx.showAdd) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "mt-2 space-y-2 rounded border bg-slate-50 p-3" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
        ...{ class: "mb-1 block text-xs text-slate-600" },
    });
    if (!__VLS_ctx.creatingDepartment) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
            value: (__VLS_ctx.newDepartmentId),
            ...{ class: "w-full rounded border px-2 py-1.5 text-sm" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
            value: (null),
        });
        for (const [d] of __VLS_getVForSourceType((__VLS_ctx.departments))) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
                key: (d.id),
                value: (d.id),
            });
            (d.name);
        }
    }
    else {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
            placeholder: "Yangi bo'lim nomi",
            ...{ class: "w-full rounded border px-2 py-1.5 text-sm" },
        });
        (__VLS_ctx.newDepartmentName);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.showAdd))
                    return;
                __VLS_ctx.creatingDepartment = !__VLS_ctx.creatingDepartment;
            } },
        type: "button",
        ...{ class: "mt-1 text-xs text-blue-600 hover:underline" },
    });
    (__VLS_ctx.creatingDepartment ? "Mavjud bo'limdan tanlash" : "+ Yangi bo'lim");
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
        ...{ class: "mb-1 block text-xs text-slate-600" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        placeholder: "masalan: Bosh mutaxassis",
        ...{ class: "w-full rounded border px-2 py-1.5 text-sm" },
    });
    (__VLS_ctx.newTitle);
    if (__VLS_ctx.error) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
            ...{ class: "text-xs text-red-600" },
        });
        (__VLS_ctx.error);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.submitNewPosition) },
        type: "button",
        disabled: (__VLS_ctx.saving),
        ...{ class: "rounded bg-slate-800 px-3 py-1 text-xs text-white disabled:opacity-50" },
    });
    (__VLS_ctx.saving ? 'Saqlanmoqda...' : "Qo'shish va tanlash");
}
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:underline']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-2']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['p-3']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-1']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:underline']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-1']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-600']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['disabled:opacity-50']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            modelValue: modelValue,
            positions: positions,
            departments: departments,
            showAdd: showAdd,
            creatingDepartment: creatingDepartment,
            newTitle: newTitle,
            newDepartmentId: newDepartmentId,
            newDepartmentName: newDepartmentName,
            saving: saving,
            error: error,
            submitNewPosition: submitNewPosition,
        };
    },
    __typeEmits: {},
    __typeProps: {},
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
    __typeEmits: {},
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
