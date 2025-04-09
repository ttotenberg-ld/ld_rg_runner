from dotenv import load_dotenv  # pip install python-dotenv
import ldclient
from ldclient.config import Config
from ldclient.context import Context
import json
import os
import random
import requests
import time
import sys
from utils.create_context import create_multi_context

'''
Get environment variables
'''
load_dotenv()

# Validate required environment variables
required_env_vars = ['SDK_KEY', 'API_KEY', 'PROJECT_KEY', 'RG_FLAG_KEY',
                     'NUMERIC_METRIC_1', 'BINARY_METRIC_1',
                     'NUMERIC_METRIC_1_FALSE_RANGE', 'NUMERIC_METRIC_1_TRUE_RANGE',
                     'BINARY_METRIC_1_FALSE_CONVERTED', 'BINARY_METRIC_1_TRUE_CONVERTED']

missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    print(
        f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

SDK_KEY = os.environ.get('SDK_KEY')
API_KEY = os.environ.get('API_KEY')
PROJECT_KEY = os.environ.get('PROJECT_KEY')
FLAG_KEY = os.environ.get('RG_FLAG_KEY')
NUMERIC_METRIC_1 = os.environ.get('NUMERIC_METRIC_1')
BINARY_METRIC_1 = os.environ.get('BINARY_METRIC_1')

# Safely parse JSON environment variables
try:
    NUMERIC_METRIC_1_FALSE_RANGE = json.loads(
        os.environ.get('NUMERIC_METRIC_1_FALSE_RANGE'))
    NUMERIC_METRIC_1_TRUE_RANGE = json.loads(
        os.environ.get('NUMERIC_METRIC_1_TRUE_RANGE'))
except json.JSONDecodeError as e:
    print(f"Error parsing JSON from environment variables: {str(e)}")
    sys.exit(1)

BINARY_METRIC_1_FALSE_CONVERTED = os.environ.get(
    'BINARY_METRIC_1_FALSE_CONVERTED')
BINARY_METRIC_1_TRUE_CONVERTED = os.environ.get(
    'BINARY_METRIC_1_TRUE_CONVERTED')


'''
Initialize the LaunchDarkly SDK
'''
try:
    ldclient.set_config(Config(SDK_KEY))
except Exception as e:
    print(f"Error initializing LaunchDarkly SDK: {str(e)}")
    sys.exit(1)

'''
It's just fun :)
'''


def show_banner():
    print()
    print("        ██       ")
    print("          ██     ")
    print("      ████████   ")
    print("         ███████ ")
    print("██ LAUNCHDARKLY █")
    print("         ███████ ")
    print("      ████████   ")
    print("          ██     ")
    print("        ██       ")
    print()


'''
Error true or false calculator. Returns True if the random number is less than or equal to the chance_number.
'''


def error_chance(chance_number):
    chance_calc = random.randint(1, 100)
    if chance_calc <= chance_number:
        return True
    else:
        return False


'''
Call the LaunchDarkly API to check if the guarded rollout is active. Then run 1000 evaluations if it is.
'''


def callLD():
    try:
        # Make API request with error handling
        url = f'https://app.launchdarkly.com/api/v2/flags/{PROJECT_KEY}/{FLAG_KEY}'
        try:
            response = requests.get(
                url, headers={'Authorization': API_KEY, 'Content-Type': 'application/json'})
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            response_data = response.json()
        except requests.RequestException as e:
            print(f"API request error: {str(e)}")
            time.sleep(5)  # Wait before retrying
            return
        except json.JSONDecodeError as e:
            print(f"Error parsing API response: {str(e)}")
            time.sleep(5)
            return

        # Safely access nested keys
        production_env = response_data.get(
            'environments', {}).get('production', {})
        fallthrough = production_env.get('fallthrough', {})
        rollout_active = fallthrough.get('rollout')

        rollout_type = None
        if rollout_active and isinstance(rollout_active, dict):
            experiment_allocation = rollout_active.get(
                'experimentAllocation', {})
            if experiment_allocation and isinstance(experiment_allocation, dict):
                rollout_type = experiment_allocation.get('type')

        if rollout_type == 'measuredRollout':

            for i in range(1000):
                try:
                    context = create_multi_context()
                    flag_variation = ldclient.get().variation(FLAG_KEY, context, False)
                    numeric_metric_true_flag_value = ldclient.get().variation("config-gr-latency", context, {"range": [52, 131]})
                    numeric_metric_true_value = random.randint(numeric_metric_true_flag_value["range"][0], numeric_metric_true_flag_value["range"][1])

                    if flag_variation:
                        print("Executing " + str(flag_variation))
                        try:
                            if error_chance(int(BINARY_METRIC_1_TRUE_CONVERTED)):
                                ldclient.get().track(BINARY_METRIC_1, context)
                                print("Tracking " + BINARY_METRIC_1)
                            else:
                                ldclient.get().track(NUMERIC_METRIC_1, context, metric_value=numeric_metric_true_value)
                                print(
                                    f"Tracking {NUMERIC_METRIC_1} with value {numeric_metric_true_value}")
                        except (ValueError, TypeError) as e:
                            print(
                                f"Error processing true variation metrics: {str(e)}")
                    else:
                        print("Executing " + str(flag_variation))
                        try:
                            if error_chance(int(BINARY_METRIC_1_FALSE_CONVERTED)):
                                ldclient.get().track(BINARY_METRIC_1, context)
                                print("Tracking " + BINARY_METRIC_1)
                            else:
                                numeric_metric_false_value = random.randint(
                                    int(NUMERIC_METRIC_1_FALSE_RANGE[0]), int(NUMERIC_METRIC_1_FALSE_RANGE[1]))
                                ldclient.get().track(NUMERIC_METRIC_1, context, metric_value=numeric_metric_false_value)
                                print(
                                    f"Tracking {NUMERIC_METRIC_1} with value {numeric_metric_false_value}")
                        except (ValueError, TypeError) as e:
                            print(
                                f"Error processing false variation metrics: {str(e)}")

                    ldclient.get().flush()
                    time.sleep(.05)
                except Exception as e:
                    print(f"Error during flag evaluation iteration: {str(e)}")
                    continue  # Continue to next iteration
        else:
            print(f"Guarded Rollout is not active. Trying again in 5 seconds...")
            time.sleep(5)
    except Exception as e:
        print(f"Unexpected error in callLD: {str(e)}")
        time.sleep(5)  # Wait before retrying


'''
Execute! Push Ctrl+C to stop the loop.
'''
show_banner()
try:
    while True:
        callLD()
except KeyboardInterrupt:
    print("\nShutting down gracefully...")
except Exception as e:
    print(f"Fatal error: {str(e)}")
finally:
    # Responsibly close the LD Client
    try:
        ldclient.get().flush()
        time.sleep(1)
        ldclient.get().close()
    except Exception as e:
        print(f"Error during shutdown: {str(e)}")
    print("Exited.")
