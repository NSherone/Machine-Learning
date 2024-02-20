from flask import Flask, render_template, request
import pandas as pd
import pickle


with open("predictive_model.pickle", "rb") as f:
    model = pickle.load(f)

def predict_failure(*args):
    machine_type = args[5]
    if machine_type not in ['M', 'H', 'L']:
        return "Invalid machine type. Please provide 'M', 'H', or 'L'", None, None

    data = {
        'Air temperature [K]': [args[0]],
        'Process temperature [K]': [args[1]],
        'Rotational speed [rpm]': [args[2]],
        'Torque [Nm]': [args[3]],
        'Tool wear [min]': [args[4]],
        'Type_H': [1 if machine_type == 'H' else 0],
        'Type_M': [1 if machine_type == 'M' else 0]
    }

    df = pd.DataFrame(data)
    predictions = model.predict(df)

    failure_type_mapping = {
        10: 'Heat Dissipation Failure',
        1: 'No Failure',
        12: 'Overstrain Failure',
        13: 'Power Failure',
        14: 'Tool Wear Failure'
    }

    predicted_failure_type_encoded = int(predictions[0])
    predicted_failure_type_name = failure_type_mapping.get(predicted_failure_type_encoded, "Unknown Failure Type")

    if predicted_failure_type_name in ["Heat Dissipation Failure", "Overstrain Failure", "Power Failure", "Tool Wear Failure"]:
        predicted_target = 1
    elif predicted_failure_type_name == "No Failure":
        predicted_target = 0
    else:
        predicted_target = 1

    return predicted_failure_type_name, predicted_failure_type_encoded, predicted_target

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        air_temp = float(request.form['air_temp'])
        process_temp = float(request.form['process_temp'])
        rotational_speed = float(request.form['rotational_speed'])
        torque = float(request.form['torque'])
        tool_wear = float(request.form['tool_wear'])
        machine_type = request.form['machine_type']

        
        failure_type, _, predicted_target = predict_failure(air_temp, process_temp, rotational_speed, torque, tool_wear, machine_type)
       
        return render_template('result.html', failure_type=failure_type, predicted_target=predicted_target)

if __name__ == '__main__':
    app.run()
