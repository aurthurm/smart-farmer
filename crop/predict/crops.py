import numpy as np
import pandas as pd
from django.conf import settings

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier


class CropRecommender:
    data: None = None
    
    def __init__(self):
        self.data = pd.read_csv(f"{settings.BASE_DIR}/crop/predict/data/crop.csv")

    def _train(self):
        train_data = self.data

        le = LabelEncoder()
        train_data.crop = le.fit_transform(train_data.crop)

        X = train_data.drop('crop', axis=1)
        y = train_data['crop']

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3)

        model = RandomForestClassifier(n_estimators=150)

        model.fit(X_train, y_train)

        return model, le


    def recommend(self, N, P, K, T, H, ph, R):
        A = [N, P, K, T, H, ph, R]

        model, le = self._train()

        S = np.array(A)
        X = S.reshape(1, -1)

        pred = model.predict(X)

        crop_pred = le.inverse_transform(pred)
        
        print(crop_pred)
        return crop_pred[0]
