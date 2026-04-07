# core-utils

`npm install @devonenergyenterprise/core-utils`

**Peer deps:** `lodash`, `luxon`

## Collection Utilities

### buildHierarchy — Flat array to tree

```typescript
import { buildHierarchy } from '@devonenergyenterprise/core-utils'

const departments = [
  { id: 1, name: 'Engineering', parentId: null },
  { id: 2, name: 'Frontend', parentId: 1 },
  { id: 3, name: 'Backend', parentId: 1 },
  { id: 4, name: 'Sales', parentId: null },
]

const tree = buildHierarchy(departments, 'id', 'name', 'name', 'parentId', true)
// Result: nested tree with { id, title, data: [...children] }
```

**Signature:** `buildHierarchy(items, idProp, titleProp, subtitleProp, parentIdProp, sort?)`
Works with any iterable (Array, Set). Useful for tree views, org charts, nested menus.

### filterBySearch — Multi-field search

```typescript
import { filterBySearch } from '@devonenergyenterprise/core-utils'

const results = filterBySearch('john doe', users, [
  u => u.name,
  u => u.email,
  u => u.role,
])
// Terms match in any order, case-insensitive
// Empty search returns all items
```

**Signature:** `filterBySearch(search, items, extractors[])`
Extractors can derive/transform data: `p => p.tags.join(' ')`, `p => formatDate(p.createdAt)`

### sliceAround — Window around index

```typescript
import { sliceAround } from '@devonenergyenterprise/core-utils'

const items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
sliceAround(items, 5, 4)  // [3, 4, 5, 6, 7]
sliceAround(items, 3, 0)  // [1, 2, 3] — clamped to start
sliceAround(items, 3, 9)  // [8, 9, 10] — clamped to end
```

**Signature:** `sliceAround(collection, count, startIndex)`
Works with any iterable. Useful for pagination or context display.

## Date Utilities

**Constants:** `defaultDateFormat` = `'MM/dd/yyyy'`, `defaultDateTimeFormat` = `"MM/dd/yyyy 'at' h:mma"`

### formatDate

```typescript
import { formatDate } from '@devonenergyenterprise/core-utils'

formatDate(new Date())                              // "12/29/2025"
formatDate('2025-12-29T10:30:00Z')                  // "12/29/2025"
formatDate(new Date(), 'yyyy-MM-dd')                // "2025-12-29"
formatDate(new Date(), "MM/dd/yyyy 'at' h:mma")     // "12/29/2025 at 2:30PM"
formatDate(undefined)                                // ""
formatDate('bad-date', 'MM/dd/yyyy', 'N/A')          // "N/A"
```

**Signature:** `formatDate(date, formatStr?, fallback?)`

### Date checks

```typescript
import { isToday, isTomorrow, isYesterday } from '@devonenergyenterprise/core-utils'

isToday(new Date())       // true
isYesterday(yesterday)    // true
isTomorrow(tomorrow)      // true
```

### mergeDateTime

```typescript
import { mergeDateTime } from '@devonenergyenterprise/core-utils'

mergeDateTime(new Date('2025-12-29'), new Date('1970-01-01T14:30:00'))
// Date object for "2025-12-29T14:30:00"
mergeDateTime(null, timeOnly)    // null
mergeDateTime(dateOnly, null)    // dateOnly at 00:00:00
```

**Signature:** `mergeDateTime(date, time)` — accepts Date, ISO string, or number

### serializeDates / deserializeDates

```typescript
import { serializeDates, deserializeDates } from '@devonenergyenterprise/core-utils'

// Form → API: Date objects → ISO strings
const payload = serializeDates(formData, ['createdAt', 'updatedAt'])

// API → Form: ISO strings → Date objects
const formData = deserializeDates(apiResponse, ['createdAt', 'updatedAt'])

// Supports nested paths
deserializeDates(data, ['user.profile.birthDate'])
```

Both expect an object. Non-objects are returned unchanged.

### startOfDayComparator

```typescript
import { startOfDayComparator } from '@devonenergyenterprise/core-utils'

startOfDayComparator(filterDate, rowDate)  // -1 (before), 0 (same day), 1 (after)
// Useful for AG Grid custom date filters
```

### toDateTime

```typescript
import { toDateTime } from '@devonenergyenterprise/core-utils'

toDateTime(new Date())         // Luxon DateTime
toDateTime('2025-12-29')       // Luxon DateTime
toDateTime(null)               // DateTime.now()
toDateTime('2025-12-29')?.toFormat('MMMM d, yyyy')  // "December 29, 2025"
```

## String Utilities

### ellipsize

```typescript
import { ellipsize } from '@devonenergyenterprise/core-utils'

ellipsize('This is a very long string that needs to be shortened', 20)  // "This is a very l..."
ellipsize('Hello', 20)       // "Hello" — short strings unchanged
ellipsize(undefined)          // ""
```

**Signature:** `ellipsize(value, maxLength=50)` — minimum length enforced at 4

### pluralize

```typescript
import { pluralize } from '@devonenergyenterprise/core-utils'

pluralize(1, 'item')                    // "1 item"
pluralize(5, 'item')                    // "5 items"
pluralize(3, 'box', 'boxes')            // "3 boxes"
pluralize(items, 'result')              // "3 results" — works with arrays/Sets
pluralize(5, 'file', 'files', false)    // "files" — without count prefix
```

**Signature:** `pluralize(target, single, plural?, includeCount?)`

### removeHtmlTags

```typescript
import { removeHtmlTags } from '@devonenergyenterprise/core-utils'

removeHtmlTags('<p>Hello <strong>World</strong></p>')  // "Hello World"
removeHtmlTags(undefined)                               // ""
```

### stringToRegExp

```typescript
import { stringToRegExp } from '@devonenergyenterprise/core-utils'

const regex = stringToRegExp('quick fox')
'the quick brown fox'.match(regex)  // Matches — words in order with content between
// Case-insensitive by default, auto-escapes special regex chars
```

**Signature:** `stringToRegExp(search, caseSensitive?)`

## Types

```typescript
import type { HierarchyNode } from '@devonenergyenterprise/core-utils'
```
