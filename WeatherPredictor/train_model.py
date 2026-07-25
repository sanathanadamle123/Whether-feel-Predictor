import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

def generate_dataset(num_samples=2000):
    np.random.seed(42)
    
    seasons = ['Summer', 'Winter', 'Rainy', 'Autumn', 'Spring']
    times_of_day = ['Morning', 'Afternoon', 'Evening', 'Night']
    
    data = []
    
    for _ in range(num_samples):
        season = np.random.choice(seasons)
        time_of_day = np.random.choice(times_of_day)
        
        # Temperature distribution based on season
        if season == 'Winter':
            temp = np.random.uniform(-20, 15)
        elif season == 'Summer':
            temp = np.random.uniform(25, 50)
        elif season == 'Rainy':
            temp = np.random.uniform(18, 32)
        elif season == 'Spring':
            temp = np.random.uniform(15, 28)
        else: # Autumn
            temp = np.random.uniform(10, 24)
            
        temp = round(temp, 1)
        
        # Humidity
        if season == 'Rainy':
            humidity = np.random.uniform(65, 100)
        elif season == 'Summer' and temp > 35:
            humidity = np.random.uniform(10, 50)
        else:
            humidity = np.random.uniform(30, 85)
        humidity = round(humidity, 1)
        
        # Wind Speed
        wind_speed = round(np.random.uniform(0, 120), 1)
        
        # Pressure
        pressure = round(np.random.uniform(850, 1100), 1)
        
        # UV Index
        if time_of_day in ['Night', 'Evening']:
            uv_index = round(np.random.uniform(0, 2), 1)
        elif season == 'Summer':
            uv_index = round(np.random.uniform(5, 15), 1)
        else:
            uv_index = round(np.random.uniform(1, 8), 1)
            
        # Rain Probability
        if humidity > 80 or season == 'Rainy':
            rain_prob = round(np.random.uniform(40, 100), 1)
        else:
            rain_prob = round(np.random.uniform(0, 40), 1)
            
        # Determine feel category
        if temp < -10:
            feel = "Very Freezing"
        elif temp < 0:
            feel = "Freezing"
        elif temp < 8:
            feel = "Very Cold"
        elif temp < 15:
            feel = "Cold"
        elif temp < 20:
            feel = "Cool"
        elif temp < 25:
            feel = "Pleasant"
        elif temp < 30:
            feel = "Comfortable"
        elif temp < 35:
            feel = "Warm"
        elif temp < 40:
            feel = "Hot"
        elif temp < 45:
            feel = "Very Hot"
        else:
            feel = "Extreme Heat"
            
        data.append({
            'temperature': temp,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'pressure': pressure,
            'uv_index': uv_index,
            'rain_prob': rain_prob,
            'season': season,
            'time_of_day': time_of_day,
            'feel_category': feel
        })
        
    df = pd.DataFrame(data)
    return df

def train_and_save_model():
    dataset_dir = os.path.join(os.path.dirname(__file__), 'dataset')
    model_dir = os.path.join(os.path.dirname(__file__), 'model')
    
    os.makedirs(dataset_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    
    csv_path = os.path.join(dataset_dir, 'weather_data.csv')
    model_path = os.path.join(model_dir, 'weather_model.pkl')
    
    print("Generating weather dataset...")
    df = generate_dataset()
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved to {csv_path}")
    
    X = df.drop(columns=['feel_category'])
    y = df['feel_category']
    
    categorical_features = ['season', 'time_of_day']
    numeric_features = ['temperature', 'humidity', 'wind_speed', 'pressure', 'uv_index', 'rain_prob']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    print("Training Random Forest model...")
    pipeline.fit(X, y)
    
    joblib.dump(pipeline, model_path)
    print(f"Model successfully saved to {model_path}")
    return pipeline

if __name__ == '__main__':
    train_and_save_model()
