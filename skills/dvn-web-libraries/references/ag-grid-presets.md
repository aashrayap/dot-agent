# ag-grid-presets

`npm install @devonenergyenterprise/ag-grid-presets`

**Peer deps:** `ag-grid-community`, `ag-grid-enterprise`, `ag-grid-react`, `@chakra-ui/react`, `@emotion/react`, `react`

## Required Semantic Tokens

Your Chakra UI theme **must** define these tokens:

```typescript
const config = defineConfig({
  theme: {
    semanticTokens: {
      colors: {
        gridBackgroundColor: {
          value: { base: '{colors.white}', _dark: '{colors.gray.800}' },
        },
        gridBorderBottomColor: {
          value: { base: '{colors.gray.200}', _dark: '{colors.gray.700}' },
        },
        gridSelectedColor: {
          value: { base: '{colors.blue.50}', _dark: '{colors.blue.900}' },
        },
        innerCardHoverBg: {
          value: { base: '{colors.gray.50}', _dark: '{colors.gray.750}' },
        },
        bodyText: {
          value: { base: '{colors.gray.900}', _dark: '{colors.gray.100}' },
        },
      },
    },
  },
})
```

| Token | Purpose |
|-------|---------|
| `gridBackgroundColor` | Cell/header background |
| `gridBorderBottomColor` | Row/header borders |
| `gridSelectedColor` | Selected row background |
| `innerCardHoverBg` | Row hover background |
| `bodyText` | Cell/header text color |

## useGridDefaults

Primary hook — configures AG Grid with Devon Energy defaults.

**Included automatically:**
- Column state persistence (filters, order, pin, sort, visibility, width)
- Chakra UI theme with light/dark mode
- Multi-row selection with checkboxes
- Status bar (selected/filtered/total counts)
- Smart cell click detection
- Row buffer of 50
- Intelligent set filter persistence

```typescript
import { useGridDefaults, gridCss, defaultAgDateColumnFilter, defaultAgTextColumnFilter, defaultSetColumnFilter } from '@devonenergyenterprise/ag-grid-presets'
import { AgGridReact } from 'ag-grid-react'

const UsersGrid = () => {
  const { data: users } = useGetUsers()

  const availableColumns = {
    name: { field: 'name', headerName: 'Name', ...defaultAgTextColumnFilter },
    email: { field: 'email', headerName: 'Email', ...defaultAgTextColumnFilter },
    status: { field: 'status', headerName: 'Status', ...defaultSetColumnFilter },
    createdAt: {
      field: 'createdAt',
      headerName: 'Created',
      valueFormatter: (p) => formatDate(p.value),
      ...defaultAgDateColumnFilter,
    },
  }

  const gridProps = useGridDefaults({
    availableColumns,
    columns: ['name', 'email', 'status', 'createdAt'],
    gridId: 'users-grid',
    onTextClicked: (user) => navigate(`/users/${user.id}`),
  })

  return (
    <Box sx={gridCss} height="600px">
      <AgGridReact {...gridProps} rowData={users} />
    </Box>
  )
}
```

### Column Definitions — Mix Strings and ColDefs

```typescript
const gridProps = useGridDefaults({
  availableColumns,
  columns: [
    'name',
    'email',
    { field: 'status', pinned: 'right', width: 120 },
  ],
  gridId: 'users-grid',
  onTextClicked: (user) => console.log(user),
})
```

### Event Extensions

```typescript
const gridProps = useGridDefaults({
  managedEventExtensions: {
    onSelectionChanged: (event) => setSelectedItems(event.api.getSelectedRows()),
    onColumnResized: (event) => console.log('Resized:', event.column.getColId()),
  },
})
```

**Available extensions:** `onCellClicked`, `onColumnMoved`, `onColumnPinned`, `onColumnResized`, `onColumnVisible`, `onColumnsReset`, `onSelectionChanged`, `onSortChanged`

### Override Defaults

```typescript
const gridProps = useGridDefaults({
  rowHeight: 50,
  pagination: true,
  paginationPageSize: 20,
  rowSelection: { mode: 'singleRow' },
})
```

### onCellClicked Override

Passing `onCellClicked` directly (or via `managedEventExtensions`) **completely bypasses** `onTextClicked` text detection.

## useGridReady

```typescript
import { useGridReady } from '@devonenergyenterprise/ag-grid-presets'

const isGridReady = useGridReady()

<GridLoader loading={isLoading || !isGridReady}>
  <AgGridReact {...gridProps} rowData={data} />
</GridLoader>
```

## GridLoader

```typescript
import { GridLoader } from '@devonenergyenterprise/ag-grid-presets'

<GridLoader loading={isLoading}>
  <AgGridReact {...gridProps} rowData={data} />
</GridLoader>

<GridLoader columns={8} rows={10} hideRowSelector loading={isLoading} transitionDelay={300}>
  <AgGridReact {...gridProps} rowData={data} />
</GridLoader>
```

**Props:** `children`, `loading`, `columns?` (default 5), `rows?` (default 5), `hideRowSelector?`, `transitionDelay?`

## Cell

```typescript
import { Cell } from '@devonenergyenterprise/ag-grid-presets'

{ cellRenderer: (params) => <Cell>{params.value}</Cell> }

{ cellRenderer: (params) => (
  <Cell>
    <HStack spacing={2}>
      <CheckIcon color="green.500" />
      <Text>{params.value}</Text>
    </HStack>
  </Cell>
)}
```

## gridCss

```typescript
import { gridCss } from '@devonenergyenterprise/ag-grid-presets'

<Box sx={gridCss} height="600px">
  <AgGridReact {...gridProps} />
</Box>
```

## Default Filters

| Filter | Type | Use For |
|--------|------|---------|
| `defaultAgDateColumnFilter` | `agDateColumnFilter` | Date columns |
| `defaultAgNumberColumnFilter` | `agNumberColumnFilter` | Numeric columns |
| `defaultAgTextColumnFilter` | `agTextColumnFilter` | Text columns |
| `defaultSetColumnFilter` | `agSetColumnFilter` | Categorical columns |

```typescript
{ field: 'createdAt', ...defaultAgDateColumnFilter }
{ field: 'amount', ...defaultAgNumberColumnFilter }
{ field: 'name', ...defaultAgTextColumnFilter }
{ field: 'status', ...defaultSetColumnFilter }
```

## Intelligent Set Filter Persistence

Auto-merges persisted filter values with current dataset values. No configuration required — works automatically for all `agSetColumnFilter` columns.

## getRowDragEventYOffset

```typescript
import { getRowDragEventYOffset } from '@devonenergyenterprise/ag-grid-presets'

const onRowDragEnd = (event: RowDragEvent) => {
  const offset = getRowDragEventYOffset(event)
  if (offset < 0) insertRowAbove(event.overNode, event.node)
  else insertRowBelow(event.overNode, event.node)
}
```
