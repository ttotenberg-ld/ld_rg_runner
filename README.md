# What is this?

It's a way to send metric events to a LaunchDarkly flag, to be measured in Release Guardian.

# How can I use it?

1. Rename `.env.example` to `.env`, and update the values to your LD environment
1. `pip install requirements.txt`
1. `python3 main.py`
1. Press `ctrl+c` to stop the script when desired

# What are the parameters in .env?

- `SDK_KEY` should point to your LD server-side SDK Key. This should be considered secret.
- `API_KEY` should have read permissions to flags
- `PROJECT_KEY` should point to the project where this flag exists
- `FLAG_KEY` is the flag you'll be evaluating and sending events to
- `NUMERIC_METRIC_1` out of the box is tracking `latency`. Change it if you want to track a different number
- `BINARY_METRIC_1` out of the box is tracking `error-rate`. Change this one if you want a different conversion metric
- `NUMERIC_METRIC_1_FALSE_RANGE` defines the range that `latency` will fall into when the flag is serving `false`
- `NUMERIC_METRIC_1_TRUE_RANGE` defines the range that `latency` will fall into when the flag is serving `true`
- `BINARY_METRIC_1_FALSE_CONVERTED` defines the percentage of time that `error-rate` will be triggered when the flag is serving `false`
- `BINARY_METRIC_1_TRUE_CONVERTED` defines the percentage of time that `error-rate` will be triggered when the flag is serving `true`

# What will it do if I don't change the metrics at all?

With the current setup, the flag serving `true` will over time show regressions both in `latency` and `error-rate`. Release Guardian will detect these regressions, and take the action you define during setup. In my testing, using the values in the example, `latency` will trigger first and cause Release Guardian to trigger a pause/rollback.

It will look something like this:
![RG](<media/release_guardian.png>)