import posthog from 'posthog-js';

posthog.init(config.POSTHOG_KEY, {
    api_host: config.POSTHOG_HOST,
    autocapture: false,
    capture_pageview: true,
    person_profiles: 'never', // do not link events with personal information (profiles)
});

if (config.POSTHOG_ENABLED) {
    posthog.opt_in_capturing(); // technically redundant (is default)
} else {
    posthog.opt_out_capturing();
}
    

export default posthog;
