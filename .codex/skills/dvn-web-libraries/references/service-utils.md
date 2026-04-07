# service-utils

`npm install @devonenergyenterprise/service-utils`

**Peer deps:** `@tanstack/react-query`, `react`, `axios`

## Hook Selection Guide

| Hook | Use When | Caching | Trigger |
|------|----------|---------|---------|
| `useServiceQuery` | Auto-fetch on mount | 24h staleTime | Automatic |
| `useServiceMutation` | POST/PUT/PATCH/DELETE | Invalidates others | Manual (`mutate()`) |
| `useOnDemandServiceQuery` | Search, parallel requests, cancellation | None | Manual (`mutateAsync()`) |

## Type Parameters (All Hooks)

- **`TData`** — Response data type
- **`TError`** — Error type (defaults to `void` / `DefaultError`)
- **`TVariables`** — Request payload type
- **`TContext`** — Mutation context type (mutations only)

## useServiceQuery

```typescript
import { useServiceQuery } from '@devonenergyenterprise/service-utils'

// Basic GET
const useGetUsers = () =>
  useServiceQuery<User[]>({
    queryKey: ['users'],
    path: '/api/users',
  })

// GET with parameters
const useGetActiveUsers = () =>
  useServiceQuery<User[]>({
    queryKey: ['users', 'active'],
    path: '/api/users',
    params: { status: 'active', limit: 50 },
  })

// POST query (complex search)
const useSearchUsers = (criteria: SearchCriteria) =>
  useServiceQuery<User[]>({
    queryKey: ['users', 'search', criteria],
    path: '/api/users/search',
    params: criteria,
    config: { method: 'post' },
  })

// Conditional query
const useGetUser = (id: number | null) =>
  useServiceQuery<User>({
    queryKey: ['user', id],
    path: `/api/users/${id}`,
    enabled: id !== null,
  })

// Custom stale time
const useGetProfile = (userId: number) =>
  useServiceQuery<User>({
    queryKey: ['user', userId],
    path: `/api/users/${userId}`,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
```

**Options:** `queryKey`, `path`, `params`, `enabled`, `staleTime` (default 24h), `config.method`, `options.dependentQueryKeys`, `options.extractODataValue`

### OData Handling

`useServiceQuery` **auto-extracts** the `value` array from OData responses by default.

```typescript
// API returns: { "@odata.context": "...", "value": [...] }
const useGetUsers = () =>
  useServiceQuery<User[]>({
    queryKey: ['odata-users'],
    path: '/odata/Users',
  })
// data is User[], not ODataResponse<User>

// To access full OData metadata (count, nextLink):
const useGetUsersWithMeta = () =>
  useServiceQuery<ODataResponse<User>>({
    queryKey: ['odata-users-full'],
    path: '/odata/Users',
    params: { $count: true, $top: 20 },
    options: { extractODataValue: false },
  })
// data['@odata.count'], data['@odata.nextLink'], data.value
```

## useServiceMutation

```typescript
import { useServiceMutation } from '@devonenergyenterprise/service-utils'

// Basic POST
const useSaveItem = () =>
  useServiceMutation<void, void, NewItem>('/MyStuff')

// Specific HTTP method
const useUpdateItem = () =>
  useServiceMutation<void, void, NewItem>('/MyStuff', { method: 'put' })

const useDeleteItem = () =>
  useServiceMutation<void, void, NewItem>('/MyStuff', { method: 'delete' })

// Invalidate queries on success
const useSaveItem = () =>
  useServiceMutation<void, void, NewItem>('/MyStuff', {
    dependentQueryKeys: [['a query key'], ['another', 'query key']],
  })

// Dynamic URL from variables
const useSaveItem = () =>
  useServiceMutation<void, void, NewItem>(
    (params) => `/MyStuff/${params.id}`,
  )

// Dynamic URL + extractParams (filter what's sent to API)
const useSaveItem = () =>
  useServiceMutation<void, void, NewItem>(
    (params) => `/MyStuff/${params.id}`,
    { extractParams: (params) => _.pick(params, 'prop1', 'prop2') },
  )

// Custom callbacks
const useSaveItem = () =>
  useServiceMutation<void, void, NewItem>('/MyStuff', {
    onError: ({ variables: { id } }) => console.error(`Failed for id: ${id}`),
    onSuccess: ({ variables: { id } }) => console.log(`Saved id: ${id}`),
  })

// Reusable hook with injected callbacks
const useSaveItem = ({ onError, onSuccess }: { onError: OnErrorFunction; onSuccess: OnSuccessFunction }) =>
  useServiceMutation<void, void, NewItem>('/MyStuff', { onError, onSuccess })
```

**Options:** `method` (post/put/patch/delete), `dependentQueryKeys`, `refetchQueryKeys`, `extractParams`, `errorMessage`, `onSuccess`, `onError`, `onSettled`

## useOnDemandServiceQuery

```typescript
import { useOnDemandServiceQuery } from '@devonenergyenterprise/service-utils'

// Basic on-demand GET
const useGetStuff = ({ onSuccess }) =>
  useOnDemandServiceQuery<MyStuff[], void, string>(
    (typeId) => `/MyStuff/${typeId}`,
    { method: 'get', onSuccess },
  )

// Usage: const { mutateAsync: getStuff } = useGetStuff({ onSuccess: ... })
// getStuff('aTypeId')

// With request cancellation
const useSearchStuff = () =>
  useOnDemandServiceQuery<MyStuff[], void, SearchParams>(
    '/MyStuff/search',
    {
      method: 'post',
      onError: ({ error }) => {
        if (!axios.isCancel(error)) console.error('Search failed')
      },
    },
  )

// Usage with AbortSignal:
const controller = new AbortController()
searchStuff({ query: 'test', $meta: { signal: controller.signal } })
controller.abort() // Cancel if needed
```

### $meta — Client-Side Metadata (Not Sent to API)

```typescript
// Dynamic URL routing
mutateAsync({ query: 'test', $meta: { version: 'v2' } })
// In hook: (params) => `/api/${params.$meta?.version || 'v1'}/search`

// Conditional callback behavior
mutateAsync({ id: 1, data: myData, $meta: { silent: true, source: 'autosave' } })
// In onSuccess: if (!variables.$meta?.silent) showToast(...)

// UI state coordination
mutateAsync({ itemId: 1, $meta: { fromBulkAction: true, itemName: 'Report' } })
// In onSuccess: skip individual toasts during bulk operations
```

**Options:** `method` (get/post), `dependentQueryKeys`, `refetchQueryKeys`, `errorMessage`, `onSuccess`, `onError`, `config` (Axios config)

## Types

```typescript
import type {
  ODataResponse,
  ErrorResponse,
  OnSuccessFunction,
  OnErrorFunction,
  OnSettledFunction,
  RequestMeta,
} from '@devonenergyenterprise/service-utils'
```

## Common Pattern: Hook Factory with Toast

```typescript
export const useUpdateItem = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  return useServiceMutation<Item, Error, UpdateParams>(
    (p) => `/api/items/${p.id}`,
    {
      method: 'put',
      dependentQueryKeys: [['items']],
      onSuccess: () => showSuccessToast('Item updated'),
      onError: () => showErrorToast('Update failed'),
    },
  )
}
```

## Common Pattern: Date Field Round-Trip

```typescript
// API → Form
const formData = deserializeDates(apiData, ['createdAt', 'dueDate'])

// Form → API
const payload = serializeDates(formData, ['createdAt', 'dueDate'])
mutation.mutate(payload)
```
