# Cross-Module Patterns

## AG Grid + core-utils: Date Column

```typescript
import { formatDate, startOfDayComparator } from '@devonenergyenterprise/core-utils'
import { defaultAgDateColumnFilter, Cell } from '@devonenergyenterprise/ag-grid-presets'

{
  field: 'createdAt',
  headerName: 'Created',
  valueFormatter: (p) => formatDate(p.value),
  cellRenderer: (p) => <Cell>{formatDate(p.value)}</Cell>,
  ...defaultAgDateColumnFilter,
}
```

## AG Grid + ui-react: Truncated Cell with Tooltip

```typescript
import { Tooltip } from '@devonenergyenterprise/ui-react'
import { ellipsize } from '@devonenergyenterprise/core-utils'
import { Cell } from '@devonenergyenterprise/ag-grid-presets'

{
  field: 'description',
  cellRenderer: (p) => (
    <Cell>
      <Tooltip content={p.value} disabled={p.value?.length <= 30}>
        <Text>{ellipsize(p.value, 30)}</Text>
      </Tooltip>
    </Cell>
  ),
}
```

## service-utils + core-utils: Search with Filtering

```typescript
import { filterBySearch, formatDate } from '@devonenergyenterprise/core-utils'

const { data: items } = useGetItems()
const filtered = filterBySearch(searchTerm, items ?? [], [
  item => item.name,
  item => item.description,
  item => formatDate(item.createdAt),
])
```

## Full Grid Setup: Query + Grid + Loading

```typescript
const UsersGrid = () => {
  const isGridReady = useGridReady()
  const { data: users, isLoading } = useGetUsers() // service-utils
  const [selected, setSelected] = useState<User[]>([])

  const availableColumns = {
    name: { field: 'name', headerName: 'Name', ...defaultAgTextColumnFilter },
    status: { field: 'status', headerName: 'Status', ...defaultSetColumnFilter },
    createdAt: {
      field: 'createdAt',
      valueFormatter: (p) => formatDate(p.value), // core-utils
      ...defaultAgDateColumnFilter,
    },
  }

  const gridProps = useGridDefaults({
    availableColumns,
    columns: ['name', 'status', 'createdAt'],
    gridId: 'users-grid',
    onTextClicked: (user) => navigate(`/users/${user.id}`),
    managedEventExtensions: {
      onSelectionChanged: (e) => setSelected(e.api.getSelectedRows()),
    },
  })

  return (
    <Box sx={gridCss} height="600px">
      <GridLoader loading={isLoading || !isGridReady} transitionDelay={300}>
        <AgGridReact {...gridProps} rowData={users} />
      </GridLoader>
    </Box>
  )
}
```
