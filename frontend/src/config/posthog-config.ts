import posthog from 'posthog-js';

posthog.init(config.POSTHOG_KEY, {
    api_host: config.POSTHOG_HOST,
    autocapture: false,
    capture_pageview: true,
    person_profiles: 'never', // do not link events with personal information (profiles)
});

export default posthog;
