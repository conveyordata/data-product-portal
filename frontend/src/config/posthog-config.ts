import posthog from 'posthog-js';

if (config.POSTHOG_ENABLED) {
    posthog.init(config.POSTHOG_KEY, {
        api_host: config.POSTHOG_HOST,
        autocapture: false,
        capture_pageview: false,
        person_profiles: 'identified_only',
    });
    posthog.opt_in_capturing(); // technically redundant (is default)
} else {
    posthog.opt_out_capturing();
}

export default posthog;
