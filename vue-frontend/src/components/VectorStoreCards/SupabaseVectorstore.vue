<script setup lang="ts">
import { ref, computed } from 'vue'
import {SupabaseNamespace, GetSupabaseNamespacesResponse} from '../../services/vector_store/supabase_namespaces/types'

type SortKey = keyof Pick<
  SupabaseNamespace,
  'namespace' | 'model' | 'row_count' | 'updated_at' | 'created_at' | 'supabase_table_name'
>

const props = withDefaults(
  defineProps<{
    items: SupabaseNamespace[]
    /** show the search input above the table */
    searchable?: boolean
    /** initial column to sort by */
    initialSortKey?: SortKey
    /** initial sort direction */
    initialSortDir?: 'asc' | 'desc'
  }>(),
  {
    searchable: true,
    initialSortKey: 'namespace',
    initialSortDir: 'asc',
  }
)

const emit = defineEmits<{
  (e: 'select', item: SupabaseNamespace): void
}>()

const search = ref('')
const sortKey = ref<SortKey>(props.initialSortKey)
const sortDir = ref<'asc' | 'desc'>(props.initialSortDir)

function toggleSort(key: SortKey) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function formatDate(value: string) {
  const d = new Date(value)
  if (isNaN(d.getTime())) return value
  return d.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const filteredItems = computed(() => {
  const term = search.value.trim().toLowerCase()
  let list = props.items

  if (term) {
    list = list.filter((item) =>
      [
        item.namespace,
        item.model,
        item.supabase_table_name,
        item.additional_info,
      ]
        .join(' ')
        .toLowerCase()
        .includes(term)
    )
  }

  return [...list].sort((a, b) => {
    const av = a[sortKey.value]
    const bv = b[sortKey.value]

    let result = 0
    if (typeof av === 'number' && typeof bv === 'number') {
      result = av - bv
    } else {
      result = String(av).localeCompare(String(bv))
    }

    return sortDir.value === 'asc' ? result : -result
  })
})

const columns: { key: SortKey; label: string }[] = [
  { key: 'namespace', label: 'Namespace' },
  { key: 'model', label: 'Model' },
  { key: 'supabase_table_name', label: 'Table' },
  { key: 'row_count', label: 'Rows' },
  { key: 'updated_at', label: 'Updated' },
  { key: 'created_at', label: 'Created' },
]
</script>

<template>
  <div class="ns-table-wrap">
    <div v-if="searchable" class="ns-toolbar">
      <input
        v-model="search"
        type="text"
        class="ns-search"
        placeholder="Search namespace, model, table..."
      />
      <span class="ns-count">{{ filteredItems.length }} / {{ items.length }}</span>
    </div>

    <div class="ns-table-scroll">
      <table class="ns-table">
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              @click="toggleSort(col.key)"
              :class="{ active: sortKey === col.key }"
            >
              {{ col.label }}
              <span class="ns-sort-arrow" v-if="sortKey === col.key">
                {{ sortDir === 'asc' ? '▲' : '▼' }}
              </span>
            </th>
            <th class="ns-info-col">Additional Info</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in filteredItems"
            :key="item.namespace + item.supabase_table_name"
            @click="emit('select', item)"
          >
            <td class="ns-namespace">{{ item.namespace }}</td>
            <td>{{ item.model }}</td>
            <td><code>{{ item.supabase_table_name }}</code></td>
            <td class="ns-num">{{ item.row_count.toLocaleString() }}</td>
            <td>{{ formatDate(item.updated_at) }}</td>
            <td>{{ formatDate(item.created_at) }}</td>
            <td class="ns-info">{{ item.additional_info }}</td>
          </tr>
          <tr v-if="filteredItems.length === 0">
            <td :colspan="columns.length + 1" class="ns-empty">No namespaces found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.ns-table-wrap {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #1f2933;
  width: 100%;
}

.ns-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.ns-search {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d3dae0;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s ease;
}

.ns-search:focus {
  border-color: #3ecf8e;
}

.ns-count {
  font-size: 13px;
  color: #6b7785;
  white-space: nowrap;
}

.ns-table-scroll {
  overflow-x: auto;
  border: 1px solid #e4e9ed;
  border-radius: 8px;
}

.ns-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  min-width: 780px;
}

.ns-table thead th {
  text-align: left;
  padding: 10px 14px;
  background: #f8fafb;
  border-bottom: 1px solid #e4e9ed;
  font-weight: 600;
  color: #46525c;
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.ns-table thead th.active {
  color: #16794f;
}

.ns-table thead th.ns-info-col {
  cursor: default;
}

.ns-sort-arrow {
  font-size: 10px;
  margin-left: 4px;
}

.ns-table tbody tr {
  cursor: pointer;
  transition: background 0.1s ease;
}

.ns-table tbody tr:not(:last-child) {
  border-bottom: 1px solid #edf1f3;
}

.ns-table tbody tr:hover {
  background: #f4faf7;
}

.ns-table td {
  padding: 10px 14px;
  vertical-align: top;
}

.ns-namespace {
  font-weight: 600;
}

.ns-num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.ns-info {
  color: #5b6773;
  max-width: 280px;
  white-space: pre-wrap;
}

code {
  background: #f1f3f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12.5px;
}

.ns-empty {
  text-align: center;
  padding: 24px;
  color: #8b98a3;
}
</style>