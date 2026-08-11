import { createDepartment, createPosition, deleteDepartment, deletePosition, listDepartments, listPositions, updateDepartment, updatePosition, } from '@/api/departments';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';
import { computed, onMounted, ref } from 'vue';
const auth = useAuthStore();
const canEdit = computed(() => auth.canEdit);
const departments = ref([]);
const positions = ref([]);
const loading = ref(true);
const error = ref('');
function extractError(e) {
    if (axios.isAxiosError(e) && typeof e.response?.data?.detail === 'string') {
        return e.response.data.detail;
    }
    return 'Amalni bajarishda xatolik yuz berdi';
}
async function loadAll() {
    const [depList, posList] = await Promise.all([listDepartments(), listPositions()]);
    departments.value = depList;
    positions.value = posList;
}
onMounted(async () => {
    loading.value = true;
    try {
        await loadAll();
    }
    finally {
        loading.value = false;
    }
});
const departmentRows = computed(() => {
    const byParent = new Map();
    for (const d of departments.value) {
        const key = d.parent_id;
        if (!byParent.has(key))
            byParent.set(key, []);
        byParent.get(key).push(d);
    }
    const rows = [];
    function walk(parentId, depth) {
        for (const child of byParent.get(parentId) ?? []) {
            rows.push({ dept: child, depth });
            walk(child.id, depth + 1);
        }
    }
    walk(null, 0);
    // Ehtiyot chorasi: agar parent_id ro'yxatda yo'q bo'lsa (odatiy holatda bo'lmasligi kerak), baribir ko'rsatiladi
    const visited = new Set(rows.map((r) => r.dept.id));
    for (const d of departments.value) {
        if (!visited.has(d.id))
            rows.push({ dept: d, depth: 0 });
    }
    return rows;
});
const positionsByDept = computed(() => {
    const map = new Map();
    for (const p of positions.value) {
        if (!map.has(p.department_id))
            map.set(p.department_id, []);
        map.get(p.department_id).push(p);
    }
    return map;
});
// ---- Bo'lim qo'shish ----
const showAddDept = ref(false);
const newDeptName = ref('');
const newDeptParentId = ref(null);
async function submitNewDept() {
    error.value = '';
    if (!newDeptName.value.trim()) {
        error.value = "Bo'lim nomini kiriting";
        return;
    }
    try {
        await createDepartment({ name: newDeptName.value.trim(), parent_id: newDeptParentId.value });
        newDeptName.value = '';
        newDeptParentId.value = null;
        showAddDept.value = false;
        await loadAll();
    }
    catch (e) {
        error.value = extractError(e);
    }
}
// ---- Bo'limni tahrirlash/o'chirish ----
const editingDeptId = ref(null);
const editDeptForm = ref({ name: '', parent_id: null });
function startEditDept(dept) {
    editingDeptId.value = dept.id;
    editDeptForm.value = { name: dept.name, parent_id: dept.parent_id };
    error.value = '';
}
async function saveEditDept(deptId) {
    error.value = '';
    if (!editDeptForm.value.name.trim()) {
        error.value = "Bo'lim nomini kiriting";
        return;
    }
    try {
        await updateDepartment(deptId, editDeptForm.value);
        editingDeptId.value = null;
        await loadAll();
    }
    catch (e) {
        error.value = extractError(e);
    }
}
async function removeDept(dept) {
    if (!confirm(`"${dept.name}" bo'limini o'chirishni tasdiqlaysizmi?`))
        return;
    error.value = '';
    try {
        await deleteDepartment(dept.id);
        await loadAll();
    }
    catch (e) {
        error.value = extractError(e);
    }
}
// ---- Lavozim qo'shish ----
const addPositionForDept = ref(null);
const newPositionTitle = ref('');
const newPositionCategory = ref('');
function toggleAddPosition(departmentId) {
    addPositionForDept.value = addPositionForDept.value === departmentId ? null : departmentId;
    newPositionTitle.value = '';
    newPositionCategory.value = '';
    error.value = '';
}
async function submitNewPosition(departmentId) {
    error.value = '';
    if (!newPositionTitle.value.trim()) {
        error.value = "Lavozim nomini kiriting";
        return;
    }
    try {
        await createPosition({
            title: newPositionTitle.value.trim(),
            department_id: departmentId,
            category: newPositionCategory.value.trim() || null,
            is_vacant: true,
        });
        addPositionForDept.value = null;
        await loadAll();
    }
    catch (e) {
        error.value = extractError(e);
    }
}
// ---- Lavozimni tahrirlash/o'chirish ----
const editingPositionId = ref(null);
const editPositionForm = ref({
    title: '',
    department_id: 0,
    category: null,
    is_vacant: true,
});
function startEditPosition(p) {
    editingPositionId.value = p.id;
    editPositionForm.value = {
        title: p.title,
        department_id: p.department_id,
        category: p.category,
        is_vacant: p.is_vacant,
    };
    error.value = '';
}
async function saveEditPosition(id) {
    error.value = '';
    if (!editPositionForm.value.title.trim()) {
        error.value = "Lavozim nomini kiriting";
        return;
    }
    try {
        await updatePosition(id, editPositionForm.value);
        editingPositionId.value = null;
        await loadAll();
    }
    catch (e) {
        error.value = extractError(e);
    }
}
async function removePosition(p) {
    if (!confirm(`"${p.title}" lavozimini o'chirishni tasdiqlaysizmi?`))
        return;
    error.value = '';
    try {
        await deletePosition(p.id);
        await loadAll();
    }
    catch (e) {
        error.value = extractError(e);
    }
}
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "mx-auto max-w-4xl p-6" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "mb-4 flex items-center justify-between" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({
    ...{ class: "text-2xl font-semibold text-slate-800" },
});
if (__VLS_ctx.canEdit) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.canEdit))
                    return;
                __VLS_ctx.showAddDept = !__VLS_ctx.showAddDept;
            } },
        ...{ class: "rounded bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700" },
    });
    (__VLS_ctx.showAddDept ? 'Bekor qilish' : "+ Yangi bo'lim");
}
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-600" },
    });
    (__VLS_ctx.error);
}
if (__VLS_ctx.showAddDept) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.form, __VLS_intrinsicElements.form)({
        ...{ onSubmit: (__VLS_ctx.submitNewDept) },
        ...{ class: "mb-6 grid grid-cols-1 gap-3 rounded-lg border bg-slate-50 p-4 sm:grid-cols-3" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sm:col-span-2" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
        ...{ class: "mb-1 block text-xs text-slate-600" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        required: true,
        ...{ class: "w-full rounded border px-2 py-1.5 text-sm" },
    });
    (__VLS_ctx.newDeptName);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
        ...{ class: "mb-1 block text-xs text-slate-600" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
        value: (__VLS_ctx.newDeptParentId),
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
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "sm:col-span-3" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        type: "submit",
        ...{ class: "rounded bg-slate-800 px-4 py-1.5 text-sm text-white" },
    });
}
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "space-y-4" },
    });
    for (const [row] of __VLS_getVForSourceType((__VLS_ctx.departmentRows))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            key: (row.dept.id),
            ...{ class: "rounded-lg bg-white p-4 shadow" },
            ...{ style: ({ marginLeft: `${row.depth * 20}px` }) },
        });
        if (__VLS_ctx.editingDeptId === row.dept.id) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                ...{ class: "grid grid-cols-1 gap-2 sm:grid-cols-3" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
                ...{ class: "rounded border px-2 py-1.5 text-sm sm:col-span-2" },
            });
            (__VLS_ctx.editDeptForm.name);
            __VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
                value: (__VLS_ctx.editDeptForm.parent_id),
                ...{ class: "rounded border px-2 py-1.5 text-sm" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
                value: (null),
            });
            for (const [d] of __VLS_getVForSourceType((__VLS_ctx.departments))) {
                __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
                    key: (d.id),
                    value: (d.id),
                    disabled: (d.id === row.dept.id),
                });
                (d.name);
            }
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                ...{ class: "flex gap-2 sm:col-span-3" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                ...{ onClick: (...[$event]) => {
                        if (!!(__VLS_ctx.loading))
                            return;
                        if (!(__VLS_ctx.editingDeptId === row.dept.id))
                            return;
                        __VLS_ctx.saveEditDept(row.dept.id);
                    } },
                ...{ class: "rounded bg-slate-800 px-3 py-1 text-xs text-white" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                ...{ onClick: (...[$event]) => {
                        if (!!(__VLS_ctx.loading))
                            return;
                        if (!(__VLS_ctx.editingDeptId === row.dept.id))
                            return;
                        __VLS_ctx.editingDeptId = null;
                    } },
                ...{ class: "rounded border px-3 py-1 text-xs" },
            });
        }
        else {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                ...{ class: "flex items-center justify-between" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({
                ...{ class: "font-semibold text-slate-800" },
            });
            (row.dept.name);
            if (__VLS_ctx.canEdit) {
                __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                    ...{ class: "flex gap-3 text-sm" },
                });
                __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                    ...{ onClick: (...[$event]) => {
                            if (!!(__VLS_ctx.loading))
                                return;
                            if (!!(__VLS_ctx.editingDeptId === row.dept.id))
                                return;
                            if (!(__VLS_ctx.canEdit))
                                return;
                            __VLS_ctx.startEditDept(row.dept);
                        } },
                    ...{ class: "text-blue-600 hover:underline" },
                });
                __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                    ...{ onClick: (...[$event]) => {
                            if (!!(__VLS_ctx.loading))
                                return;
                            if (!!(__VLS_ctx.editingDeptId === row.dept.id))
                                return;
                            if (!(__VLS_ctx.canEdit))
                                return;
                            __VLS_ctx.removeDept(row.dept);
                        } },
                    ...{ class: "text-red-600 hover:underline" },
                });
            }
        }
        if (__VLS_ctx.positionsByDept.get(row.dept.id)?.length) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.table, __VLS_intrinsicElements.table)({
                ...{ class: "mt-3 w-full text-sm" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.thead, __VLS_intrinsicElements.thead)({});
            __VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({
                ...{ class: "border-b text-left text-slate-500" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({
                ...{ class: "p-2" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({
                ...{ class: "p-2" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({
                ...{ class: "p-2" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({
                ...{ class: "p-2" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.tbody, __VLS_intrinsicElements.tbody)({});
            for (const [p] of __VLS_getVForSourceType((__VLS_ctx.positionsByDept.get(row.dept.id)))) {
                __VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({
                    key: (p.id),
                    ...{ class: "border-b" },
                });
                if (__VLS_ctx.editingPositionId === p.id) {
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({
                        ...{ class: "p-2" },
                        colspan: "4",
                    });
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                        ...{ class: "grid grid-cols-1 gap-2 sm:grid-cols-4" },
                    });
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
                        ...{ class: "rounded border px-2 py-1 text-sm sm:col-span-2" },
                    });
                    (__VLS_ctx.editPositionForm.title);
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
                        placeholder: "Toifa",
                        ...{ class: "rounded border px-2 py-1 text-sm" },
                    });
                    (__VLS_ctx.editPositionForm.category);
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
                        ...{ class: "flex items-center gap-1 text-xs text-slate-600" },
                    });
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
                        type: "checkbox",
                    });
                    (__VLS_ctx.editPositionForm.is_vacant);
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                        ...{ class: "flex gap-2 sm:col-span-4" },
                    });
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                        ...{ onClick: (...[$event]) => {
                                if (!!(__VLS_ctx.loading))
                                    return;
                                if (!(__VLS_ctx.positionsByDept.get(row.dept.id)?.length))
                                    return;
                                if (!(__VLS_ctx.editingPositionId === p.id))
                                    return;
                                __VLS_ctx.saveEditPosition(p.id);
                            } },
                        ...{ class: "rounded bg-slate-800 px-3 py-1 text-xs text-white" },
                    });
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                        ...{ onClick: (...[$event]) => {
                                if (!!(__VLS_ctx.loading))
                                    return;
                                if (!(__VLS_ctx.positionsByDept.get(row.dept.id)?.length))
                                    return;
                                if (!(__VLS_ctx.editingPositionId === p.id))
                                    return;
                                __VLS_ctx.editingPositionId = null;
                            } },
                        ...{ class: "rounded border px-3 py-1 text-xs" },
                    });
                }
                else {
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({
                        ...{ class: "p-2" },
                    });
                    (p.title);
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({
                        ...{ class: "p-2" },
                    });
                    (p.category ?? '—');
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({
                        ...{ class: "p-2" },
                    });
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                        ...{ class: "rounded px-2 py-0.5 text-xs" },
                        ...{ class: (p.is_vacant ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700') },
                    });
                    (p.is_vacant ? "Bo'sh" : 'Band');
                    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({
                        ...{ class: "p-2 text-right" },
                    });
                    if (__VLS_ctx.canEdit) {
                        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                            ...{ class: "flex justify-end gap-3" },
                        });
                        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                            ...{ onClick: (...[$event]) => {
                                    if (!!(__VLS_ctx.loading))
                                        return;
                                    if (!(__VLS_ctx.positionsByDept.get(row.dept.id)?.length))
                                        return;
                                    if (!!(__VLS_ctx.editingPositionId === p.id))
                                        return;
                                    if (!(__VLS_ctx.canEdit))
                                        return;
                                    __VLS_ctx.startEditPosition(p);
                                } },
                            ...{ class: "text-blue-600 hover:underline" },
                        });
                        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                            ...{ onClick: (...[$event]) => {
                                    if (!!(__VLS_ctx.loading))
                                        return;
                                    if (!(__VLS_ctx.positionsByDept.get(row.dept.id)?.length))
                                        return;
                                    if (!!(__VLS_ctx.editingPositionId === p.id))
                                        return;
                                    if (!(__VLS_ctx.canEdit))
                                        return;
                                    __VLS_ctx.removePosition(p);
                                } },
                            ...{ class: "text-red-600 hover:underline" },
                        });
                    }
                }
            }
        }
        else {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
                ...{ class: "mt-3 text-sm text-slate-400" },
            });
        }
        if (__VLS_ctx.canEdit) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                ...{ class: "mt-3" },
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                ...{ onClick: (...[$event]) => {
                        if (!!(__VLS_ctx.loading))
                            return;
                        if (!(__VLS_ctx.canEdit))
                            return;
                        __VLS_ctx.toggleAddPosition(row.dept.id);
                    } },
                ...{ class: "text-sm text-blue-600 hover:underline" },
            });
            (__VLS_ctx.addPositionForDept === row.dept.id ? 'Bekor qilish' : '+ Yangi lavozim');
            if (__VLS_ctx.addPositionForDept === row.dept.id) {
                __VLS_asFunctionalElement(__VLS_intrinsicElements.form, __VLS_intrinsicElements.form)({
                    ...{ onSubmit: (...[$event]) => {
                            if (!!(__VLS_ctx.loading))
                                return;
                            if (!(__VLS_ctx.canEdit))
                                return;
                            if (!(__VLS_ctx.addPositionForDept === row.dept.id))
                                return;
                            __VLS_ctx.submitNewPosition(row.dept.id);
                        } },
                    ...{ class: "mt-2 grid grid-cols-1 gap-2 rounded border bg-slate-50 p-3 sm:grid-cols-3" },
                });
                __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
                    placeholder: "Lavozim nomi",
                    required: true,
                    ...{ class: "rounded border px-2 py-1.5 text-sm" },
                });
                (__VLS_ctx.newPositionTitle);
                __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
                    placeholder: "Toifa (ixtiyoriy)",
                    ...{ class: "rounded border px-2 py-1.5 text-sm" },
                });
                (__VLS_ctx.newPositionCategory);
                __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
                    type: "submit",
                    ...{ class: "rounded bg-slate-800 px-3 py-1.5 text-sm text-white" },
                });
            }
        }
    }
    if (!__VLS_ctx.departmentRows.length) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
            ...{ class: "text-sm text-slate-400" },
        });
    }
}
/** @type {__VLS_StyleScopedClasses['mx-auto']} */ ;
/** @type {__VLS_StyleScopedClasses['max-w-4xl']} */ ;
/** @type {__VLS_StyleScopedClasses['p-6']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['text-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-slate-700']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-red-200']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-red-50']} */ ;
/** @type {__VLS_StyleScopedClasses['p-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-600']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-6']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-1']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['p-4']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:grid-cols-3']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:col-span-2']} */ ;
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
/** @type {__VLS_StyleScopedClasses['sm:col-span-3']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['px-4']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['space-y-4']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['p-4']} */ ;
/** @type {__VLS_StyleScopedClasses['shadow']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-1']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:grid-cols-3']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:col-span-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:col-span-3']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:underline']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:underline']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-3']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b']} */ ;
/** @type {__VLS_StyleScopedClasses['text-left']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
/** @type {__VLS_StyleScopedClasses['p-2']} */ ;
/** @type {__VLS_StyleScopedClasses['p-2']} */ ;
/** @type {__VLS_StyleScopedClasses['p-2']} */ ;
/** @type {__VLS_StyleScopedClasses['p-2']} */ ;
/** @type {__VLS_StyleScopedClasses['border-b']} */ ;
/** @type {__VLS_StyleScopedClasses['p-2']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-1']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:grid-cols-4']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:col-span-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:col-span-4']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['p-2']} */ ;
/** @type {__VLS_StyleScopedClasses['p-2']} */ ;
/** @type {__VLS_StyleScopedClasses['p-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-0.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
/** @type {__VLS_StyleScopedClasses['p-2']} */ ;
/** @type {__VLS_StyleScopedClasses['text-right']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-end']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:underline']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:underline']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-3']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-blue-600']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:underline']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-2']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-1']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-50']} */ ;
/** @type {__VLS_StyleScopedClasses['p-3']} */ ;
/** @type {__VLS_StyleScopedClasses['sm:grid-cols-3']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['px-2']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-slate-800']} */ ;
/** @type {__VLS_StyleScopedClasses['px-3']} */ ;
/** @type {__VLS_StyleScopedClasses['py-1.5']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-400']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            canEdit: canEdit,
            departments: departments,
            loading: loading,
            error: error,
            departmentRows: departmentRows,
            positionsByDept: positionsByDept,
            showAddDept: showAddDept,
            newDeptName: newDeptName,
            newDeptParentId: newDeptParentId,
            submitNewDept: submitNewDept,
            editingDeptId: editingDeptId,
            editDeptForm: editDeptForm,
            startEditDept: startEditDept,
            saveEditDept: saveEditDept,
            removeDept: removeDept,
            addPositionForDept: addPositionForDept,
            newPositionTitle: newPositionTitle,
            newPositionCategory: newPositionCategory,
            toggleAddPosition: toggleAddPosition,
            submitNewPosition: submitNewPosition,
            editingPositionId: editingPositionId,
            editPositionForm: editPositionForm,
            startEditPosition: startEditPosition,
            saveEditPosition: saveEditPosition,
            removePosition: removePosition,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
