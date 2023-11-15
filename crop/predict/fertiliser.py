import pandas as pd
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from crop.predict.utils import fertilizer_dic


class FertiliserPred:
    def __init__(self):
        self.data = pd.read_csv(f"{settings.BASE_DIR}/crop/predict/data/fertilizer.csv")
        
    def recommend(self, crop, N, P, K):
        df = self.data

        nr = df[df['Crop'] == crop]['N'].iloc[0]
        pr = df[df['Crop'] == crop]['P'].iloc[0]
        kr = df[df['Crop'] == crop]['K'].iloc[0]

        n = nr - float(N)
        p = pr - float(P)
        k = kr - float(K)
        temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
        max_value = temp[max(temp.keys())]
        
        if max_value == "N":
            if n < 0:
                key = 'NHigh'
                fert_err = f"Nitrogen is high with a value of {N}"
            else:
                key = "Nlow"
                fert_err = f"Nitrogen is low with a value of {N}"
        elif max_value == "P":
            if p < 0:
                key = 'PHigh'
                fert_err = f"Phosposous is high with a value of {P}"
            else:
                key = "Plow"
                fert_err = f"Phosphporous is low with a value of {P}"
        else:
            if k < 0:
                key = 'KHigh'
                fert_err = f"Potassium is high with a value of {K}"
            else:
                key = "Klow"
                fert_err = f"Pottasium is low with a value of {K}"

        return fert_err, format_html("{}", mark_safe(str(fertilizer_dic[key]).replace('\n', '')))