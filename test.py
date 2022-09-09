import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)

db = firestore.client()  # this connects to our Firestore database
collection = db.collection('trigger_lock')  # opens 'places' collection
doc = collection.document('Mm4BLLgEHxtgeZIhi6iu')  # specifies the 'rome' document

print(doc.get().to_dict()['IFTTT_TRIGGER_LOCK'])




gcloud projects add-iam-policy-binding ensure-dev-zone --member="s535976716507-compute@developer.gserviceaccount.com" --role="roles/datastore.user"

