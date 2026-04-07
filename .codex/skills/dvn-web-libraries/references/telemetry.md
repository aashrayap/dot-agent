# telemetry

`npm install @devonenergyenterprise/telemetry`

Application Insights tracking.

```typescript
import { aiTelemetryTracker, trackEvent, trackInfo, trackWarning, trackError } from '@devonenergyenterprise/telemetry'

// Initialize once at app start
aiTelemetryTracker.initialize(connectionString, reactPlugin, history)

// Track events
trackEvent('user.login', { method: 'sso' })
trackInfo('Data loaded')
trackWarning('Cache miss')
trackError('API failed', error)
```
