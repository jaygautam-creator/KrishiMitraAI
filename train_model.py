# import pandas as pd
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# import joblib

# # 1. Load dataset
# df = pd.read_csv("Crop_recommendation.csv")

# # 2. Features (7 columns) and target (label)
# X = df.drop("label", axis=1)   # N, P, K, temperature, humidity, ph, rainfall
# y = df["label"]

# # 3. Train-test split
# X_train, X_test, y_train, y_test = train_test_split(
#     X, y, test_size=0.2, random_state=42
# )

# # 4. Train model
# model = RandomForestClassifier(n_estimators=100, random_state=42)
# model.fit(X_train, y_train)

# # 5. Save model
# joblib.dump(model, "crop_model.pkl")
# joblib.dump(model, "crop_model.joblib")  # optional

# print("✅ Model trained & saved with 7 features (N, P, K, temp, humidity, ph, rainfall)")

# # import pandas as pd
# # from sklearn.ensemble import RandomForestClassifier
# # from sklearn.model_selection import train_test_split
# # import joblib

# # # 1. Load the dataset
# # df = pd.read_csv("Crop_recommendation.csv")

# # # 2. Split features and label
# # X = df.drop("label", axis=1)
# # y = df["label"]

# # # 3. Split into training and test data
# # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # # 4. Train the RandomForestClassifier
# # model = RandomForestClassifier(n_estimators=100, random_state=42)
# # model.fit(X_train, y_train)

# # # 5. Save the trained model to a file
# # joblib.dump(model, "crop_model.pkl")

# # print("✅ Model trained and saved as crop_model.pkl")
# # import joblib

# # # after training your model
# # joblib.dump(model, "crop_model.joblib")
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# 1. Load dataset
df = pd.read_csv("Crop_recommendation.csv")

# 2. Encode labels
le = LabelEncoder()
df["label_encoded"] = le.fit_transform(df["label"])

# 3. Split features/labels
X = df.drop(["label", "label_encoded"], axis=1)
y = df["label_encoded"]

# 4. Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. Save both model and label encoder
joblib.dump({"model": model, "encoder": le}, "crop_model.pkl")

print("✅ Model and encoder trained and saved as crop_model.pkl")
