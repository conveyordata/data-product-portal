import posthog from 'posthog-js';

posthog.init('phc_4VSDmArvfOF31URzwkvuCGpSmyTHQkmFs0Y8SFC6FRs', {
  api_host: 'https://eu.i.posthog.com',
  autocapture: true,
  capture_pageview: true,
  person_profiles: 'never', // do not link events with personal information (profiles)
})

export default posthog;