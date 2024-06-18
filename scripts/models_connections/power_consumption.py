import waise_model
import subprocess
import time

def get_gpu_power_usage():
    try:
        output = subprocess.check_output(['nvidia-smi', '--query-gpu=power.draw', '--format=csv,nounits,noheader'])
        power_usage = float(output.decode('utf-8').strip())
        return power_usage
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing nvidia-smi: {e}")
        return None

def measure_power_consumption(prompt):
    model = waise_model.WaiseModel()
    
    # Get the initial power usage
    initial_power = get_gpu_power_usage()
    if initial_power is None:
        return

    # Invoke the model
    start_time = time.time()
    response = model.invoke(prompt)
    end_time = time.time()

    # Get the power usage after model invocation
    final_power = get_gpu_power_usage()
    if final_power is None:
        return

    # Calculate the power consumption
    power_consumption = final_power - initial_power
    execution_time = end_time - start_time

    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print(f"Power Consumption: {power_consumption} W")
    print(f"Execution Time: {execution_time:.2f} seconds")

prompt = "What is the capital of France?"
print(measure_power_consumption(prompt))