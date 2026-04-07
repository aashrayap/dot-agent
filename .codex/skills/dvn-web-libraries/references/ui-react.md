# ui-react

`npm install @devonenergyenterprise/ui-react`

**Peer deps:** `@chakra-ui/react` ^3.29.0, `react` ^18.0.0

## Tooltip

Chakra UI wrapper with Devon Energy defaults: 500ms delay, top placement, arrow, portal rendering.

```tsx
import { Tooltip } from '@devonenergyenterprise/ui-react'

// Basic
<Tooltip content="Save your changes">
  <Button>Save</Button>
</Tooltip>

// Without arrow
<Tooltip content="Delete" showArrow={false}>
  <IconButton aria-label="Delete" />
</Tooltip>

// Custom position
<Tooltip content="Info" positioning={{ placement: 'right' }}>
  <InfoIcon />
</Tooltip>

// Conditional
<Tooltip content="Won't show when disabled" disabled={!showTooltip}>
  <Button>Hover me</Button>
</Tooltip>

// Rich content
<Tooltip content={<Box><Text fontWeight="bold">Status</Text><Text fontSize="sm">All systems go</Text></Box>}>
  <Badge colorScheme="green">Active</Badge>
</Tooltip>

// Without portal
<Tooltip content="Local tooltip" portalled={false}>
  <Button>Hover me</Button>
</Tooltip>
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `content` | `ReactNode` | required | Tooltip content |
| `children` | `ReactNode` | required | Trigger element |
| `showArrow` | `boolean` | `true` | Show arrow |
| `disabled` | `boolean` | `false` | Disable tooltip |
| `portalled` | `boolean` | `true` | Render in portal |
| `positioning` | `PositioningOptions` | `{ placement: 'top' }` | Position config |
| `openDelay` | `number` | `500` | Open delay (ms) |
| `closeDelay` | `number` | - | Close delay (ms) |

Also accepts all `Tooltip.RootProps` from Chakra UI.
